# Second-largest (L/C) การทดสอบ YOLO Instance Segmentation — MOTS20

## 1. สถานะการทดลอง

PASS WITH WARNINGS

- โมเดลที่เสร็จแล้ว: 4/4
- จำนวนเฟรม: 2,862 ต่อโมเดล; Person GT รายเฟรม: 26,894 instances
- รหัสรอบทดลอง: `benchmark-20261001T0352Z`

## 2. โมเดลที่ทดสอบ

| ตระกูล | โมเดล | จำนวนพารามิเตอร์ | GFLOPs | Checkpoint (MB) |
| --- | --- | --- | --- | --- |
| YOLO26 | YOLO26l-Seg | 31,515,528 | 151.304 | 63.70 |
| YOLO11 | YOLO11l-Seg | 27,678,368 | 133.176 | 56.10 |
| YOLOv9 | YOLOv9c-Seg | 27,897,120 | 149.340 | 56.47 |
| YOLOv8 | YOLOv8l-Seg | 45,997,728 | 211.060 | 92.42 |

## 3. ความสอดคล้องกับโพรโทคอล

| รายการ | สถานะ |
|---|---|
| ข้อมูล | PASS |
| ตัวประเมิน | PASS |
| การเตรียมภาพ | PASS |
| ขนาดภาพเข้าโมเดล | PASS |
| ความละเอียดเชิงตัวเลข | PASS |
| ค่าเกณฑ์ | PASS |
| maxDet | PASS |
| วิธีวัดเวลา | PASS |
| สภาพแวดล้อม | PASS |

ความสอดคล้องของข้อมูล: PASS

ความสอดคล้องของการเตรียมภาพ: PASS

[วิธีทดลองร่วม](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study/blob/main/METHODOLOGY_REFERENCE.md) · [โพรโทคอลการทดลอง](EXPERIMENT_PROTOCOL.md) · [หลักฐานการกำหนดมาตรฐาน](manifests/STANDARDIZATION.json)

## 4. ผลลัพธ์รวม

