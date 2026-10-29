"""Additive schema-0009 persistence; no second aggregate or public DB endpoint."""

import json

from sqlalchemy import text

from competence_hub_api.portal.coach_target import ObjectEvidenceInput, subjects


async def available(connection):
    return await connection.scalar(
        text(
            "SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema='competence_hub' AND table_name='coach_profile_revisions' AND column_name='target_version')"
        )
    )


async def load(connection, revision_ids):
    result = {}
    for table in (
        "coach_public_roles",
        "coach_qualifications",
        "coach_offering_families",
        "coach_object_evidence",
    ):
        result[table] = (
            (
                await connection.execute(
                    text(
                        f"SELECT * FROM competence_hub.{table} WHERE revision_id=ANY(CAST(:ids AS uuid[]))"
                    ),
                    {"ids": revision_ids},
                )
            )
            .mappings()
            .all()
        )
    return result


def content_fields(row, children):
    if "target_version" not in row:
        return {}

    def subset(table):
        return sorted(
            (x for x in children[table] if x["revision_id"] == row["id"]),
            key=lambda x: x["ordering"],
        )

    roles = [
        {
            "key": r["item_key"],
            **{k: r[k] for k in ("ordering", "code", "display_label")},
        }
        for r in subset("coach_public_roles")
    ]
    qualifications = [
        {
            "key": q["item_key"],
            **{
                k: q[k]
                for k in (
                    "ordering",
                    "canonical_title",
                    "public_display_label",
                    "issuer",
                    "qualification_type",
                    "public",
                    "status",
                    "verification_state",
                    "evidence_reference",
                    "internal_note",
                )
            },
        }
        for q in subset("coach_qualifications")
    ]
    families = [
        {
            "key": f["item_key"],
            **{k: f[k] for k in ("ordering", "title", "description", "active")},
            **f["metadata"],
        }
        for f in subset("coach_offering_families")
    ]
    return {
        "target_version": row["target_version"],
        "presentation": row["presentation"],
        "boundaries": row["boundaries"],
        "public_roles": roles,
        "qualifications": qualifications,
        "offering_families": families,
    }


def offering_fields(row):
    if row.get("metadata") is None:
        return {}
    return {"key": row["item_key"], "family_key": row["family_key"], **row["metadata"]}


def evidence_fields(row):
    return ObjectEvidenceInput(
        key=row["evidence_key"],
        **{k: row[k] for k in ObjectEvidenceInput.model_fields if k != "key"},
    )


async def write_content(connection, coach_id, revision):
    c = revision.content
    hashes = {
        kind + ":" + key: value
        for (kind, key), value in subjects(c, revision.topics).items()
    }
    await connection.execute(
        text(
            "UPDATE competence_hub.coach_profile_revisions SET target_version=:version,presentation=CAST(:presentation AS jsonb),boundaries=CAST(:boundaries AS jsonb),subject_hashes=CAST(:hashes AS jsonb) WHERE id=:id"
        ),
        {
            "id": revision.id,
            "version": c.target_version,
            "presentation": (
                json.dumps(c.presentation.model_dump(mode="json"))
                if c.presentation
                else None
            ),
            "boundaries": json.dumps([b.model_dump(mode="json") for b in c.boundaries]),
            "hashes": json.dumps(hashes),
        },
    )
    for table in (
        "coach_public_roles",
        "coach_qualifications",
        "coach_offering_families",
    ):
        await connection.execute(
            text(f"DELETE FROM competence_hub.{table} WHERE revision_id=:id"),
            {"id": revision.id},
        )
    for r in c.public_roles:
        await connection.execute(
            text(
                "INSERT INTO competence_hub.coach_public_roles(revision_id,coach_id,item_key,ordering,code,display_label) VALUES (:revision,:coach,:key,:ordering,:code,:display_label)"
            ),
            {"revision": revision.id, "coach": coach_id, **r.model_dump()},
        )
    for q in c.qualifications:
        await connection.execute(
            text(
                "INSERT INTO competence_hub.coach_qualifications(revision_id,coach_id,item_key,ordering,canonical_title,public_display_label,issuer,qualification_type,public,status,verification_state,evidence_reference,internal_note) VALUES (:revision,:coach,:key,:ordering,:canonical_title,:public_display_label,:issuer,:qualification_type,:public,:status,:verification_state,:evidence_reference,:internal_note)"
            ),
            {"revision": revision.id, "coach": coach_id, **q.model_dump()},
        )
    for f in c.offering_families:
        await connection.execute(
            text(
                "INSERT INTO competence_hub.coach_offering_families(revision_id,coach_id,item_key,ordering,title,description,active,metadata) VALUES (:revision,:coach,:key,:ordering,:title,:description,:active,CAST(:metadata AS jsonb))"
            ),
            {
                "revision": revision.id,
                "coach": coach_id,
                **f.model_dump(
                    include={"key", "ordering", "title", "description", "active"}
                ),
                "metadata": json.dumps(
                    f.model_dump(
                        mode="json",
                        exclude={"key", "ordering", "title", "description", "active"},
                    )
                ),
            },
        )


async def write_offering(connection, revision_id, offering):
    if offering.key is None:
        return
    await connection.execute(
        text(
            "UPDATE competence_hub.coach_offerings SET item_key=:key,family_key=:family,metadata=CAST(:metadata AS jsonb) WHERE revision_id=:revision AND ordering=:ordering"
        ),
        {
            "revision": revision_id,
            "ordering": offering.ordering,
            "key": offering.key,
            "family": offering.family_key,
            "metadata": json.dumps(
                offering.model_dump(
                    mode="json",
                    exclude={
                        "title",
                        "type",
                        "description",
                        "active",
                        "ordering",
                        "key",
                        "family_key",
                    },
                )
            ),
        },
    )


async def write_evidence(connection, coach_id, revision, previous):
    existing = {e.id for e in previous.object_evidence} if previous else set()
    for e in revision.object_evidence:
        if e.id in existing:
            continue
        await connection.execute(
            text(
                "INSERT INTO competence_hub.coach_object_evidence(id,revision_id,coach_id,evidence_key,subject_type,subject_key,subject_hash,kind,environment,scope,status,evidence_reference,approved_by,approved_at,approved_on,internal_note,recorded_by,recorded_at) VALUES (:id,:revision,:coach,:key,:subject_type,:subject_key,:subject_hash,:kind,:environment,:scope,:status,:evidence_reference,:approved_by,:approved_at,:approved_on,:internal_note,:recorded_by,:recorded_at)"
            ),
            {
                "id": e.id,
                "revision": revision.id,
                "coach": coach_id,
                "recorded_by": e.recorded_by,
                "recorded_at": e.recorded_at,
                **e.value.model_dump(),
            },
        )
