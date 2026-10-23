"""Bounded, read-only management projections over the existing Registry schema."""

from dataclasses import asdict

from sqlalchemy import text

from competence_hub_api.portal.coach_registry import management_capabilities
from competence_hub_api.portal.postgres_coach_registry import rows


class CoachManagementQueries:
    def __init__(self, repository):
        self.repository = repository
        self.engine = repository.engine

    async def index(self, *, limit, offset, lifecycle=None, publication=None):
        async with self.engine.connect() as c:
            result = await rows(
                c,
                """
                SELECT c.id,COALESCE(r.display_name,c.display_name) AS display_name,c.lifecycle_status AS lifecycle,c.registry_lock_version AS version,
                    r.revision_number,r.status AS revision_status,
                    (SELECT count(*) FROM competence_hub.coach_profile_topics WHERE revision_id=r.id) AS topic_count,
                    (SELECT count(*) FROM competence_hub.coach_offerings WHERE revision_id=r.id AND active) AS offering_count,
                    COALESCE(p.state,'not_published') AS preview,
                    COALESCE(q.state,'not_published') AS production
                FROM competence_hub.coaches c
                LEFT JOIN LATERAL (SELECT id,display_name,revision_number,status FROM competence_hub.coach_profile_revisions
                    WHERE coach_id=c.id ORDER BY revision_number DESC LIMIT 1) r ON true
                LEFT JOIN competence_hub.coach_publications p ON p.coach_id=c.id AND p.environment='preview'
                LEFT JOIN competence_hub.coach_publications q ON q.coach_id=c.id AND q.environment='production'
                WHERE c.registry_request_id IS NOT NULL
                    AND (CAST(:lifecycle AS text) IS NULL OR c.lifecycle_status=:lifecycle)
                    AND (CAST(:publication AS text) IS NULL
                        OR (:publication='preview' AND p.state='published')
                        OR (:publication='production' AND q.state='published')
                        OR (:publication='unpublished' AND COALESCE(p.state,'')<>'published' AND COALESCE(q.state,'')<>'published'))
                ORDER BY lower(c.display_name),c.id LIMIT :limit OFFSET :offset
            """,
                limit=limit + 1,
                offset=offset,
                lifecycle=lifecycle,
                publication=publication,
            )
        return {
            "items": [dict(r) for r in result[:limit]],
            "has_more": len(result) > limit,
            "limit": limit,
            "offset": offset,
        }

    async def workspace(self, coach_id, *, revision_id=None, now):
        async with self.engine.begin() as c:
            await c.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            coach = await self.repository._load(
                c, coach_id, bounded=True, selected_id=revision_id
            )
            if coach is None or coach.request_id is None:
                return None
            selected = (
                coach.revision(revision_id)
                if revision_id
                else (coach.revisions[-1] if coach.revisions else None)
            )
            linked = (
                await rows(
                    c,
                    """
                SELECT c.public_profile_path,
                    CASE WHEN u.id IS NULL THEN 'none' WHEN u.active THEN 'active' ELSE 'disabled' END AS portal_account,
                    EXISTS(SELECT 1 FROM competence_hub.user_roles ur JOIN competence_hub.roles r ON r.id=ur.role_id
                        WHERE ur.user_id=c.portal_user_id AND r.code='coach' AND r.active) AS calendar_role
                FROM competence_hub.coaches c LEFT JOIN competence_hub.portal_users u ON u.id=c.portal_user_id WHERE c.id=:id
            """,
                    id=coach_id,
                )
            )[0]
            future = await self.repository._future(c, coach_id, now)
            return {
                "id": coach.id,
                "display_name": coach.display_name,
                "lifecycle": coach.lifecycle,
                "version": coach.version,
                "publication_floor": coach.publication_floor,
                "revision": (
                    {
                        "id": selected.id,
                        "number": selected.number,
                        "status": selected.status,
                        "created_at": selected.created_at,
                        "content": selected.content.model_dump(mode="json"),
                        "topics": [asdict(t) for t in selected.topics],
                        "approvals": [
                            {"kind": a.kind, "occurred_at": a.occurred_at}
                            for a in selected.approvals
                        ],
                    }
                    if selected
                    else None
                ),
                "publications": {
                    e: {
                        "state": p.state,
                        "revision_number": coach.revision(p.revision_id).number,
                        "occurred_at": p.occurred_at,
                    }
                    for e, p in coach.publications.items()
                },
                "capabilities": management_capabilities(
                    coach, selected, future_calendar=future
                ),
                "links": {**dict(linked), "future_calendar": future},
            }

    async def topics(self, *, limit, offset):
        async with self.engine.connect() as c:
            result = await rows(
                c,
                """
                SELECT t.id,t.name, array_remove(array_agg(a.category_code ORDER BY a.category_code),NULL) AS categories
                FROM competence_hub.topics t LEFT JOIN competence_hub.topic_category_assignments a ON a.topic_id=t.id
                WHERE t.active GROUP BY t.id,t.name ORDER BY lower(t.name),t.id LIMIT :limit OFFSET :offset
            """,
                limit=limit + 1,
                offset=offset,
            )
        return {
            "items": [dict(r) for r in result[:limit]],
            "has_more": len(result) > limit,
            "limit": limit,
            "offset": offset,
        }

    async def history(self, coach_id, *, limit, offset, revisions=False):
        async with self.engine.connect() as c:
            if revisions:
                result = await rows(
                    c,
                    """
                    SELECT id,revision_number AS number,status,created_at
                    FROM competence_hub.coach_profile_revisions WHERE coach_id=:id
                    ORDER BY revision_number DESC LIMIT :limit OFFSET :offset
                """,
                    id=coach_id,
                    limit=limit + 1,
                    offset=offset,
                )
            else:
                result = await rows(
                    c,
                    """
                    SELECT action,occurred_at FROM competence_hub.audit_events
                    WHERE entity_type='coach_registry' AND (entity_id=:id OR entity_id IN
                        (SELECT id FROM competence_hub.coach_profile_revisions WHERE coach_id=:id))
                    ORDER BY occurred_at DESC,id DESC LIMIT :limit OFFSET :offset
                """,
                    id=coach_id,
                    limit=limit + 1,
                    offset=offset,
                )
        return {
            "items": [dict(r) for r in result[:limit]],
            "has_more": len(result) > limit,
            "limit": limit,
            "offset": offset,
        }
