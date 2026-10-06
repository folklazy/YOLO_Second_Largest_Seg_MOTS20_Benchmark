# Second-largest (L/C) YOLO Segmentation Benchmark — MOTS20

## 1. Experiment Status

PASS WITH WARNINGS

- Models completed: 4/4
- Frames: 2,862 per model; Person GT instances: 26,894
- Run ID: `benchmark-20261001T0352Z`

## 2. Models Tested

| Family | Model | Parameters | GFLOPs | Checkpoint MB |
| --- | --- | --- | --- | --- |
| YOLO26 | YOLO26l-Seg | 31,515,528 | 151.304 | 63.70 |
| YOLO11 | YOLO11l-Seg | 27,678,368 | 133.176 | 56.10 |
| YOLOv9 | YOLOv9c-Seg | 27,897,120 | 149.340 | 56.47 |
| YOLOv8 | YOLOv8l-Seg | 45,997,728 | 211.060 | 92.42 |


## 3. Protocol Compatibility

| Item | Status |
|---|---|
| Dataset | PASS |
| Evaluator | PASS |
| Preprocessing | PASS |
| Input size | PASS |
| Precision | PASS |
| Thresholds | PASS |
| maxDet | PASS |
| Timing protocol | PASS |
| Environment | PASS |

Dataset compatibility: PASS

Preprocessing compatibility: PASS

Historical environment and frozen evidence verified; shared methodology: [Master Study](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study).

## 4. Overall Results

| Model | Mask mAP50-95 | AP50 | AP75 | Precision | Recall | F1 | TP-only IoU | TP-only Dice | Inference ms | Pipeline ms | FPS | Peak VRAM MiB | Params | GFLOPs | Checkpoint MB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YOLO26l-Seg | 0.586237 | 0.889890 | 0.643537 | 0.935702 | 0.834387 | 0.882145 | 0.825340 | 0.900714 | 36.266 | 76.403 | 13.089 | 777.52 | 31,515,528 | 151.304 | 63.70 |
| YOLO11l-Seg | 0.528228 | 0.867132 | 0.565728 | 0.931599 | 0.809772 | 0.866424 | 0.801233 | 0.885822 | 35.387 | 76.810 | 13.019 | 794.47 | 27,678,368 | 133.176 | 56.10 |
| YOLOv9c-Seg | 0.517646 | 0.855414 | 0.559180 | 0.918776 | 0.802930 | 0.856956 | 0.798288 | 0.883840 | 35.293 | 76.921 | 13.000 | 838.49 | 27,897,120 | 149.340 | 56.47 |
| YOLOv8l-Seg | 0.520145 | 0.859978 | 0.558149 | 0.909425 | 0.809400 | 0.856502 | 0.797581 | 0.883410 | 40.090 | 83.558 | 11.968 | 855.27 | 45,997,728 | 211.060 | 92.42 |


## 5. Tier Winners

| Category | Model | Value |
|---|---|---|
| Highest Mask mAP50-95 | YOLO26l-Seg | 0.586237 |
| Highest AP75 | YOLO26l-Seg | 0.643537 |
| Highest Recall | YOLO26l-Seg | 0.834387 |
| Fastest inference | YOLOv9c-Seg | 35.293 |
| Fastest pipeline | YOLO26l-Seg | 76.403 |
| Highest FPS | YOLO26l-Seg | 13.089 |
| Lowest VRAM | YOLO26l-Seg | 777.52 |


## 6. Key Findings

- Observed highest Mask mAP50-95: YOLO26l-Seg (0.586237).
- Lowest inference mean: YOLOv9c-Seg; lowest pipeline mean: YOLO26l-Seg. These are distinct measurements.
- Lowest allocated VRAM: YOLO26l-Seg (777.52 MiB).
- Interpretation: choose by measured accuracy, latency and memory constraints; no weighted score or architecture-causality claim.
- YOLOv9c-Seg and YOLO11l-Seg inference means, and the leading three pipeline means, are descriptively close; no significance test was performed.

## 7. Per-sequence Observations

- YOLO26l-Seg: strongest MOTS20-11 (0.640991); weakest MOTS20-02 (0.469068) by sequence Mask mAP50-95.
- YOLO11l-Seg: strongest MOTS20-05 (0.595551); weakest MOTS20-02 (0.406686) by sequence Mask mAP50-95.
- YOLOv9c-Seg: strongest MOTS20-05 (0.580796); weakest MOTS20-02 (0.396062) by sequence Mask mAP50-95.
- YOLOv8l-Seg: strongest MOTS20-05 (0.581724); weakest MOTS20-02 (0.402322) by sequence Mask mAP50-95.

## 8. Efficiency and Resource Observations

YOLOv9c-Seg has the lowest measured inference mean; YOLO26l-Seg has the lowest pipeline mean and highest mean-derived FPS. YOLO26l-Seg has the lowest allocator peak. Loaded parameters and NMS-path GFLOPs are in the table; fused runtime counts and separate loading times are in MODEL_COMPLEXITY.csv. Parameter counts do not imply proportional VRAM or latency.

## 9. Warnings and Anomalies

Historical PASS WITH WARNINGS retained: CPU NNPACK warnings during complexity inspection and pycocotools/NumPy deprecation warnings. Historical regression checks passed; no dependency changes were made. Pipeline excludes RLE preparation and disk I/O, so FPS is not end-to-end saved-mask throughput. No contaminated primary timing runs were recorded.

## 10. Limitations

ผลนี้เป็น Person instance segmentation รายเฟรมบน MOTS20 ไม่ใช่ MOTS tracking; TP-only IoU/Dice พิจารณาเฉพาะคู่ที่ match ได้ ภาพวิดีโอต่อเนื่องสัมพันธ์กันและไม่ได้ทดสอบ statistical significance ค่าใกล้กันควรอ่านว่า near-tied descriptively รุ่น E/X และ C/L ไม่ใช่ capacity เท่ากัน ผลยังไม่ยืนยัน blur, low-light, มุมกล้อง, ระดับ occlusion หรือความพร้อมใช้งาน CCTV; เป็น candidate for later CCTV robustness evaluation เท่านั้น

## 11. Reproducibility and Source Artifacts

- [TIER_RESULTS.csv](metrics/TIER_RESULTS.csv)
- [PER_SEQUENCE_RESULTS.csv](metrics/PER_SEQUENCE_RESULTS.csv)
- [TIMING_SUMMARY.csv](metrics/TIMING_SUMMARY.csv)
- [MODEL_COMPLEXITY.csv](metrics/MODEL_COMPLEXITY.csv)
- [PREFLIGHT_MAXDET.csv](metrics/PREFLIGHT_MAXDET.csv)

[Standardization provenance](manifests/STANDARDIZATION.json) · [Frozen protocol](EXPERIMENT_PROTOCOL.md) · [Historical reports](reports/archive/)

[Canonical plots](outputs/plots/INDEX.md).

## 12. Relation to Full Scaling Study

[Master Study](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study) — this is one tier only. The 17-model synthesis remains gated on all five tiers and explicit authorization.

## Qualitative Analysis

Same-frame visual evidence, observed failures and interpretation are in
[PRESENTATION_SUMMARY_TH.md](PRESENTATION_SUMMARY_TH.md).
Comparisons reuse saved RLE predictions and original MOTS20 frames; no inference rerun or benchmark value changes.
