# Neuro3D: consolidated technical status - 2026-10-06

## Identifiable source
The integration combines local motor work at
ba87272570be38188cb0bee7ae8bbc7fcd08a3f6 with public Iris fixes at
3dc2809192dccff0d17903614101741798c4c7ee using a normal two-parent merge.
The source merge contains 1,753 tracked paths before provenance/documentation
additions. All expected source blobs were checked against both inputs. The
original working tree and its four edited coordination documents were preserved.
Unfinished local research is retained with its original status.
See [the consolidation receipt](validation/consolidation-2026-10-06.json).

## Evidence by execution route

| Route | Evidence retained | Current limit |
|---|---|---|
| CPU oracle and graph model | Deterministic model and contract tests | Reference calculation; no physical hardware |
| Iris lattice | 16 MZI, 8 modes; stored report 117/120 train and 29/30 hold-out; scene raycasts and Python complex accumulation | Analytical training; hybrid CPU inference; portable blend cold-verified on 2026-10-06; repeated rebuilds and scene isolation verified through background API calls |
| Native OpenGL GPU geometry | Bounded K3/K4 pilots and nearest V2 comparisons | Native ALU pilot; no trained whole Iris network or proof of RT-core use |
| Precision research | Rational references and CPU hi/lo checks | Latest precision protocol has zero verified native joins |
| RT pilot006 | Retained bounded geometric readbacks and audit | Coherent end-to-end propagation incomplete |
| Unreal | Plugin source and execution design | Real compilation/readback/parity open |
| GPU supervision | Windows owned-process containment tests | Complete admission/telemetry/native integration open |
| Physical photonic device | No measurement established by this consolidation | Simulation does not supply physical evidence |

The consolidation receipt identifies the original CPU checks. The subsequent
[portable Iris validation](IRIS_REBUILD_VALIDATION_2026-10-06.md) reran all 150
scene classifications in a fresh process. Other route evidence remains historical.

## Source documents

- [Iris implementation and report](../Blender/demo_lattice_iris/README.md)
- [Nearest GPU V2](EXP-005-NEAREST-GPU-V2-2026-09-30.md)
- [Retained RT audit](EXP-005-RT-PILOT006-RETAINED-AUDIT.md)
- [CPU source precision](EXP-005-PRECISION-ORIGINAL-SOURCE-DIRECTION-ENDPOINTS-HILO-CPU-001.md)
- [Owned-process containment](EXP-005-GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001.md)
- [Night summary](NIGHT-SUMMARY-2026-09-30.md)
- [Preserved research](../Blender/research/README.md)

## Known reproduction boundaries

1. CLOSED: the distributed Iris blend was regenerated and verified away from
   the repository on all 150 rows. See [the report](IRIS_PORTABLE_VALIDATION_2026-10-06.md).
2. CLOSED: repeated rebuilds, suffixed names, materials and live state pass
   seven regression cases, five compatibility contracts and the refreshed portable
   check. See [point 3](IRIS_REBUILD_VALIDATION_2026-10-06.md).
3. The old CPU workflow omits the Iris tests.
4. Historical receipts retain absolute workstation paths. Six old GPU containment
   pins refer to host files outside Git: five RT pilot records and the Blender
   4.5.14 shader compiler DLL. They remain external historical dependencies.
5. Raw-byte hashes depend on line endings. Attributes fix ordinary text to LF and
   preserve historical CRLF additions without conversion. Old receipts and
   thresholds were not rewritten.
6. Research scripts with import-time scene changes must not enter incidental
   test discovery. Their historical results are not certified by this merge.

## Sequential execution policy

Close each roadmap point against explicit criteria before advancing. Keep CPU,
GPU ALU, RT and physical evidence separate. Native tests require fresh bounded
resource admission; historical permission receipts are not current launch
authorization. Retain negative results and exact thresholds.
Physical validation, actual external reproduction and scientific consequence
remain open until real evidence exists.

## Technical references

- [Git merge semantics](https://git-scm.com/docs/git-merge)
- [Worktree isolation](https://git-scm.com/docs/git-worktree)
- [Checkout attributes](https://git-scm.com/docs/gitattributes)
