"""Local synthetic presentation adapter. Never imports runtime/DB configuration."""
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from scripts.browser_acceptance_app import (
    COACH_EMAIL, EMPTY_COACH_EMAIL, SYNTHETIC_IDENTITIES,
    InMemoryCalendarRepository, create_acceptance_app,
)
from competence_hub_api.main import PORTAL_UI_DIRECTORY
from competence_hub_api.portal.calendar import (
    CalendarAccessDeniedError, CalendarIdempotencyConflictError,
    CalendarService, CalendarTimeConflictError, CalendarTopicUnavailableError,
    CalendarTransitionConflictError,
)
from competence_hub_api.web.calendar import _protected_context

ASSETS = Path(__file__).with_name("cal1_demo")
BANNER = ('<nav class="demo-banner" aria-label="Lokale Kalender-Demo">'
          '<strong>DEMO · Nur synthetische Daten</strong> '
          '<a href="/demo/">Demo-Kalender</a> '
          '<a href="/demo/#zugang">Testzugänge</a> '
          '<a href="/demo/history">Statusverlauf</a></nav>')


class DemoCalendarRepository(InMemoryCalendarRepository):
    """Existing browser fixture, with contract-faithful public/revision semantics."""

    def __init__(self):
        self.history = []
        super().__init__()

    def _seed(self):
        super()._seed()
        other = SYNTHETIC_IDENTITIES[EMPTY_COACH_EMAIL][0]
        for key, detail in list(self._offers.items()):
            revision = replace(detail.current_revision, draft=replace(
                detail.current_revision.draft,
                title="DEMO: " + detail.current_revision.draft.title,
                public_location="Demo-Raum (kein echter Veranstaltungsort)",
            ))
            self._offers[key] = replace(detail, offer=replace(detail.offer,
                coach_display_name="Demo-Coach A"), current_revision=revision,
                published_revision=revision if revision.workflow_status == "published" else None)
        published = next(d for d in self._offers.values() if d.published_revision)
        key = uuid4()
        rev = replace(published.current_revision, id=uuid4(), offer_id=key,
            draft=replace(published.current_revision.draft, title="DEMO: Parallelworkshop",
                format_code="hybrid"), created_by_user_id=other)
        self._offers[key] = replace(published, offer=replace(published.offer,
            id=key, coach_id=self.COACHES[other], created_by_user_id=other,
            client_request_id=uuid4(), coach_display_name="Demo-Coach B"),
            current_revision=rev, published_revision=rev)
        for detail in self._offers.values():
            self._record(detail, "Ausgangszustand (synthetisch)")

    def _record(self, detail, action):
        self.history.append({"offer_id": detail.offer.id, "title": detail.current_revision.draft.title,
            "revision": detail.current_revision.revision_number,
            "status": detail.current_revision.workflow_status,
            "lifecycle": detail.offer.lifecycle_status, "action": action})

    def _store(self, detail, revision, now, **values):
        if detail.offer.lifecycle_status != "active":
            raise CalendarTransitionConflictError("withdrawn offer is immutable")
        result = super()._store(detail, revision, now, **values)
        self._record(result, "Status / Revision aktualisiert")
        return result

    async def create_offer(self, **values):
        if values["draft"].topic_id != self.TOPIC.id:
            raise CalendarTopicUnavailableError("topic unavailable")
        prior = self._request_ids.get((values["actor_user_id"], values["client_request_id"]))
        if prior and self._offers[prior].current_revision.draft != values["draft"]:
            raise CalendarIdempotencyConflictError("request reused with different content")
        result = await super().create_offer(**values)
        if not prior:
            name = "Demo-Coach A" if result.offer.coach_id == self.COACHES[SYNTHETIC_IDENTITIES[COACH_EMAIL][0]] else "Demo-Coach B"
            result = replace(result, offer=replace(result.offer, coach_display_name=name))
            self._offers[result.offer.id] = result
            self._record(result, "Entwurf erstellt")
        return result

    async def update_draft(self, **values):
        if values["draft"].topic_id != self.TOPIC.id:
            raise CalendarTopicUnavailableError("topic unavailable")
        return await super().update_draft(**values)

    def _no_overlap(self, detail):
        candidate = detail.current_revision.draft
        for other in self._offers.values():
            if other.offer.id == detail.offer.id or other.offer.coach_id != detail.offer.coach_id or other.offer.lifecycle_status != "active":
                continue
            revisions = [other.published_revision]
            if other.current_revision.workflow_status == "in_review":
                revisions.append(other.current_revision)
            for rev in revisions:
                if rev and candidate.starts_at < rev.draft.ends_at and rev.draft.starts_at < candidate.ends_at:
                    raise CalendarTimeConflictError("same coach overlaps")

    async def submit_offer(self, **values):
        detail = self._visible(values["actor_user_id"], values["allow_any_coach"], values["offer_id"])
        if detail:
            self._require_version(detail, values["expected_version"])
            self._no_overlap(detail)
        return await super().submit_offer(**values)

    async def review_offer(self, **values):
        detail = self._offers.get(values["offer_id"])
        if detail and values["outcome"] == "published":
            self._require_version(detail, values["expected_version"])
            self._no_overlap(detail)
        return await super().review_offer(**values)

    def _public(self, detail):
        # Published revision stays public while its replacement is a private draft.
        published = replace(detail, current_revision=detail.published_revision)
        result = super()._public(published)
        suffix = "a" if detail.offer.coach_id == self.COACHES[SYNTHETIC_IDENTITIES[COACH_EMAIL][0]] else "b"
        return replace(result, coach_profile_path=f"/coaches/demo-coach-{suffix}/")

    async def get_public_offer(self, **values):
        detail = self._offers.get(values["offer_id"])
        return self._public(detail) if detail and detail.offer.lifecycle_status == "active" and detail.published_revision else None

    async def list_public_offers(self, **values):
        rows = [self._public(d) for d in self._offers.values()
                if d.offer.lifecycle_status == "active" and d.published_revision]
        rows = [r for r in rows if values["from_at"] <= r.starts_at < values["to_at"]
                and (values["topic_id"] is None or r.topic_id == values["topic_id"])]
        rows.sort(key=lambda r: (r.starts_at, r.id))
        if values["after_starts_at"] is not None:
            rows = [r for r in rows if (r.starts_at, r.id) > (values["after_starts_at"], values["after_offer_id"])]
        return tuple(rows[:values["limit"]])