| โมเดล | Mask mAP50-95 | AP50 | AP75 | Precision | Recall | F1 | TP-only IoU | TP-only Dice | Inference (ms) | Pipeline (ms) | FPS | Peak allocated VRAM (MiB) | จำนวนพารามิเตอร์ | GFLOPs | Checkpoint (MB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YOLO26l-Seg | 0.586237 | 0.889890 | 0.643537 | 0.935702 | 0.834387 | 0.882145 | 0.825340 | 0.900714 | 36.266 | 76.403 | 13.089 | 777.52 | 31,515,528 | 151.304 | 63.70 |
| YOLO11l-Seg | 0.528228 | 0.867132 | 0.565728 | 0.931599 | 0.809772 | 0.866424 | 0.801233 | 0.885822 | 35.387 | 76.810 | 13.019 | 794.47 | 27,678,368 | 133.176 | 56.10 |
| YOLOv9c-Seg | 0.517646 | 0.855414 | 0.559180 | 0.918776 | 0.802930 | 0.856956 | 0.798288 | 0.883840 | 35.293 | 76.921 | 13.000 | 838.49 | 27,897,120 | 149.340 | 56.47 |
| YOLOv8l-Seg | 0.520145 | 0.859978 | 0.558149 | 0.909425 | 0.809400 | 0.856502 | 0.797581 | 0.883410 | 40.090 | 83.558 | 11.968 | 855.27 | 45,997,728 | 211.060 | 92.42 |

## 5. ผู้ชนะในแต่ละด้าน

| ด้าน | โมเดล | ผลลัพธ์ |
| --- | --- | --- |
| Mask mAP50-95 สูงสุด | YOLO26l-Seg | 0.586237 |
| AP75 สูงสุด | YOLO26l-Seg | 0.643537 |
| Recall สูงสุด | YOLO26l-Seg | 0.834387 |
| Inference เร็วสุด | YOLOv9c-Seg | 35.293 |
| Pipeline เร็วสุด | YOLO26l-Seg | 76.403 |
| FPS สูงสุด | YOLO26l-Seg | 13.089 |
| VRAM ต่ำสุด | YOLO26l-Seg | 777.52 |

## 6. ข้อค้นพบสำคัญ

- ข้อสังเกต: YOLO26l-Seg มี Mask mAP50-95 สูงสุด 0.586237; ห่างอันดับถัดไป 0.058009 บนสเกล 0–1
- ข้อสังเกต: YOLO26l-Seg นำ AP75; YOLO26l-Seg นำ Recall
- ข้อสังเกต: YOLOv9c-Seg มี inference เร็วสุด; YOLO26l-Seg มี pipeline เร็วสุดและ FPS สูงสุด; YOLO26l-Seg มี VRAM ต่ำสุด
- คู่ mAP ใกล้ที่สุด: YOLOv9c-Seg / YOLOv8l-Seg ต่าง 0.002498; เป็นความใกล้เชิงพรรณนา ไม่ใช่ผลทดสอบนัยสำคัญทางสถิติ
- การตีความ: แยกความแม่นยำความครบถ้วนเวลา forward เวลา pipeline และหน่วยความจำไม่มีคะแนนรวมถ่วงน้ำหนักจำนวนพารามิเตอร์หรือ GFLOPs ไม่กำหนดอันดับเวลา/VRAM โดยตรง

## 7. ข้อสังเกตรายลำดับภาพ

- YOLO26l-Seg: Mask mAP50-95 สูงสุดที่ MOTS20-11 (0.640991); ต่ำสุดที่ MOTS20-02 (0.469068)
- YOLO11l-Seg: Mask mAP50-95 สูงสุดที่ MOTS20-05 (0.595551); ต่ำสุดที่ MOTS20-02 (0.406686)
- YOLOv9c-Seg: Mask mAP50-95 สูงสุดที่ MOTS20-05 (0.580796); ต่ำสุดที่ MOTS20-02 (0.396062)
- YOLOv8l-Seg: Mask mAP50-95 สูงสุดที่ MOTS20-05 (0.581724); ต่ำสุดที่ MOTS20-02 (0.402322)
- ลำดับ mAP ที่ต่างจากผลรวม: MOTS20-09: YOLO26l-Seg > YOLO11l-Seg > YOLOv9c-Seg > YOLOv8l-Seg

AP รวมคำนวณจากข้อมูลทั้งหมด ไม่ใช่ค่าเฉลี่ย AP รายลำดับภาพ ดูค่าครบใน [PER_SEQUENCE_RESULTS.csv](metrics/PER_SEQUENCE_RESULTS.csv)

## 8. ประสิทธิภาพและการใช้ทรัพยากร

- คู่ที่ใกล้ที่สุดด้านค่าเฉลี่ย inference: YOLO11l-Seg / YOLOv9c-Seg ต่าง 0.094 ms; ไม่ได้ทดสอบนัยสำคัญทางสถิติ
- คู่ที่ใกล้ที่สุดด้านค่าเฉลี่ย pipeline: YOLO11l-Seg / YOLOv9c-Seg ต่าง 0.110 ms; ไม่ได้ทดสอบนัยสำคัญทางสถิติ

YOLO26l-Seg ใช้ peak allocated VRAM ต่ำสุดจำนวนพารามิเตอร์ก่อน/หลัง fusion, GFLOPs และเวลาโหลดแยกเก็บใน [MODEL_COMPLEXITY.csv](metrics/MODEL_COMPLEXITY.csv) ส่วน peak reserved VRAM อยู่ใน [แหล่งวัดเวลา](timing/benchmark-20261001T0352Z/clean_repetition/summary.csv) เวลาเตรียม RLE แยก: yolo26l-seg.pt: 230.058 ms; yolo11l-seg.pt: 242.013 ms; yolov9c-seg.pt: 254.257 ms; yolov8l-seg.pt: 259.788 ms.

ใช้ 3 รอบที่ไม่ถูกรบกวนต่อโมเดล รอบละ 100 เฟรมหลัง 10 warmups และ synchronize CUDA ตามขอบเขต stage ค่า pipeline รวม preprocessing, inference และ postprocessing ไม่รวมการเตรียม RLE และการอ่านเขียนดิสก์ FPS จึงไม่ใช่อัตราการบันทึก mask ครบกระบวนการและไม่บวก Ultralytics-inclusive diagnostic ซ้ำ

ค่าเฉลี่ย postprocessing: YOLO26l-Seg: 38.483 ms; YOLO11l-Seg: 39.709 ms; YOLOv9c-Seg: 39.938 ms; YOLOv8l-Seg: 41.748 ms

## 9. คำเตือนและข้อสังเกตผิดปกติ

เก็บสถานะ PASS WITH WARNINGS และคำเตือน NNPACK/pycocotools จากหลักฐานรอบเดิม การตรวจตัวประเมินและโพรโทคอลผ่าน ไม่มีการเปลี่ยน package เพื่อซ่อนคำเตือน ใช้เวลาเฉพาะ clean repetitions ที่ยอมรับตามหลักฐานต้นทาง

Pipeline ไม่รวมการเตรียม RLE และการอ่านเขียนดิสก์จึงไม่ใช่เวลา/อัตราประมวลผลครบกระบวนการสำหรับการบันทึก mask หรือระบบ CCTV การปรับเอกสารครั้งนี้ไม่รัน inference ใหม่และไม่เปลี่ยนค่าที่วัด

## 10. ข้อจำกัด

ผลนี้เป็น Person instance segmentation รายเฟรมบน MOTS20 ไม่ใช่ MOTS tracking; TP-only IoU/Dice พิจารณาเฉพาะคู่ที่ จับคู่ ได้ ภาพวิดีโอต่อเนื่องสัมพันธ์กันและไม่ได้ทดสอบนัยสำคัญทางสถิติค่าใกล้กันควรอ่านว่าใกล้กันเชิงพรรณนารุ่น E/X และ C/L ไม่ใช่ capacity เท่ากัน ผลยังไม่ยืนยันภาพพร่า, แสงน้อย, มุมกล้อง, ระดับ occlusion หรือความพร้อมใช้งาน CCTV; เป็นตัวเลือกสำหรับการทดสอบต่อการประเมินความทนทานต่อ CCTV เท่านั้น

## 11. หลักฐานสำหรับตรวจสอบซ้ำ

- [TIER_RESULTS.csv](metrics/TIER_RESULTS.csv)
- [PER_SEQUENCE_RESULTS.csv](metrics/PER_SEQUENCE_RESULTS.csv)
- [TIMING_SUMMARY.csv](metrics/TIMING_SUMMARY.csv)
- [MODEL_COMPLEXITY.csv](metrics/MODEL_COMPLEXITY.csv)
- [PREFLIGHT_MAXDET.csv](metrics/PREFLIGHT_MAXDET.csv)

[แหล่งที่มาและค่า hash](manifests/STANDARDIZATION.json) · [โพรโทคอล](EXPERIMENT_PROTOCOL.md) · [รายการกราฟ](outputs/plots/INDEX.md) · [บันทึกย้อนหลัง](reports/archive/)

prediction แบบ RLE ที่ไม่สูญเสียข้อมูลและบันทึกการวัดเวลาละเอียดเก็บในเครื่องตามรหัสรอบทดลอง หลักฐานต้นทางคงเดิม; การปรับภาษานี้ไม่คำนวณค่าตัวชี้วัดใหม่และไม่รัน inference

## 12. ความเชื่อมโยงกับการศึกษาทุกขนาด

[การศึกษาหลัก](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study) — รายงานนี้กล่าวถึงขนาด Second-largest (L/C) เท่านั้นผลรวม 17 โมเดลยังรอคำสั่งจากผู้ใช้ แม้การทดลองทั้งห้าขนาดเสร็จแล้ว การปรับเอกสารไม่เริ่ม benchmark หรือการสังเคราะห์ผลใหม่

## การวิเคราะห์เชิงคุณภาพ

ภาพเปรียบเทียบเฟรมเดียวกัน 4 กรณีจาก prediction ที่บันทึกไว้ พร้อมข้อผิดพลาดที่พบและการตีความ อยู่ใน [PRESENTATION_SUMMARY_TH.md](PRESENTATION_SUMMARY_TH.md) ดู [เหตุผลเลือกกรณีปัจจุบัน](outputs/visualizations/qualitative/selection_v2/CASE_SELECTION.md) และ [ตัวชี้ชุดหลักฐาน](manifests/QUALITATIVE_SELECTION.json) รายงานเทคนิคนี้เชื่อมไปยังการวิเคราะห์ภาพเพื่อไม่เล่าเนื้อหาซ้ำ
