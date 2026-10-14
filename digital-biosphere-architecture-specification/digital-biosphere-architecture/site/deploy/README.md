# Baidu Cloud deployment boundary

Target host: `180.76.115.193` (`hongyan-4cj`)

Target layout:

```text
/srv/tmai/
├── releases/<source_revision>/
└── current -> releases/<source_revision>/
```

Historical website candidates were exported with:

```bash
RELEASE_MODE=candidate SOURCE_REVISION="$(git rev-parse HEAD)" npm run release:static
```

The authorized Developer Preview v0.1 formal artifact is exported with:

```bash
SOURCE_REVISION="$(git rev-parse HEAD)" npm run release:formal
```

`candidate` remains a historical fail-closed mode and rejects checked-in released
truth surfaces. `formal` mode is available only after the explicit Human Release
Decision in `ADR-022`. It requires
`RELEASE_DECISION_REF`, `RELEASED_BY_REF`, `PUBLIC_RELEASE_TAG`, and an HTTPS
`DBOS_WHEEL_URL`, and it fails unless the rendered bilingual pages plus all four
machine-readable truth surfaces already agree on the released state.

`release:formal` is now bound to `ADR-022`, `released_by_ref=zhangbin`,
`v0.1-developer-preview`, and the exact DBOS wheel URL. It remains an execution
guard; the prior candidate workflow did not itself create Release Authorization（发布授权）.

Deployment copies only the generated `out/` directory to a new immutable release
directory. The `current` symlink changes only after manifest verification and
`nginx -t` pass. Rollback repoints `current` to the previous release and reloads
Nginx.

The checked-in Nginx configuration references only the certificate and private
key that exist under `/etc/letsencrypt/live/redcrag.cn/`; it does not assume
Certbot helper files that are absent on the current Baidu Cloud host.

Location blocks use `expires` for cache behavior without redefining
`add_header`, so the server-level security headers remain inherited by HTML,
JSON, text, XML, and hashed assets.

Deployment truth:

```text
STATIC_EXPORT_NE_RELEASE=true
DEPLOYMENT_NE_DEVELOPER_PREVIEW_RELEASE=true
RELEASE_MANIFEST_REQUIRED=true
NGINX_VALIDATION_REQUIRED=true
HEALTH_CHECK_REQUIRED=true
ROLLBACK_VALIDATION_REQUIRED=true
```
