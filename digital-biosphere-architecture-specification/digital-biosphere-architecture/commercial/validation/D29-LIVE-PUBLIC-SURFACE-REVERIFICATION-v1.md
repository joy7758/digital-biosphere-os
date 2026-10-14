# D29 Live Public Surface Reverification v1

Observed at `2026-08-08T23:27:26+08:00` from clean DBA
`main@add393f88a9c6983df6d1de02858aaf857e56ad2`.

## Result

```text
LIVE_CATALOG_HTTP_200=7/7
LIVE_CATALOG_SOURCE_BYTE_IDENTICAL=6/7
REQUIRED_COMMERCIAL_HUMAN_ROUTES_HTTP_200=10/10
PRODUCT_DETAIL_ROUTES_HTTP_200=4/4
COLLECTION_ROUTES_HTTP_200=0/4
LIVE_STATUS_JSON_SOURCE_MATCH=false
RESULT=FAIL_CLOSED_PARTIAL_DEPLOYMENT_MACHINE_STATUS_INCONSISTENT
```

The six current commercial catalogs are now reachable and byte-identical to
the current DBA source. The ten bounded commercial pages and four product
detail pages are also reachable. This supersedes only the earlier claim that
all commercial routes were still undeployed.

`/status.json` remains a conflicting live machine surface. Its bytes do not
match the current source and it still presents historical community identity
and stale operational facts. The direct URLs also do not prove open-web Agent
discovery. The four collection routes `/platform/`, `/products/`, `/solutions/`
and `/proof/` are not available as HTTP 200 entry pages.

The exact route and digest evidence is in
[`D29-LIVE-PUBLIC-SURFACE-REVERIFICATION-v1.json`](D29-LIVE-PUBLIC-SURFACE-REVERIFICATION-v1.json).

## Retained boundaries

```text
HISTORICAL_D29_LIVE_DISCOVERY_FAILURE_RETAINED=true
DIRECT_KNOWN_URL_REACHABILITY_NE_OPEN_WEB_DISCOVERY=true
HTTP_200_NE_COMMERCIAL_AVAILABILITY=true
PUBLIC_CATALOG_NE_OFFER_AUTHORIZATION=true
COMMERCIAL_PRIVATE_PILOT_READY=false
PAID_MONITOR_PILOT_AVAILABLE=false
DEPLOYMENT_EXECUTED_BY_THIS_REVERIFICATION=false
```

No server edit, deployment, restart, customer contact, offer activation or
Gate closure was performed.
