# Experiment 2: Second-largest available YOLO segmentation models on MOTS20

**Status: PASS WITH WARNINGS — 4 models × 2,862 accuracy frames; 3 clean timing rounds/model.**

- 📊 อ่านสรุป Benchmark แบบเข้าใจง่าย → [BENCHMARK_INSIGHTS_TH.md](BENCHMARK_INSIGHTS_TH.md)
- 📄 Technical Benchmark Report → [REPORT.md](REPORT.md)
- 🧪 Experimental Protocol → [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md)
- [Experiment 1: largest available variants](https://github.com/folklazy/YOLO_Large_Seg_MOTS20_Benchmark)

Compare official pretrained `yolo26l-seg.pt`, `yolo11l-seg.pt`,
`yolov8l-seg.pt` and `yolov9c-seg.pt` on all 2,862 MOTS20 train frames.
YOLOv9 c is its second-largest available segmentation variant in this family;
there is no official v9 L segmentation variant here. Capacities are unequal.
No training, fine-tuning or dataset adaptation.

Use the workspace `.venv/bin/python` directly. Do not reinstall from the
environment record: `requirements.txt` records the existing environment.
Dataset and checkpoints live only in workspace `datasets/` and `models/`.
Resolve workspace paths from the script location. Experiment 1 and
`Person_Segmentation_Pilot` are read-only reference records.

The dataset audit passed exact ordered frame list, image SHA256, dimensions,
GT hashes and sequence metadata checks against Experiment 1.
See [shared input evidence](manifests/shared_input_audit.json).
Preflight, timing and qualitative frame lists must match Experiment 1 exactly.
AP maxDet=200 must pass the new preflight convergence gate before full inference.

The evaluation and timing semantics are preserved from Experiment 1. Raw
lossless predictions stay local and are excluded from Git. Published summaries
will distinguish TP-only mask quality from detection success and pipeline FPS
from neural forward-pass speed.

## Reproducibility

All commands start at the shared workspace root. The run ID is
`benchmark-20261001T0352Z`. The full input archive under
`reports/<run>/frozen_inputs/` includes config, source, manifests and preserved
Experiment 1 summaries. SHA256 manifests record exact input provenance.

The execution stages are `src/audit_shared_inputs.py`, `src/validate.py`,
`src/benchmark.py preflight <run>`, `src/freeze_inputs.py <run>`,
`src/benchmark.py full <run>`, `src/repeat_clean_timing.py <run>`,
`src/cross_tier_report.py <run>` and `src/final_artifact_checks.py <run>`.
Final arithmetic and publication audits use `src/audit_results.py <run>` and
`src/publication_checks.py <run>`. The final human interpretation was reviewed
after report generation; original frozen runtime/evaluator sources are unchanged.
Use a fresh sibling checkout for a new benchmark, a fresh run ID, and set
`ap_max_dets: null` before its preflight; retain the fixed requirement that
200 must converge. Do not rerun preparation over this archived experiment or
overwrite its protocol, manifests, predictions or historical results.

For metric regeneration from the saved local RLE, with no model inference:

```bash
.venv/bin/python -B YOLO_Second_Largest_Seg_MOTS20_Benchmark/src/recompute_metrics.py \
  --run benchmark-20261001T0352Z --output-name independent-recomputation
```

The output directory must not exist. Raw predictions are intentionally not
included in Git; this command requires the preserved local `predictions/` tree
and the unchanged shared dataset. Accuracy evaluation calls the same frozen
evaluator used by the original run.

## Results

Accuracy: **YOLO26l-Seg**; inference speed: **YOLOv9c-Seg**; pipeline speed: **YOLO26l-Seg**; lowest peak allocated VRAM: **YOLO26l-Seg**.

Read the linked reports for measured cross-tier deltas and limitations.

YOLO26l is the strongest starting point for the measured accuracy/pipeline/allocated-memory
trade-off here. YOLOv9c's neural inference lead over YOLO11l is only 0.094 ms;
the three fastest pipelines differ by less than 0.52 ms. These are descriptive
measurements, not statistically established speed superiority. Pipeline FPS
excludes RLE preparation and disk I/O.

All 12 Experiment 2 timing runs were clean. The directory name `clean_repetition/`
is inherited from Experiment 1's validated runner; Experiment 2 did not discard
an initial timing pass. Frozen raw environment records and logs remain local;
see `manifests/environment_public.json` and `manifests/package_inventory.json`
for the publishable environment evidence. No packages were installed or upgraded.
