# Preview Dependency Assessment

Date: 2026-10-21. Scope: the bounded static GitHub Pages preview, not a general security approval of the dependency tree.

## Finding And Disposition

Fresh npm audit against the unchanged lockfile reports 17 affected packages:
1 critical, 11 high, 4 moderate, 1 low; all installed application tooling is development/build tooling.
The warnings remain real maintenance debt. No dependency version or lockfile was changed in the content slice.
The proposed Astro remediation is a major upgrade and needs a separate compatibility/upgrade test block.

For this reviewed slice no reachable high/critical runtime exploit path was found.
This conclusion is conditional on the exact static build, trusted repository input and existing manual workflow described below; it is not a claim that every vulnerable package is fixed or safe for arbitrary use.
Proceeding with the approved static preview does not authorize an Astro server, remote image imports, untrusted build input or a new public development server.

## Reachability Evidence

| Warning group | Required path / source | Observed boundary |
| --- | --- | --- |
| Astro critical AVIF / Sharp | Processing attacker-controlled AVIF; see maintainer advisory below | No astro:assets, Image/Picture service imports or image optimizer in source. Existing local JPEG/PNG/WebP portraits are copied unchanged. No image endpoint is deployed. |
| Astro Host-header SSRF | SSR app.render runtime fetching an error page | Static output, no SSR adapter/output:server, no Astro runtime on Pages or IONOS |
| Astro slots/islands/transition XSS | Attacker-influenced hydrated slot/attribute/directive content | No client:* islands, server:* islands, astro:transitions, define:vars or user-controlled component props in the source. Browser hash filters accept fixed IDs and use textContent. |
| devalue buffer/DoS | Serialization/parsing of buffers or malicious input | No app import or browser use of devalue; no request-driven server rendering, hydrated props or raw-event deserialization |
| Vite / esbuild launch editor and dev server | Reachable development endpoints, in some cases Windows editor invocation | Local QA uses the small static server bound to 127.0.0.1; CI builds on Linux. No Vite/esbuild development server is published. |
| fast-uri / http-cache-semantics | Untrusted URI handling or shared HTTP response cache | No application fetch/proxy/cache path; builds consume repository-local data, not visitor URLs or cross-user responses |
| YAML / TOML / source maps / PostCSS / nanoid / SVGO | Malformed input, pathological size, untrusted map/source or executable SVG sanitization assumptions | Trusted checked-in source only; no upload/content-ingestion feature or reliance on SVGO as a sanitizer. Existing local SVG icons remain developer-controlled. |

Tracked source/config searches covered astro:assets, astro:transitions, client:*, server:*, define:vars, set:html, Sharp/devalue imports, AVIF and fetch calls; no relevant application path was found.
The workflow is workflow_dispatch-only, checks out main, installs the existing lockfile with npm ci, runs verification and uploads only dist-preview.
Build token permissions are contents:read; pages/id-token write are limited to the separate deploy job.
There is no pull-request build of untrusted source, private source download, SFTP or production credential use in this workflow.
Browser acceptance records no external requests, writes, resource failures or JavaScript errors for the tested preview paths.
The complete production build remains byte-identical across all 52 files.

## Primary Advisory References

- [Astro maintainer: AVIF image processing RCE](https://github.com/withastro/astro/security/advisories/GHSA-26w7-cxv4-gfx2): malicious AVIF processing is the prerequisite; patched Astro 7.2.8 / Sharp 0.35.4 are documented.
- [Astro maintainer: Host-header SSRF](https://github.com/withastro/astro/security/advisories/GHSA-2pvr-wf23-7pc7): SSR error-page fetch path, not static delivery.
- [Astro maintainer: slot XSS](https://github.com/withastro/astro/security/advisories/GHSA-8hv8-536x-4wqp): hydrated component/slot rendering path.
- [devalue maintainer: buffer serialization](https://github.com/sveltejs/devalue/security/advisories/GHSA-j22f-vq7h-c4qm): serialization may expose backing-buffer contents; no such application data flow is used here.
- Other advisories and affected ranges are identified by the fresh npm audit result; warning counts are packages, not unique CVEs.

## Remaining Work And Invalidating Changes

Create a separate toolchain-upgrade slice before accepting untrusted content/images, enabling SSR/islands or exposing a dev server.
It should evaluate supported Node/Astro versions, patch transitive dependencies deliberately, repeat both environment builds, link/privacy gates and browser acceptance, and document expected production-artifact deltas.
Any new remote import, upload, rendering adapter, hydrated component, serialization or request-driven build invalidates this bounded reachability conclusion and reopens the security gate.
No npm audit fix --force, broad package update, backend change or IONOS release was performed.
