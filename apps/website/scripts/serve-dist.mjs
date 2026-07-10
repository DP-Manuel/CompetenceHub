import { createServer } from "node:http";
import { createReadStream, existsSync, statSync } from "node:fs";
import { extname, join, normalize } from "node:path";

const root = normalize(join(process.cwd(), "dist"));
const configuredBase = process.env.BASE_PATH || "/";
const base = configuredBase === "/" ? "" : configuredBase.replace(/\/$/, "");
const port = Number(process.env.PORT || 4321);

const types = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
};

function resolvePath(urlPath) {
  let path = decodeURIComponent(urlPath.split("?")[0]);
  if (path === "/" && base) path = `${base}/`;
  if (path.startsWith(base)) path = path.slice(base.length) || "/";
  const candidate = normalize(join(root, path));
  if (!candidate.startsWith(root)) return null;
  if (existsSync(candidate) && statSync(candidate).isFile()) return candidate;
  const indexFile = join(candidate, "index.html");
  if (existsSync(indexFile)) return indexFile;
  return null;
}

createServer((req, res) => {
  const file = resolvePath(req.url || "/");
  if (!file) {
    res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    res.end("Not found");
    return;
  }

  res.writeHead(200, {
    "content-type": types[extname(file)] || "application/octet-stream",
  });
  createReadStream(file).pipe(res);
}).listen(port, "127.0.0.1", () => {
  console.log(`Static preview: http://127.0.0.1:${port}${base || "/"}`);
});
