# Current Hardened Exact-Source Characterization Receipts

```text
source_commit=3a63161d3e04d785b4b04feadd4a0712bf6314fc
source_tree=b0fe73d232e0467a615eb71687144366de59b4b6
implementation_manifest=sha256:b6c03faf50bfab4ce25edaeb39b7ae36d2525df32519f82a8108c164162bd9fc
manifest_file_count=56
manifest_total_bytes=716453
characterization_result=TA_P001_TO_TA_P005_PASS
production_ready=false
```

| case | artifact digest |
|---|---|
| `TA-P001` | `sha256:0cd8a2815ba54fda31dafb21de621b42b8bbff787b54d7a17fc1c8255b14088f` |
| `TA-P002` | `sha256:d5e4bdf1b04dac64a940345ff9bff88ad604804266117c5db74279376fd4dfa6` |
| `TA-P003` | `sha256:35835720f02011cff5e54b20aed644a5c0466df847dae86047b4db4eb4ac7580` |
| `TA-P004` | `sha256:d4f468a451b3ede07e765796f6fa4c50ce715ab6af21541953c380b690853ab0` |
| `TA-P005` | `sha256:048db60c950a24123b1f56c7ca04631d399ed65db7ff71e16516dc256ccf3499` |

All five results were generated sequentially from an exact remote clean clone. Every source binding
and integrity result is `PASS`; every authority-effect field is `false`; artifact targets were private
and non-overwriting. The raw report tool intentionally claims implementation-manifest binding only;
the repository commit binding was verified independently with local and remote Git refs.

These are synthetic characterization receipts, not canonical Evidence, SLOs, cross-platform results,
Human Approval, deployment authorization or Production Ready evidence.
