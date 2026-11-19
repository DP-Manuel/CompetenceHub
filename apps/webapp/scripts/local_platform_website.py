"""Build and mount the local-only Astro journey; not part of the VPS wheel."""
import base64
from functools import lru_cache
from hashlib import sha256
from html.parser import HTMLParser
import os
from pathlib import Path
import subprocess

from starlette.datastructures import MutableHeaders
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[3]
SITE = ROOT / "apps" / "website"
SYNTHETIC_PROFILE = "/coaches/v2-demo-coach/"
_CSP_KEY = "competence_hub.local_website_csp"


def build_website(destination: Path) -> None:
    if destination.exists():
        raise ValueError("Expected a fresh local website output directory")
    node = ROOT / "tools" / "node-v22.16.0-win-x64" / "node.exe"
    if not node.is_file():
        raise RuntimeError("Install the project's verified Windows Node runtime before starting V2")
    env = {name: os.environ[name] for name in ("SystemRoot", "TEMP", "TMP", "PATH", "APPDATA", "LOCALAPPDATA", "USERPROFILE")
           if name in os.environ}
    env.update(WEBSITE_ENV="production", ASTRO_TELEMETRY_DISABLED="1")
    result = subprocess.run(
        [str(node), "node_modules/astro/astro.js", "build", "--config",
         "astro.v2-local.config.mjs", "--outDir", str(destination)],
        cwd=SITE, env=env, timeout=150, check=False,
    )
    if result.returncode or not (destination / "index.html").is_file():
        raise RuntimeError("Local website build failed")


class _InlineElements(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.active = None
        self.blocks = {"script": [], "style": []}
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.blocks and not (tag == "script" and "src" in dict(attrs)):
            self.active = tag
            self.parts = []

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if self.active == tag:
            content = "".join(self.parts).encode("utf-8")
            digest = base64.b64encode(sha256(content).digest()).decode("ascii")
            self.blocks[tag].append(f"'sha256-{digest}'")
            self.active = None


@lru_cache(maxsize=100)
def _html_policy(path: Path) -> str:
    parser = _InlineElements()
    parser.feed(path.read_text(encoding="utf-8"))
    scripts = " ".join(dict.fromkeys(parser.blocks["script"]))
    styles = " ".join(dict.fromkeys(parser.blocks["style"]))
    return ("default-src 'none'; base-uri 'none'; connect-src 'self'; font-src 'self'; "
            "form-action 'self'; frame-ancestors 'none'; img-src 'self' data:; "
            f"script-src 'self' {scripts}; style-src 'self' {styles}")


class _WebsiteFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if isinstance(response, FileResponse):
            source = Path(response.path)
            if source.suffix == ".html":
                scope[_CSP_KEY] = _html_policy(source)
        return response


class _WebsitePolicy:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def response(message):
            if message["type"] == "http.response.start" and _CSP_KEY in scope:
                headers = MutableHeaders(scope=message)
                headers["Content-Security-Policy"] = scope[_CSP_KEY]
                headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
            await send(message)
        await self.app(scope, receive, response)


def attach_website(app, directory: Path) -> None:
    app.state.local_website_path = "/website/"
    app.mount("/website", _WebsiteFiles(directory=directory, html=True), name="local-v2-website")
    app.add_middleware(_WebsitePolicy)
