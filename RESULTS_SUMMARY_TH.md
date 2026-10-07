# สรุปผล Second-largest (L/C) YOLO Instance Segmentation

## สรุปใน 1 นาที

- โมเดล: YOLO26l-Seg, YOLO11l-Seg, YOLOv9c-Seg, YOLOv8l-Seg
- MOTS20 2,862 frames / 26,894 Person GT instances รายเฟรม
- Official pretrained checkpoints; ไม่มี training หรือ fine-tuning; สถานะ PASS WITH WARNINGS
- Accuracy สูงสุด: YOLO26l-Seg — Mask mAP50-95 0.586237
- Inference เร็วสุด: YOLOv9c-Seg — 35.293 ms
- Pipeline เร็วสุด: YOLO26l-Seg — 76.403 ms / 13.089 FPS
- Peak allocated VRAM ต่ำสุด: YOLO26l-Seg — 777.52 MiB
- Trade-off หลัก: ตัวนำ mAP สูงกว่ารองอันดับสอง 5.801 percentage points; ต้องแยก forward จาก pipeline

## ผลลัพธ์หลัก

| Model | Mask mAP50-95 | AP75 | Recall | Inference ms | Pipeline ms | FPS | Peak VRAM MiB |
|---|---|---|---|---|---|---|---|
| YOLO26l-Seg | 0.586237 | 0.643537 | 0.834387 | 36.266 | 76.403 | 13.089 | 777.52 |
| YOLO11l-Seg | 0.528228 | 0.565728 | 0.809772 | 35.387 | 76.810 | 13.019 | 794.47 |
| YOLOv9c-Seg | 0.517646 | 0.559180 | 0.802930 | 35.293 | 76.921 | 13.000 | 838.49 |
| YOLOv8l-Seg | 0.520145 | 0.558149 | 0.809400 | 40.090 | 83.558 | 11.968 | 855.27 |

AP/Recall เป็น fraction ช่วง 0–1; latency เป็น ms/frame และ FPS มาจาก mean pipeline

## Winner ของแต่ละด้าน

| ด้าน | Model | Result |
|---|---|---|
| Mask mAP50-95 | YOLO26l-Seg | 0.586237 |
| AP75 | YOLO26l-Seg | 0.643537 |
| Recall | YOLO26l-Seg | 0.834387 |
| Inference speed | YOLOv9c-Seg | 35.293 ms |
| Pipeline speed | YOLO26l-Seg | 76.403 ms |
| VRAM | YOLO26l-Seg | 777.52 MiB |

## สิ่งที่ตัวเลขบอกเรา

- YOLO26l-Seg นำ YOLO11l-Seg ด้าน mAP 5.801 percentage points
- YOLO26l นำ accuracy, pipeline และ memory พร้อมกันตามค่าที่วัด แต่ไม่ได้มี forward เร็วสุด
- YOLOv9c/YOLO11l มี forward ใกล้กันมาก และ pipeline ของสามรุ่นนำอยู่ใกล้กัน; ยังไม่มี significance test
- ไม่มีคู่ผ่าน descriptive mAP near-tie screen ≤0.001; ความใกล้ของ latency เป็นคนละประเด็น; near tie ไม่ใช่ equivalence หรือ statistical significance

## บทบาทของแต่ละโมเดล

| Model | จุดเด่น | สิ่งที่แลก | เหมาะพิจารณาเมื่อ |
|---|---|---|---|
| YOLO26l-Seg | นำ mAP/AP75/Recall; pipeline และ VRAM ต่ำสุด | Forward ช้ากว่า YOLO11l/YOLOv9c | เน้น accuracy ร่วมกับ pipeline/memory |
| YOLO11l-Seg | mAP/AP75 อันดับสอง; forward ใกล้ YOLOv9c | mAP ต่ำกว่า YOLO26l; pipeline/VRAM สูงกว่า | Forward เป็นข้อจำกัดและต้องการเทียบกับ YOLOv9c |
| YOLOv9c-Seg | Inference ต่ำสุดตาม mean ที่วัด | mAP ต่ำสุด; pipeline/VRAM ไม่ต่ำสุด | สนใจ forward โดยไม่ถือช่องว่างเล็กว่ามีนัยสำคัญ |
| YOLOv8l-Seg | mAP/Recall สูงกว่า YOLOv9c | Inference/pipeline ช้าสุด; VRAM สูงสุด | ต้องการ baseline และตรวจอันดับต่างกันตาม metric |

## Trade-off หลัก

### Accuracy vs Speed

YOLO26l-Seg มี mAP 0.586237; ตัว forward เร็วสุด YOLOv9c-Seg มี mAP 0.517646 และ inference ต่ำกว่า 0.973 ms ส่วน pipeline ต้องดู YOLO26l-Seg แยก ไม่ถือว่า forward winner เป็น throughput winner

### Accuracy vs Memory

YOLO26l-Seg นำทั้ง mAP และ allocated VRAM ต่ำสุดใน tier นี้ จึงไม่มีการแลก accuracy ลงเพื่อ memory ที่ต่ำกว่าในคู่ที่วัด ไม่ใช้ชื่อขนาดหรือ parameters แทน memory measurement

## ข้อควรระวังในการตีความ

ไม่มี significance test; ภาพวิดีโอสัมพันธ์กัน TP-only quality วัดเฉพาะคู่ที่ match และ Recall เป็น mask matching ไม่ใช่ box Recall Pipeline ไม่รวม decode, RLE preparation และการเขียนผล; VRAM เป็น peak allocated ภายใต้ benchmark นี้ การแบ่ง tier ไม่ทำให้ capacity/pretraining เท่ากัน และยังไม่ยืนยัน CCTV robustness ไม่มี weighted score หรือผู้ชนะทุกข้อจำกัด

## รายละเอียดเพิ่มเติม

[REPORT.md](REPORT.md) · [รายงานวิจัยภาพเชิงคุณภาพ](PRESENTATION_SUMMARY_TH.md) · [TIER_RESULTS.csv](metrics/TIER_RESULTS.csv) · [Master Study](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study)
