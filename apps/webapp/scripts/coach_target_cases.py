"""Synthetic COACH-3C reality cases. No real person or workshop source content."""

from competence_hub_api.portal.coach_registry import ProfileContent
from competence_hub_api.portal.coach_target import (
    ObjectEvidenceInput,
    requirements,
    subjects,
)


def target_profile(name="Alpha", **changes):
    value = dict(
        target_version=1,
        display_name="Synthetic Coach " + name,
        short_intro="Synthetic public introduction",
        profile_path="/coaches/synthetic-" + name.lower() + "/",
        public_roles=[
            dict(key="trainer", code="trainer", display_label="Trainer", ordering=0)
        ],
        qualifications=[
            dict(
                key="q-public",
                canonical_title="Synthetic training",
                public_display_label="Synthetic training",
                public=True,
                issuer="Synthetic institute",
                verification_state="source_asserted",
                evidence_reference="private:certificate",
                internal_note="PRIVATE_PRICE_999",
                ordering=0,
            ),
            dict(
                key="q-internal",
                canonical_title="PRIVATE_QUALIFICATION",
                public=False,
                ordering=1,
            ),
        ],
        offering_families=[
            dict(
                key="family-one",
                title="Synthetic family",
                ordering=0,
                protected_source_reference="private:workshop",
                service_domains=["coaching", "training"],
                boundaries=[
                    dict(
                        key="no-therapy",
                        text="Coaching is not therapy or legal advice",
                        excluded_services=["psychotherapy", "legal_advice"],
                    )
                ],
            )
        ],
        offerings=[
            dict(
                key="day",
                family_key="family-one",
                title="Synthetic day workshop",
                type="workshop",
                ordering=0,
                duration=dict(clock_start="10:00", clock_end="16:00"),
                delivery_mode="live_unspecified",
                delivery_label="Live",
                service_domains=["training"],
                variants=[
                    dict(
                        key="follow-up",
                        kind="add_on",
                        title="Follow-up after four weeks",
                    )
                ],
            ),
            dict(
                key="program",
                family_key="family-one",
                title="Synthetic six-week program",
                type="coaching",
                ordering=1,
                duration=dict(weeks=6, sessions_per_week=1, session_minutes=60),
                program_modules=["Synthetic orientation", "Synthetic reflection"],
            ),
        ],
        presentation=dict(
            teaser="Synthetic teaser",
            languages=["Deutsch"],
            quote="Synthetic quotation",
        ),
    )
    value.update(changes)
    return ProfileContent.model_validate(value)


def three_family_profile():
    value = target_profile("Epsilon").model_dump(mode="json")
    value["offering_families"] += [
        dict(
            key="health",
            title="Synthetic workplace health",
            ordering=1,
            service_domains=["health_promotion", "training"],
            boundaries=[
                dict(
                    key="no-medicine",
                    text="No medical treatment or diagnostics",
                    excluded_services=["medical_treatment", "diagnostics"],
                )
            ],
            variants=[dict(key="walk", kind="add_on", title="Ergonomics walk-through")],
        ),
        dict(
            key="reflection",
            title="Synthetic team reflection",
            ordering=2,
            service_domains=["moderation", "coaching"],
            boundaries=[
                dict(
                    key="not-mediation",
                    text="Not mediation or supervision",
                    excluded_services=["mediation", "supervision"],
                )
            ],
        ),
    ]
    value["offerings"] += [
        dict(
            key="health-half",
            family_key="health",
            title="Synthetic half-day",
            type="workshop",
            ordering=2,
            duration=dict(minutes=240),
            variants=[
                dict(
                    key="full-day", kind="variant", title="Full-day option", ordering=0
                ),
                dict(
                    key="follow-up",
                    kind="add_on",
                    title="Four-to-six-week follow-up",
                    ordering=1,
                ),
            ],
        ),
        dict(
            key="reflection-day",
            family_key="reflection",
            title="Synthetic reflection day",
            type="workshop",
            ordering=3,
        ),
        dict(
            key="reflection-series",
            family_key="reflection",
            title="Synthetic reflection series",
            type="other",
            ordering=4,
        ),
    ]
    return ProfileContent.model_validate(value)


def approvals_for(revision, environment="preview", prefix="consent"):
    hashes = subjects(revision.content, revision.topics)
    return [
        ObjectEvidenceInput(
            key=f"{prefix}-{i}",
            subject_type=t,
            subject_key=k,
            subject_hash=hashes[t, k],
            kind=kind,
            environment=environment,
            status="approved",
            evidence_reference="synthetic:consent",
        )
        for i, (t, k, kind) in enumerate(sorted(requirements(revision.content)))
    ]