def create_demo_app(port=8446):
    app = create_acceptance_app(port)
    repository = DemoCalendarRepository()
    app.state.calendar_service = CalendarService(repository)
    app.state.demo_repository = repository

    async def portal():
        html = (PORTAL_UI_DIRECTORY / "index.html").read_text(encoding="utf8")
        html = html.replace("</head>", '<link rel="stylesheet" href="/demo-assets/styles.css"><script src="/demo-assets/portal.js" defer></script></head>')
        return HTMLResponse(html.replace("<body>", "<body>" + BANNER))

    # Override only this fixture's static entry, never the shipped Portal files.
    app.router.routes.insert(0, APIRoute("/portal/", portal, methods=["GET"]))
    app.router.routes.insert(0, APIRoute("/portal/index.html", portal, methods=["GET"]))

    @app.get("/demo/", response_class=HTMLResponse)
    @app.get("/demo/history", response_class=HTMLResponse)
    async def demo():
        return HTMLResponse((ASSETS / "index.html").read_text(encoding="utf8"))

    @app.get("/demo/api/history")
    async def history(request: Request):
        context = await _protected_context(request, require_csrf=False)
        if isinstance(context, Response):
            return context
        actor, service = context
        try:
            visible = {d.offer.id for d in repository._offers.values()
                       if await service.get_offer(actor=actor, offer_id=d.offer.id)}
        except CalendarAccessDeniedError:
            return JSONResponse({"items": []}, status_code=403)
        return JSONResponse({"items": [{**r, "offer_id": str(r["offer_id"])}
                                      for r in repository.history if r["offer_id"] in visible]})

    @app.get("/coaches/{slug}/", response_class=HTMLResponse)
    async def profile(slug: str):
        if slug not in {"demo-coach-a", "demo-coach-b"}:
            return Response(status_code=404)
        name = "Demo-Coach " + slug[-1].upper()
        return HTMLResponse('<!doctype html><html lang="de"><head><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="/demo-assets/styles.css"><title>' + name + '</title></head><body>' + BANNER + '<main><h1>' + name + '</h1><p>Fiktive Person. Keine echten Qualifikationen, keine persönliche Verfügbarkeit und keine Verbindung zu realen Coachprofilen.</p><a href="/demo/">Zum Demo-Kalender</a></main></body></html>')

    @app.get("/demo-assets/calendar-month.mjs", response_class=FileResponse)
    async def calendar_month_module():
        # Windows MIME registry can label .mjs as text/plain; modules reject it.
        return FileResponse(ASSETS / "calendar-month.mjs", media_type="text/javascript")

    app.mount("/demo-assets", StaticFiles(directory=ASSETS), name="demo-assets")
    return app
