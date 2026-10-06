# Experiment 2: Second-largest available variant comparison on MOTS20

Status: frozen design before preflight. The sole predeclared selection is common
AP maxDet from the saved 100-frame preflight. Its decision will be appended here
before any full accuracy run. No training, adaptation, threshold optimization or
other segmentation family is used. This is not a parameter-matched comparison.

## Inputs and order

Official Ultralytics `yolo26l-seg.pt`, `yolo11l-seg.pt`, `yolov8l-seg.pt`,
`yolov9c-seg.pt` in workspace `models/`. YOLOv9 c is its second-largest available supported
segmentation variant; there is no official v9 L segmentation checkpoint here. L/c do not imply equal capacity. Record local unfused
parameter counts, NMS-path GFLOPs when available, bytes and SHA256; also record
runtime fused parameters separately. Official sources:
[YOLO26](https://docs.ultralytics.com/models/yolo26/),
[YOLO11](https://docs.ultralytics.com/models/yolo11/),
[YOLOv8](https://docs.ultralytics.com/models/yolov8/),
[YOLOv9](https://docs.ultralytics.com/models/yolov9/).

Only `datasets/MOTS/MOTS/train`, sequences 02, 05, 09, 11 in that order, then
ascending frame number: 2,862 frames. GT is each sequence's bundled `gt/gt.txt`.
Validate all images and GT/ignore RLE; save individual image SHA256, GT hashes,
metadata hashes and source dimensions. Recheck hashes at completion. Inputs
and pilot remain unchanged. Save environment/package freeze and GPU state.

Preflight: 25 evenly spaced frames per sequence including endpoints, integer
rounding of linspace(1, sequence_length, 25). Save exact list before results.
Timing uses that same 100-frame list. Predetermined visualization uses 3 equally
spaced frames per sequence (12 total), frozen before results. Samples overlap
accuracy population intentionally; this is pretrained inference, not fitting.

## Common inference

One model at a time, CUDA:0 respecting existing visibility, batch 1, FP32,
imgsz 640, no augmentation. Explicit `nms=True` selects YOLO26 one-to-many before
fusion; assert backend end2end=False for all models. Exact COCO Person index 0
and name `person` required. Confidence >0.001 as implemented by Ultralytics NMS,
NMS box IoU 0.70, agnostic_nms=False, max_det=1000. This cap is independent of AP
maxDet. Log post-NMS candidates before native empty-mask filtering and saved
candidates before evaluator capping. Stop if 1000 is reached or NMS truncation
warnings occur. No per-model candidate-policy changes.

Preserve pilot preprocessing: OpenCV BGR images, aspect-preserving linear resize,
centered square letterbox, padding value 114, rect=False / auto=False, scaleup=True,
no stretch; channel conversion to RGB BCHW FP32 /255. Network input must be
1×3×640×640 for every model/frame. Record native dimensions and input shape.
`retina_masks=True` uses native Ultralytics original-resolution mask reconstruction
after undoing letterbox, binary threshold and native empty-mask removal. Pilot
lossless GPU bit-packing and compact CPU transfer are preserved. Save compressed
COCO RLE, class, confidence, xyxy bbox and source size for every prediction.

OOM/crash: record model/frame/exception/GPU/allocator state, stop. No easier
settings for one model. Completed frames are atomic files; failed runs are kept.
No automatic resume or silent overwrite. A future explicitly documented resume
must verify manifest/config/checkpoint hashes and unique frame keys.

## Frozen evaluator

Byte-identical snapshot of validated pilot `metrics.py` and `mots.py`, with
SHA256 provenance in `manifests/source_manifest.json`. Run its regression suite
read-only before preflight. Do not modify matching or definitions.

Person GT class 2; class 10 masks unioned per frame. Fixed metrics select saved
predictions with confidence >=0.25, descending score and stable input ties.
Greedy one-to-one match at mask IoU >=0.50; best IoU then GT object ID breaks ties.
Valid Person GT has priority. Only unmatched predictions are ignored when
intersection(prediction, union(ignore))/area(prediction) >=0.50. Otherwise FP.
Person masks are not clipped. Dataset micro TP/FP/FN determine P/R/F1.
Matched-only IoU and Dice=2IoU/(1+IoU) report mean, median, population std, P25/P75.
These conditional TP statistics are not overall dataset mask quality.

AP uses frozen confidence-ranked Person-only COCO frame-level segmentation
evaluator, mask IoUs 0.50:0.05:0.95, 101 recall points. Ignore crowd overlap is
mapped to 1/0 at the fixed 0.50 prediction-area threshold, preserving valid-GT
priority at every AP IoU. Report AP50/AP75/mAP50-95 on 0–1 scale. This is not
official MOTS tracking evaluation; no tracking metrics are computed.

Preflight evaluates saved predictions at maxDet 100/200/300/1000 without further
inference. Require the cross-experiment common cap 200, whose absolute AP50, AP75 and mAP50-95
differences from 1000 are each <0.0001 for all four models. 1000 is the reference,
not evidence that an unobserved tail beyond model cap is harmless. Stop on model
cap saturation, invalid/nonfinite metrics or failed compatibility. STOP if 200 fails; otherwise freeze 200
in YAML and append decision before full benchmark starts.

## Timing, memory and contamination

Dedicated timing follows accuracy. Seed 20260929 permutes the four model names;
three rounds cyclically rotate this seeded order. Save exact order in advance.
Each run releases previous model, garbage collects and clears CUDA cache; model
load/initialization time is separate. Ten untimed inferences cycle first ten
subset frames. Reset allocator peak stats after warmup and record baseline.
Read/decode each image before timing; synchronize CUDA at every stage boundary.

Preprocessing includes transforms and H2D transfer; inference is forward pass;
postprocessing includes NMS, native masks, binary validation, GPU bit-packing,
compact CPU transfer and prediction objects, as in pilot. Total pipeline is
preprocess+inference+postprocess. RLE encoding/evaluation preparation is timed
separately. Exclude disk I/O, model loading, GT, metrics, visualization, CSV/JSON.
Report mean, median/P50, population std and P95; FPS=1000/mean pipeline ms.
Three repeats, identical order within the subset, 300 measured frames/model.
Report peak allocated/reserved MiB and baseline, including resident model;
allocator memory is not whole-device nvidia-smi memory.

Collect nvidia-smi utilization, memory, temperature, power, clocks and processes
before and after every run and periodically between timed frames (outside timers).
Conservatively mark contaminated if any other compute PID is present or pre-load
idle GPU utilization exceeds 5%. Exclude entire contaminated run from primary
speed results; retain diagnostics. A contaminated round may be repeated unchanged
when idle, otherwise speed comparison is incomplete. Never rank incomplete speed.

## Outputs, analyses and final gate

Fresh run directories and stdout/stderr, timestamps, settings, source/checkpoint
hashes, GPU state, exceptions, candidate counts, progress, atomic RLE predictions.
Regenerate accuracy from saved predictions; AP overall is pooled, not an average
of sequence AP. Report per sequence and per frame, matched instances, ignore
counts, GT size (area/bbox/source-normalized values) and relative mask area
min/P10/P25/median/P75/P90/max. Crowd descriptions group by exact GT person count;
do not equate density with annotated occlusion. No size thresholds invented.

Main report has Thai summary, complete technical tables, plots from saved CSVs,
predetermined qualitative sheets and preserved run summary. Final gate compares
frame lists/counts, evaluator/config/maxDet/confidence/NMS/preprocessing/precision/
resolution/GT, input hashes, metrics completeness and clean timing. Accuracy
ranking uses mask mAP50-95; efficiency trade-offs have no combined weighted score.
Adjacent video frames are correlated; no independent-image significance claim.
Different model capacities and pretraining are confounders. MOTS20 alone cannot
establish controlled blur, lighting, camera-angle or final CCTV robustness.


## Cross-experiment commitments frozen before preflight

Experiment 1 remains read-only. Use its exact saved ordered all-frame, preflight,
timing and visualization manifests, verified against current images, dimensions,
GT and sequence metadata before inference. Dataset audit and reference report
SHA256 are in manifests/shared_input_audit.json. Recomputed GT area and crowd
data must be byte-identical. The original reference evaluator, adapter and
visualization implementations are preserved byte-for-byte in src/frozen_pilot.
No Experiment 1 inference is rerun. Compare its preserved clean timing results.

The 100-frame preflight tests 100/200/300/1000. Even if 100 converges, retain 200.
If 200 fails any strict <0.0001 check, STOP before full inference and establish
a common policy with the user. No unilateral cap or methodology changes.

Timing uses Experiment 1's idle-gated clean repetition runner and identical
measured loop, ten warmups, seed and cyclic family ordering. All contaminated
rounds are excluded. Any required repetition retains the original records.

Cross-tier differences are second-largest minus largest. AP, recall and F1
percentage-point differences equal 100 times the difference on the 0–1 scale.
Relative change is 100*(second-largest/largest-1), reported separately.
Report inference and pipeline latency, mean-derived FPS, allocator peak VRAM,
parameters and checkpoint size without assuming that smaller models are faster.
No significance claim or arbitrary weighted score. Both experiments describe
available model tiers, not capacity-controlled architecture superiority or final
CCTV suitability, controlled blur/lighting/camera-angle/occlusion robustness.

Before full inference freeze config, protocol, sources, dataset/checkpoint
manifests, exact frame lists and Experiment 1 report hashes. Changes to model
names, storage paths and the stricter cross-tier cap gate do not change evaluator
semantics or the measurement method. This protocol is frozen before preflight;
only its predeclared maxDet decision may be appended before full inference.

## Preflight decision — 2026-10-01T03:55:43.787555+00:00

Run `benchmark-20261001T0352Z` passed all four models, 100 frames each. Common AP maxDet = **200**. All three AP absolute differences from 1000 are <0.0001 for every model. See `metrics/benchmark-20261001T0352Z/preflight_maxdet.csv`. This decision precedes full accuracy.
