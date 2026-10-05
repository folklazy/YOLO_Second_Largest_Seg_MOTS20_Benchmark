# สรุปผล Second-largest (L/C) YOLO Instance Segmentation

## สรุปใน 1 นาที

- โมเดล: YOLO26l-Seg, YOLO11l-Seg, YOLOv9c-Seg, YOLOv8l-Seg
- MOTS20 2,862 frames / 26,894 Person GT instances (annotation รายเฟรม)
- Official pretrained checkpoints / no fine-tuning; สถานะเดิม PASS WITH WARNINGS
- Accuracy สูงสุด: YOLO26l-Seg — Mask mAP50-95 0.586237
- เร็วสุด: inference YOLOv9c-Seg (35.293 ms); pipeline YOLO26l-Seg (76.403 ms)
- Peak allocated VRAM ต่ำสุด: YOLO26l-Seg — 777.52 MiB
- Trade-off หลัก: YOLO26l-Seg นำรองอันดับสอง 5.800857 percentage points ของ mAP; เวลา inference มากกว่าตัวเร็วสุด 0.973 ms

## ผลลัพธ์หลัก

| Model | Mask mAP50-95 | AP75 | Recall | Inference ms | Pipeline ms | FPS | Peak VRAM MiB |
|---|---|---|---|---|---|---|---|
| YOLO26l-Seg | 0.586237 | 0.643537 | 0.834387 | 36.266 | 76.403 | 13.089 | 777.52 |
| YOLO11l-Seg | 0.528228 | 0.565728 | 0.809772 | 35.387 | 76.810 | 13.019 | 794.47 |
| YOLOv9c-Seg | 0.517646 | 0.559180 | 0.802930 | 35.293 | 76.921 | 13.000 | 838.49 |
| YOLOv8l-Seg | 0.520145 | 0.558149 | 0.809400 | 40.090 | 83.558 | 11.968 | 855.27 |

## สรุปผลจากตาราง

อ่านร่วมกับตารางหลักด้านบน; AP50 และ TP-only IoU/Dice อ้างอิง [canonical CSV](metrics/TIER_RESULTS.csv) และ [REPORT.md](REPORT.md) ตัวเลข TP-only วัดเฉพาะคู่ที่ match ได้ จึงไม่แทนความครอบคลุม GT หรือคุณภาพทุก instance

### YOLO26l-Seg

นำทั้ง AP50, AP75, mAP50-95, Recall และ TP-only IoU/Dice; Recall 83.44% จึงสนับสนุนความครอบคลุม GT ที่สูงกว่าใน tier นี้ แต่ยังมีคนพลาดหรือจับคู่ไม่ผ่าน และ TP-only quality บอกเฉพาะคู่ที่ผ่าน matching

ต่างจาก Largest รุ่นนี้มีทั้ง pipeline 76.403 ms เร็วสุดและ VRAM 777.52 MiB ต่ำสุดด้วย จึงเป็น candidate ที่เด่นเมื่อพิจารณา accuracy ร่วมกับ pipeline/memory สิ่งที่ยังแลกคือ inference 36.266 ms ช้ากว่า YOLO11l/YOLOv9c ไม่ใช่ผู้ชนะทุกด้าน และช่องว่าง pipeline ที่เล็กยังไม่พิสูจน์ความมีนัยสำคัญ

### YOLO11l-Seg

mAP/AP50/AP75 สูงเป็นอันดับสอง และ Recall/TP-only quality สูงกว่า YOLOv9c และ YOLOv8l ตามค่าที่วัด Inference 35.387 ms ใกล้ YOLOv9c (35.293 ms) มาก จึงไม่ควรตัดสินคู่นี้จากอันดับเวลาเพียงอย่างเดียว

เมื่อเทียบ YOLO26l มี accuracy ต่ำกว่า pipeline ช้ากว่าเล็กน้อยและ VRAM สูงกว่า แต่ forward เร็วกว่า จึงเป็น candidate สำหรับตรวจ trade-off ของ forward latency กับ accuracy ไม่ใช่ “สมดุลดีที่สุด” โดยอัตโนมัติ

### YOLOv9c-Seg

