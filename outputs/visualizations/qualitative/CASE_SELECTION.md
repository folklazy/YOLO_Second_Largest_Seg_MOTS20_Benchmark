# Qualitative case selection

Pool: the 12 frozen frames in manifests/visualization_frames.json, reviewed using existing
per-frame CSVs and actual comparisons. Diagnostic selection, not random or representative sampling.
The set includes an advantage, shared failure, counterexample and similar-output check.
No inference; source frame / GT / prediction / comparison SHA256 and per-frame counts are in CASE_EVIDENCE.json.
Counts were checked against existing CSVs. All panels show the same full frame at the same scale.

| Case | Sequence | Frame | Reason | Model behavior |
|---|---|---|---|---|
| 1 | MOTS20-05 | 000419 | additional valid small Person; retain shared FN | YOLO26l-Seg: TP/FP/FN 5/0/1; YOLO11l-Seg: TP/FP/FN 4/1/2; YOLOv9c-Seg: TP/FP/FN 4/0/2; YOLOv8l-Seg: TP/FP/FN 4/0/2 |
| 2 | MOTS20-09 | 000263 | shared misses / unmatched masks | YOLO26l-Seg: TP/FP/FN 9/2/4; YOLO11l-Seg: TP/FP/FN 9/2/4; YOLOv9c-Seg: TP/FP/FN 8/1/5; YOLOv8l-Seg: TP/FP/FN 8/2/5 |
| 3 | MOTS20-02 | 000001 | counterexample to aggregate ranking / detection trade-off | YOLO26l-Seg: TP/FP/FN 9/0/3; YOLO11l-Seg: TP/FP/FN 9/0/3; YOLOv9c-Seg: TP/FP/FN 8/0/4; YOLOv8l-Seg: TP/FP/FN 10/2/2 |
| 4 | MOTS20-09 | 000001 | similar valid detections / near-tie context | YOLO26l-Seg: TP/FP/FN 6/0/0; YOLO11l-Seg: TP/FP/FN 6/0/0; YOLOv9c-Seg: TP/FP/FN 6/0/0; YOLOv8l-Seg: TP/FP/FN 6/0/0 |

Only observed failure types are discussed. No inferred error frequency, scene severity or statistical significance.
