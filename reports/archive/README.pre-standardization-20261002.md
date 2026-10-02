# Experiment 2: Second-largest available YOLO segmentation models on MOTS20

**Status: PASS WITH WARNINGS — 4 models × 2,862 accuracy frames; 3 clean timing rounds/model.**

## สรุป Benchmark แบบกระชับ

- เปรียบเทียบ **YOLO26l-Seg, YOLO11l-Seg, YOLOv9c-Seg และ YOLOv8l-Seg** รุ่น segmentation **ใหญ่เป็นอันดับสองที่มีให้ใช้จากแต่ละตระกูล** โดย YOLOv9 ใช้รุ่น c และทั้งสี่โมเดลมี capacity ไม่เท่ากัน
- ใช้ **MOTS20 train ครบ 2,862 ภาพ และ 26,894 Person GT instances** ซึ่งนับคนแยกตามภาพ ไม่ใช่จำนวนคนไม่ซ้ำทั้งวิดีโอ
- ใช้ pretrained checkpoints โดย **ไม่ฝึกใหม่และไม่ fine-tune** เพื่อดูการนำโมเดลสำเร็จรูปมาใช้กับข้อมูลชุดนี้
- ทุกโมเดลใช้ภาพและเกณฑ์เดียวกับ Experiment 1: **Tesla T4, FP32, batch 1, input 640×640 และ NMS-based prediction** โดย preflight ยืนยันให้ใช้ AP maxDet=200 ร่วมกันได้
- **YOLO26l-Seg เด่นด้าน accuracy และสมดุลโดยรวมในผลชุดนี้**: Mask mAP50-95 สูงสุด **0.586237**, Recall สูงสุด **0.834387**, pipeline mean ต่ำสุด **76.403 ms** และ peak allocated VRAM ต่ำสุด **777.520 MiB**
- **YOLOv9c-Seg มี inference mean ต่ำสุด 35.293 ms** แต่เร็วกว่า YOLO11l เพียง **0.094 ms** และ pipeline ของ YOLO26l/YOLO11l/YOLOv9c ต่างกันไม่ถึง **0.52 ms** จึงไม่ควรตีความว่าชนะด้านความเร็วอย่างมีนัยสำคัญ
- เมื่อเทียบกับรุ่นใหญ่สุดของตระกูลเดียวกัน **mAP ลด 0.461–1.900 percentage points แลกกับ inference latency ที่ลด 40.91–49.95%** แต่ VRAM ไม่ได้ลดตามขนาดโมเดลเสมอไป เช่น v9e→v9c ลด peak allocated เพียง **1.98%**
- ผลนี้ช่วยเลือกตัวแทนไปทดลองต่อ แต่ **ยังไม่ยืนยันความทนทานใน CCTV จริงทุกสภาพ** และไม่ใช่การพิสูจน์ความเหนือกว่าของ architecture ภายใต้ capacity ที่เท่ากัน; เวลา pipeline ที่รายงานไม่รวม RLE preparation และ disk I/O