มี inference 35.293 ms ต่ำสุด แต่เร็วกว่า YOLO11l เพียงเล็กน้อย ขณะที่ pipeline 76.921 ms ช้ากว่า YOLO26l และ YOLO11l; VRAM 838.49 MiB ก็ไม่ได้ต่ำสุด ความเร็ว forward จึงไม่แปลว่า pipeline หรือ memory ได้เปรียบทั้งหมด

mAP ต่ำสุดใน tier แต่ AP75 สูงกว่า YOLOv8l เล็กน้อย ขณะที่ Recall ต่ำกว่า แสดงว่าอันดับเปลี่ยนได้ตามเกณฑ์ที่สนใจ เหมาะเก็บเป็น candidate เมื่อต้องการตรวจข้อจำกัด forward โดยเทียบ YOLO11l ด้วย ไม่ควรสรุปว่าชนะด้านความเร็วอย่างมีนัยสำคัญ

### YOLOv8l-Seg

mAP สูงกว่า YOLOv9c เล็กน้อย แต่ AP75 และ TP-only IoU/Dice ต่ำกว่าเล็กน้อย; Recall ใกล้ YOLO11l มาก จึงไม่ควรเรียกว่าด้อยสุดด้าน accuracy ทุกตัวชี้วัด อย่างไรก็ตาม inference 40.090 ms และ pipeline 83.558 ms ช้าที่สุด พร้อม VRAM 855.27 MiB สูงสุด

YOLO26l และ YOLO11l มี mAP/AP75/Recall สูงกว่า พร้อม latency ต่ำกว่าและใช้ VRAM น้อยกว่าในรอบนี้ จึงไม่มีข้อได้เปรียบในแกนที่วัดสำหรับเลือกเป็นตัวนำ แต่ยังมีประโยชน์เป็น baseline รุ่นก่อน ผลนี้ไม่อธิบายสาเหตุจาก architecture หรือรับรองอันดับบนข้อมูลใหม่

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

- mAP ของ YOLO26l-Seg สูงกว่า YOLO11l-Seg 5.800857 percentage points
- YOLOv9c กับ YOLOv8l มี mAP ต่างกัน 0.002498 (0.249819 percentage points); ค่อนข้างใกล้กันเชิงพรรณนา
- Inference ของ YOLOv9c กับ YOLO11l ต่างเพียง 0.094 ms; pipeline ของ YOLO26l กับ YOLO11l ต่าง 0.408 ms
- YOLO26l ชนะทั้ง accuracy, pipeline และ VRAM แต่ inference ไม่เร็วสุด; จึงต้องแยกเวลา forward จาก pipeline

## Trade-off หลัก

### Accuracy vs Speed

YOLO26l-Seg มี mAP 0.586237; YOLOv9c-Seg มี mAP 0.517646
และ inference 35.293 ms เทียบกับ 36.266 ms ของ accuracy winner
Pipeline winner คือ YOLO26l-Seg (76.403 ms); ไม่ใช้เวลา forward แทน throughput ของ pipeline

### Accuracy vs Memory

YOLO26l-Seg ชนะทั้ง accuracy และ memory: mAP 0.586237 / 777.52 MiB
เทียบกับ YOLO11l-Seg ที่ mAP 0.528228 / 794.47 MiB; รอบนี้ไม่มีการแลก accuracy ลดลงเพื่อ VRAM ต่ำลงระหว่างสองรุ่นนี้

## ข้อควรระวังในการตีความ

ไม่มีการทดสอบ statistical significance; near tie เป็นคำบรรยาย ค่า AP/Recall อยู่ช่วง 0–1
Pipeline ไม่รวม RLE preparation และ disk I/O; VRAM เป็น peak allocated
MOTS20 ไม่ใช่ผลทดสอบ CCTV robustness ขั้นสุดท้าย และ E/X, C/L ไม่ใช่ capacity เท่ากัน

## ข้อมูลสำหรับนำไปรวมต่อ

นำ YOLO26l สำหรับ accuracy/pipeline/VRAM และ YOLOv9c สำหรับ inference; เก็บ YOLO11l เทียบ latency ที่ใกล้กัน ไปเทียบข้าม tier โดยคง protocol และแหล่ง canonical เดิม ยังไม่สรุปครบ 17 โมเดล

[TIER_RESULTS.csv](metrics/TIER_RESULTS.csv) · [REPORT.md](REPORT.md) ·
[Visual analysis](PRESENTATION_SUMMARY_TH.md) ·
[Master Study](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study)
