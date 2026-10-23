"""Relational COACH-1 adapter. All mutations serialize on the existing Coach row."""

from contextlib import asynccontextmanager
from copy import deepcopy
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from competence_hub_api.portal.coach_registry import (
    Approval,
    Asset,
    CoachAggregate,
    Offering,
    ProfileContent,
    ProfileRevision,
    Publication,
    RegistryConflict,
    TopicSnapshot,
)


async def rows(connection, statement, **parameters):
    return (await connection.execute(text(statement), parameters)).mappings().all()


class PostgresCoachRegistryRepository:
    def __init__(self, engine):
        self.engine = engine

    async def create(self, *, display_name, request_id, actor_id, now):
        async with self.engine.begin() as connection:
            inserted = await rows(
                connection,
                """
                INSERT INTO competence_hub.coaches(display_name,public_profile_status,registry_request_id)
                VALUES (:name,'not_published',:request_id)
                ON CONFLICT (registry_request_id) DO NOTHING RETURNING id
            """,
                name=display_name,
                request_id=request_id,
            )
            current = await rows(
                connection,
                "SELECT id,display_name FROM competence_hub.coaches WHERE registry_request_id=:request_id FOR UPDATE",
                request_id=request_id,
            )
            if current[0]["display_name"] != display_name:
                raise RegistryConflict("creation retry conflict")
            if inserted:
                await self._audit(
                    connection, "coach_registry.create", actor_id, now, current[0]["id"]
                )
            return await self._load(connection, current[0]["id"])

    async def get(self, coach_id):
        async with self.engine.connect() as connection:
            async with connection.begin():
                await connection.execute(
                    text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                )
                return await self._load(connection, coach_id)

    async def list_coaches(self, *, limit, offset):
        if not 1 <= limit <= 100 or not 0 <= offset <= 10000:
            raise ValueError("invalid pagination")
        async with self.engine.connect() as connection:
            result = await rows(
                connection,
                "SELECT * FROM competence_hub.coaches ORDER BY lower(display_name),id LIMIT :limit OFFSET :offset",
                limit=limit,
                offset=offset,
            )
            return tuple(self._coach(row) for row in result)

    @asynccontextmanager
    async def edit(self, coach_id, expected_version):
        try:
            async with self.engine.begin() as connection:
                locked = await rows(
                    connection,
                    "SELECT id FROM competence_hub.coaches WHERE id=:id FOR UPDATE",
                    id=coach_id,
                )
                if not locked:
                    raise LookupError("Coach not found")
                coach = await self._load(connection, coach_id)
                if coach.version != expected_version:
                    raise RegistryConflict("stale Coach version")
                before = deepcopy(coach)
                yield coach
                # Calendar create also holds this row lock, preventing a racing offer.
                if coach.lifecycle != before.lifecycle and coach.lifecycle != "active":
                    if await self._future(connection, coach.id, coach.events[-1][2]):
                        raise RegistryConflict(
                            "withdraw current/future Calendar offers first"
                        )
                await self._save(connection, before, coach)
        except IntegrityError as error:
            raise RegistryConflict("Registry constraint conflict") from error

    async def topics(self, topic_ids):
        if not topic_ids:
            return ()
        async with self.engine.connect() as connection:
            result = await rows(
                connection,
                """
                SELECT t.id,t.name,array_remove(array_agg(a.category_code ORDER BY a.category_code),NULL) AS categories
                FROM competence_hub.topics t LEFT JOIN competence_hub.topic_category_assignments a ON a.topic_id=t.id
                WHERE t.active AND t.id=ANY(CAST(:ids AS uuid[])) GROUP BY t.id,t.name
            """,
                ids=list(topic_ids),
            )
        by_id = {
            r["id"]: TopicSnapshot(r["id"], r["name"], tuple(r["categories"]))
            for r in result
        }
        if set(topic_ids) != set(by_id):
            raise RegistryConflict("unknown or inactive topic")
        return tuple(by_id[id] for id in topic_ids)

    async def has_future_calendar(self, coach_id, now):
        async with self.engine.connect() as connection:
            return await self._future(connection, coach_id, now)

    @staticmethod
    async def _future(connection, coach_id, now):
        return await connection.scalar(
            text("""
            SELECT EXISTS(SELECT 1 FROM competence_hub.calendar_offers o
            JOIN competence_hub.calendar_offer_revisions r ON r.offer_id=o.id
            WHERE o.coach_id=:id AND o.lifecycle_status='active' AND r.ends_at>=:now)
        """),
            {"id": coach_id, "now": now},
        )

    @staticmethod
    def _coach(row):
        return CoachAggregate(
            row["id"],
            row["display_name"],
            row["registry_request_id"],
            row["lifecycle_status"],
            row["registry_lock_version"],
            row["publication_floor"],
        )

    async def _load(self, connection, coach_id, *, bounded=False, selected_id=None):
        found = await rows(
            connection, "SELECT * FROM competence_hub.coaches WHERE id=:id", id=coach_id
        )
        if not found:
            return None
        coach = self._coach(found[0])
        selection = ""
        if bounded:
            # Keep an older activation-eligible revision even when newer unapproved
            # revisions exist. At most six revisions, independent of history length.
            selection = """ AND (id IN (SELECT id FROM competence_hub.coach_profile_revisions
                WHERE coach_id=:id ORDER BY revision_number DESC LIMIT 2)
                OR id IN (SELECT r.id FROM competence_hub.coach_profile_revisions r
                    WHERE r.coach_id=:id AND r.status='submitted'
                    AND r.revision_number>(SELECT publication_floor FROM competence_hub.coaches WHERE id=:id)
                    AND EXISTS(SELECT 1 FROM competence_hub.coach_profile_approvals a WHERE a.revision_id=r.id AND a.kind='content_review')
                    AND EXISTS(SELECT 1 FROM competence_hub.coach_profile_approvals a WHERE a.revision_id=r.id AND a.kind='person_consent')
                    ORDER BY r.revision_number DESC LIMIT 1)
                OR id IN (SELECT revision_id FROM competence_hub.coach_publications WHERE coach_id=:id)
                OR id=:selected_id)"""
        revisions = await rows(
            connection,
            "SELECT * FROM competence_hub.coach_profile_revisions WHERE coach_id=:id"
            + selection
            + " ORDER BY revision_number",
            id=coach_id,
            **({"selected_id": selected_id} if bounded else {}),
        )
        ids = [r["id"] for r in revisions]
        children = {}
        for table in (
            "coach_profile_labels",
            "coach_profile_topics",
            "coach_profile_topic_categories",
            "coach_offerings",
            "coach_assets",
            "coach_profile_approvals",
        ):
            # Table names are a fixed internal allowlist, never request input.
            children[table] = await rows(
                connection,
                f"SELECT * FROM competence_hub.{table} WHERE revision_id=ANY(CAST(:ids AS uuid[]))",
                ids=ids,
            )
        for row in revisions:

            def subset(table):
                return [r for r in children[table] if r["revision_id"] == row["id"]]

            labels = sorted(subset("coach_profile_labels"), key=lambda r: r["ordering"])
            topics = tuple(
                TopicSnapshot(
                    t["topic_id"],
                    t["snapshot_name"],
                    tuple(
                        sorted(
                            c["category_code"]
                            for c in subset("coach_profile_topic_categories")
                            if c["topic_id"] == t["topic_id"]
                        )
                    ),
                )
                for t in sorted(
                    subset("coach_profile_topics"), key=lambda t: str(t["topic_id"])
                )
            )
            content = ProfileContent(
                **{
                    k: row[k]
                    for k in (
                        "display_name",
                        "academic_suffix",
                        "short_intro",
                        "description",
                        "professional_background",
                        "profile_path",
                    )
                },
                target_groups=tuple(
                    r["label"] for r in labels if r["kind"] == "target_group"
                ),
                competencies=tuple(
                    r["label"] for r in labels if r["kind"] == "competency"
                ),
                topic_ids=tuple(t.id for t in topics),
                offerings=tuple(
                    Offering(
                        **{
                            k: o[k]
                            for k in (
                                "title",
                                "type",
                                "description",
                                "active",
                                "ordering",
                            )
                        }
                    )
                    for o in sorted(
                        subset("coach_offerings"), key=lambda o: o["ordering"]
                    )
                ),
                assets=tuple(
                    Asset(
                        reference=a["reference"],
                        sha256=a["sha256"],
                        alt_text=a["alt_text"],
                        active=a["active"],
                        scopes=tuple(
                            e for e in ("preview", "production") if a[e + "_allowed"]
                        ),
                    )
                    for a in subset("coach_assets")
                ),
            )
            revision = ProfileRevision(
                row["id"],
                row["revision_number"],
                content,
                row["created_by"],
                row["created_at"],
                row["status"],
                topics,
            )
            revision.approvals = [
                Approval(a["kind"], a["actor_id"], a["occurred_at"], a["evidence_ref"])
                for a in subset("coach_profile_approvals")
            ]
            coach.revisions.append(revision)
        publications = await rows(
            connection,
            "SELECT * FROM competence_hub.coach_publications WHERE coach_id=:id",
            id=coach_id,
        )
        coach.publications = {
            p["environment"]: Publication(
                p["revision_id"], p["state"], p["actor_id"], p["occurred_at"]
            )
            for p in publications
        }
        return coach

    async def _save(self, connection, before, coach):
        for revision in coach.revisions:
            previous = next((r for r in before.revisions if r.id == revision.id), None)
            if previous is None:
                await connection.execute(
                    text("""
                    INSERT INTO competence_hub.coach_profile_revisions(id,coach_id,revision_number,status,display_name,academic_suffix,short_intro,description,professional_background,profile_path,created_by,created_at)
                    VALUES (:id,:coach_id,:number,'draft',:display_name,:academic_suffix,:short_intro,:description,:professional_background,:profile_path,:actor,:now)
                """),
                    {
                        "id": revision.id,
                        "coach_id": coach.id,
                        "number": revision.number,
                        "actor": revision.created_by,
                        "now": revision.created_at,
                        **revision.content.model_dump(
                            exclude={
                                "target_groups",
                                "competencies",
                                "topic_ids",
                                "offerings",
                                "assets",
                            }
                        ),
                    },
                )
            if previous is None or (
                previous.status == "draft"
                and (
                    previous.content != revision.content
                    or previous.topics != revision.topics
                )
            ):
                await self._write_content(connection, coach.id, revision)
            if previous is not None and previous.content != revision.content:
                await connection.execute(
                    text("""
                    UPDATE competence_hub.coach_profile_revisions SET display_name=:display_name,academic_suffix=:academic_suffix,
                    short_intro=:short_intro,description=:description,professional_background=:professional_background,profile_path=:profile_path WHERE id=:id
                """),
                    {
                        "id": revision.id,
                        **revision.content.model_dump(
                            exclude={
                                "target_groups",
                                "competencies",
                                "topic_ids",
                                "offerings",
                                "assets",
                            }
                        ),
                    },
                )
            if revision.status in {"submitted", "abandoned"} and (
                previous is None or previous.status == "draft"
            ):
                await connection.execute(
                    text(
                        "UPDATE competence_hub.coach_profile_revisions SET status=:status WHERE id=:id"
                    ),
                    {"id": revision.id, "status": revision.status},
                )
            existing = {a.kind for a in previous.approvals} if previous else set()
            for approval in revision.approvals:
                if approval.kind not in existing:
                    await connection.execute(
                        text(
                            "INSERT INTO competence_hub.coach_profile_approvals(revision_id,kind,actor_id,occurred_at,evidence_ref) VALUES (:id,:kind,:actor,:now,:ref)"
                        ),
                        {
                            "id": revision.id,
                            "kind": approval.kind,
                            "actor": approval.actor_id,
                            "now": approval.occurred_at,
                            "ref": approval.evidence_ref,
                        },
                    )
        await connection.execute(
            text(
                "UPDATE competence_hub.coaches SET lifecycle_status=:state,registry_lock_version=:version,publication_floor=:floor WHERE id=:id"
            ),
            {
                "id": coach.id,
                "state": coach.lifecycle,
                "version": coach.version,
                "floor": coach.publication_floor,
            },
        )
        for environment, publication in coach.publications.items():
            if before.publications.get(environment) == publication:
                continue
            await connection.execute(
                text("""
                INSERT INTO competence_hub.coach_publications(coach_id,environment,revision_id,state,profile_path,actor_id,occurred_at)
                VALUES (:id,:env,:revision,:state,:path,:actor,:now)
                ON CONFLICT (coach_id,environment) DO UPDATE SET revision_id=EXCLUDED.revision_id,state=EXCLUDED.state,
                profile_path=EXCLUDED.profile_path,actor_id=EXCLUDED.actor_id,occurred_at=EXCLUDED.occurred_at
            """),
                {
                    "id": coach.id,
                    "env": environment,
                    "revision": publication.revision_id,
                    "state": publication.state,
                    "path": coach.revision(
                        publication.revision_id
                    ).content.profile_path,
                    "actor": publication.actor_id,
                    "now": publication.occurred_at,
                },
            )
        for action, actor, now, entity in coach.events:
            await self._audit(connection, action, actor, now, entity)
        coach.events.clear()

    @staticmethod
    async def _audit(connection, action, actor, now, entity):
        await connection.execute(
            text(
                "INSERT INTO competence_hub.audit_events(actor_user_id,occurred_at,action,entity_type,entity_id,outcome) VALUES (:actor,:now,:action,'coach_registry',:entity,'success')"
            ),
            {"actor": actor, "now": now, "action": action, "entity": entity},
        )

    @staticmethod
    async def _write_content(connection, coach_id, revision):
        for table in (
            "coach_profile_topic_categories",
            "coach_profile_topics",
            "coach_profile_labels",
            "coach_offerings",
            "coach_assets",
        ):
            await connection.execute(
                text(f"DELETE FROM competence_hub.{table} WHERE revision_id=:id"),
                {"id": revision.id},
            )
        for kind, labels in (
            ("target_group", revision.content.target_groups),
            ("competency", revision.content.competencies),
        ):
            for position, label in enumerate(labels):
                await connection.execute(
                    text(
                        "INSERT INTO competence_hub.coach_profile_labels VALUES (:id,:kind,:position,:label)"
                    ),
                    {
                        "id": revision.id,
                        "kind": kind,
                        "position": position,
                        "label": label,
                    },
                )
        for topic in revision.topics:
            await connection.execute(
                text(
                    "INSERT INTO competence_hub.coach_profile_topics VALUES (:id,:topic,:name)"
                ),
                {"id": revision.id, "topic": topic.id, "name": topic.name},
            )
            for category in topic.categories:
                await connection.execute(
                    text(
                        "INSERT INTO competence_hub.coach_profile_topic_categories VALUES (:id,:topic,:category)"
                    ),
                    {"id": revision.id, "topic": topic.id, "category": category},
                )
        for offering in revision.content.offerings:
            await connection.execute(
                text(
                    "INSERT INTO competence_hub.coach_offerings(revision_id,coach_id,ordering,title,type,description,active) VALUES (:id,:coach_id,:ordering,:title,:type,:description,:active)"
                ),
                {"id": revision.id, "coach_id": coach_id, **offering.model_dump()},
            )
        for asset in revision.content.assets:
            await connection.execute(
                text(
                    "INSERT INTO competence_hub.coach_assets VALUES (:id,:type,:reference,:sha256,:alt_text,:preview,:production,:active)"
                ),
                {
                    "id": revision.id,
                    "preview": "preview" in asset.scopes,
                    "production": "production" in asset.scopes,
                    **asset.model_dump(exclude={"scopes"}),
                },
            )