- 📊 อ่านสรุป Benchmark แบบเข้าใจง่าย → [BENCHMARK_INSIGHTS_TH.md](BENCHMARK_INSIGHTS_TH.md)
- 📄 Technical Benchmark Report → [REPORT.md](REPORT.md)
- 🧪 Experimental Protocol → [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md)
- [Experiment 1: largest available variants](https://github.com/folklazy/YOLO_Large_Seg_MOTS20_Benchmark)

## รายละเอียด Dataset ที่ใช้

### ข้อมูลทั่วไปแบบสั้น

- **ชุดข้อมูล:** MOTS20 train จำนวน 4 วิดีโอ (02, 05, 09, 11) รวม **2,862 ภาพ** และ **26,894 Person GT instances** โดยคนเดิมที่อยู่หลายภาพถูกนับซ้ำตามภาพ
- **FPS ของวิดีโอต้นฉบับ:** 30 FPS สำหรับ 02, 09, 11 และ 14 FPS สำหรับ 05; ตัวเลขนี้เป็นอัตราเฟรมของข้อมูล ไม่ใช่ FPS ที่โมเดลประมวลผลได้
- **ความละเอียดต้นฉบับ:** 1920 × 1080 สำหรับ 02, 09, 11 และ 640 × 480 สำหรับ 05
- **ฉากที่มี:** คนเดินในจัตุรัสขนาดใหญ่ (02), ฉากถนนจากกล้องที่เคลื่อนที่ (05), ถนนคนเดินถ่ายจากมุมต่ำ (09), และกล้องเคลื่อนไปข้างหน้าในบริเวณช้อปปิ้งที่มีคนพลุกพล่าน (11; เว็บไซต์ทางการเรียกว่า “shopping mall”)
- **ลักษณะป้ายกำกับ:** มี mask แยกคนแต่ละคนและพื้นที่ ignore; benchmark นี้วัดการแยกคนรายภาพ ไม่ได้วัด tracking

ตรวจ FPS และความละเอียดกับ `seqinfo.ini` ของทั้ง 4 sequences ในชุดข้อมูลที่ใช้จริง และตรวจคำอธิบายฉากกับ [MOTChallenge: MOTS](https://motchallenge.net/data/MOTS/) แล้ว ข้อมูลตัวอย่างที่ทุก sequence เป็น 25 FPS และมีฉากสถานีรถไฟ/สนามกีฬาตอนกลางคืนเป็นของ [MOT20](https://motchallenge.net/data/MOT20/) ซึ่งเป็นคนละชุดกับ **MOTS20** ที่ใช้ในการทดลองนี้

### รายละเอียดประกอบ

ใช้ **MOTS20 train ทั้ง 4 sequences รวม 2,862 ภาพ** เป็นภาพต่อเนื่องจากวิดีโอที่มี Ground Truth (GT) แบบ **instance segmentation**: ระบุพื้นที่พิกเซลของคนแต่ละคนด้วย mask และมี object ID แยกบุคคล การทดลองนี้ประเมินการแยกคน **รายภาพ** ไม่ได้ประเมินการติดตามคนข้ามเฟรมหรือ tracking metrics

| Sequence | จำนวนภาพ | ความละเอียดต้นฉบับ (กว้าง × สูง) | Person GT instances | Ignore annotations |
| --- | ---: | --- | ---: | ---: |
| MOTS20-02 | 600 | 1920 × 1080 | 7,039 | 600 |
| MOTS20-05 | 837 | 640 × 480 | 6,570 | 802 |
| MOTS20-09 | 525 | 1920 × 1080 | 4,774 | 525 |
| MOTS20-11 | 900 | 1920 × 1080 | 8,511 | 900 |
| **รวม** | **2,862** | สองความละเอียด | **26,894** | **2,827** |

**อ่านจำนวนเหล่านี้อย่างไร**

- **26,894 Person GT instances** คือจำนวนคนที่ติดป้ายกำกับรวมทุกภาพ เฉลี่ยประมาณ **9.40 คนต่อภาพ** คนเดิมที่ปรากฏหลายเฟรมถูกนับหลายครั้ง จึงไม่ใช่จำนวนคนไม่ซ้ำทั้งชุด
- **Person GT ใช้ class 2** ส่วนผลทำนายจาก YOLO ใช้ COCO class 0 = `person` เป็นคนละระบบหมายเลขคลาสที่ evaluator จับคู่ให้ตรงกัน
- **Ignore ใช้ class 10** จำนวน 2,827 คือจำนวน annotations ของพื้นที่ ignore รวมทุกเฟรม ไม่ใช่จำนวนคนหรือจำนวน predictions ที่ถูก ignore โดย evaluator จะจับคู่กับ Person GT ก่อน แล้วจึงไม่นับ unmatched prediction เป็น FP หากพื้นที่ของ prediction ทับกับ union ของ ignore masks ตั้งแต่ 50% ขึ้นไป

**ไฟล์ข้อมูลและวิธีใช้ในการทดลอง**

- ภาพต้นฉบับ: `datasets/MOTS/MOTS/train/<sequence>/img1/`
- GT: `datasets/MOTS/MOTS/train/<sequence>/gt/gt.txt` โดย mask เก็บแบบ **RLE** ซึ่งบีบอัดตำแหน่งพิกเซลและถอดกลับเป็น mask ได้
- ใช้ GT ที่มากับแต่ละ sequence เท่านั้น ไม่ใช้ `datasets/MOTSLabels/MOTSLabels/` เป็น GT อีกชุด และไม่ใช้ MOTS20 test คำนวณ accuracy ในการทดลองนี้
- แม้โฟลเดอร์ชื่อ `train` แต่ครั้งนี้ใช้สำหรับ **ประเมิน pretrained models เท่านั้น** ไม่มีการฝึกใหม่, fine-tune, ดัดแปลงภาพต้นฉบับ หรือสร้าง split ใหม่
- ก่อนเข้าโมเดล ทุกภาพผ่าน resize แบบคงสัดส่วนและเติมขอบให้เป็น **640 × 640**; การประเมิน mask ใช้ความละเอียดต้นฉบับ จึงไม่ควรเข้าใจว่าภาพใน dataset มีขนาด 640 × 640 อยู่แล้ว
- ใช้ **100 ภาพเดิม** สำหรับ preflight และ timing และ **12 ภาพเดิม** สำหรับ visualization ตามรายการที่กำหนดไว้ใน Experiment 1 ทั้งหมดเป็นส่วนหนึ่งของ 2,862 ภาพ ไม่ใช่ชุดข้อมูลเพิ่ม

**ขนาดคนและข้อจำกัดของข้อมูล**

พื้นที่ mask คนหารด้วยพื้นที่ภาพต้นฉบับมีค่ามัธยฐานประมาณ **0.627%**; percentile 10 และ 90 อยู่ที่ประมาณ **0.081%** และ **5.875%** ตามลำดับ จึงมีความหลากหลายของขนาดคนในภาพ โดยไม่ได้กำหนดเกณฑ์ small/medium/large เพิ่มเอง จำนวนคนต่อภาพใช้บรรยายความหนาแน่น ไม่ใช่ป้ายระดับการบังกัน (occlusion severity)

ภาพวิดีโอต่อเนื่องมีความสัมพันธ์กัน จึงไม่ใช่ภาพอิสระ 2,862 ตัวอย่าง และข้อมูลชุดนี้ยังไม่ครอบคลุมการทดสอบ CCTV แบบควบคุม blur, low-light, มุมกล้อง หรือระดับ occlusion โดยเฉพาะ

ตรวจยืนยันแล้วว่ารายการ/ลำดับภาพ, image hashes, GT hashes, sequence metadata และความละเอียดตรงกับ Experiment 1 ดูหลักฐานใน [dataset manifest](manifests/dataset_manifest.json), [shared input audit](manifests/shared_input_audit.json) และ [ข้อมูลขนาดคน](metrics/person_size_distribution.json)

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
