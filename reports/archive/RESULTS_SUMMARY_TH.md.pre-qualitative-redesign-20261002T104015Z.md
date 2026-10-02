# สรุปผล Second-largest (L/C) YOLO Instance Segmentation

## สรุปใน 1 นาที

- ทดสอบ YOLO26l-Seg, YOLO11l-Seg, YOLOv9c-Seg, YOLOv8l-Seg สำหรับ Person instance segmentation
- MOTS20 2,862 frames และ 26,894 Person GT instances เป็น annotation รายเฟรม ไม่ใช่จำนวนบุคคลไม่ซ้ำ
- ใช้ pretrained checkpoints / no fine-tuning ภายใต้ controlled benchmark เดียวกัน
- Accuracy สูงสุด: YOLO26l-Seg — Mask mAP50-95 0.586237
- Inference เร็วสุด: YOLOv9c-Seg; pipeline เร็วสุด: YOLO26l-Seg
- Peak allocated VRAM ต่ำสุด: YOLO26l-Seg
- ค่าความต่างเล็กมากเป็นเพียง near-tied descriptively ไม่ได้พิสูจน์ statistical significance
- คง PASS WITH WARNINGS และใช้ผลย้อนหลังเดิมทั้งหมด ไม่รัน inference ใหม่

## ผลหลัก

| Model | Mask mAP50-95 | Recall | F1 | Inference ms | Pipeline ms | FPS | Peak VRAM MiB |
| --- | --- | --- | --- | --- | --- | --- | --- |
| YOLO26l-Seg | 0.586237 | 0.834387 | 0.882145 | 36.266 | 76.403 | 13.089 | 777.52 |
| YOLO11l-Seg | 0.528228 | 0.809772 | 0.866424 | 35.387 | 76.810 | 13.019 | 794.47 |
| YOLOv9c-Seg | 0.517646 | 0.802930 | 0.856956 | 35.293 | 76.921 | 13.000 | 838.49 |
| YOLOv8l-Seg | 0.520145 | 0.809400 | 0.856502 | 40.090 | 83.558 | 11.968 | 855.27 |


## แต่ละโมเดลเด่นด้านไหน

**YOLO26l-Seg**: อันดับเชิงตัวเลข: accuracy 1, inference speed 3, VRAM ต่ำ 1 จากโมเดลใน tier นี้ จุดเด่นคือ accuracy / VRAM; จุดที่ด้อยกว่าคือ inference speed เหมาะเป็นตัวเลือกเริ่มต้นเมื่อให้ความสำคัญกับ accuracy แต่ต้องตรวจ latency ตามข้อจำกัดจริง

**YOLO11l-Seg**: อันดับเชิงตัวเลข: accuracy 2, inference speed 2, VRAM ต่ำ 2 จากโมเดลใน tier นี้ จุดเด่นคือ accuracy / inference speed / VRAM; จุดที่ด้อยกว่าคือ ไม่ได้ชนะทุกเป้าหมายพร้อมกัน ควรเปรียบเทียบกับตัวนำตามข้อจำกัดของงาน ไม่สรุปว่าลำดับที่ใกล้กันมีนัยสำคัญ

**YOLOv9c-Seg**: อันดับเชิงตัวเลข: accuracy 4, inference speed 1, VRAM ต่ำ 3 จากโมเดลใน tier นี้ จุดเด่นคือ inference speed; จุดที่ด้อยกว่าคือ accuracy / VRAM เหมาะพิจารณาเมื่อจำกัดเวลา forward และยอมรับ accuracy ที่ต่ำกว่าตัวนำได้

**YOLOv8l-Seg**: อันดับเชิงตัวเลข: accuracy 3, inference speed 4, VRAM ต่ำ 4 จากโมเดลใน tier นี้ จุดเด่นคือ เป็นจุดอ้างอิงของตระกูลใน tier นี้; จุดที่ด้อยกว่าคือ accuracy / inference speed / VRAM ควรเปรียบเทียบกับตัวนำตามข้อจำกัดของงาน ไม่สรุปว่าลำดับที่ใกล้กันมีนัยสำคัญ

## สิ่งที่น่าสนใจจากรอบนี้

- Observation: YOLO26l-Seg นำด้าน Mask mAP50-95 แต่การเลือกต้องพิจารณา inference และ pipeline แยกกัน
- Observation: YOLO26l-Seg ใช้ peak allocated VRAM ต่ำสุด; จำนวน parameters ไม่ใช่ตัวแทน VRAM โดยตรง
- Observation: YOLOv9c และ YOLO11l มี inference mean ใกล้กัน และ pipeline ของสามตัวนำใกล้กัน
- Interpretation: ผลนี้ช่วยเลือก candidate for later CCTV robustness evaluation ยังไม่ใช่ข้อยืนยัน deployment

## Trade-off ที่เห็น

### Accuracy

YOLO26l-Seg มี Mask mAP50-95 สูงสุดในชุดนี้

### Speed

YOLOv9c-Seg มี inference mean ต่ำสุด ส่วน YOLO26l-Seg มี pipeline mean ต่ำสุด; FPS ไม่รวม RLE preparation

### Memory / Resource

YOLO26l-Seg มี peak allocated VRAM ต่ำสุด ต้องแยกจาก whole-device GPU memory

### ภาพรวม

เลือกตามข้อจำกัดจริง ไม่รวมเป็น weighted score และไม่อนุมานสาเหตุจาก architecture เพียงอย่างเดียว

## สิ่งที่ต้องระวังในการตีความ

ผลนี้เป็น Person instance segmentation รายเฟรมบน MOTS20 ไม่ใช่ MOTS tracking; TP-only IoU/Dice พิจารณาเฉพาะคู่ที่ match ได้ ภาพวิดีโอต่อเนื่องสัมพันธ์กันและไม่ได้ทดสอบ statistical significance ค่าใกล้กันควรอ่านว่า near-tied descriptively รุ่น E/X และ C/L ไม่ใช่ capacity เท่ากัน ผลยังไม่ยืนยัน blur, low-light, มุมกล้อง, ระดับ occlusion หรือความพร้อมใช้งาน CCTV; เป็น candidate for later CCTV robustness evaluation เท่านั้น

คงคำเตือน NNPACK และ pycocotools ตามหลักฐานเดิม

## ข้อมูลสำหรับนำไปรวมต่อ

[metrics/TIER_RESULTS.csv](metrics/TIER_RESULTS.csv) · [REPORT.md](REPORT.md) · [PRESENTATION_SUMMARY_TH.md](PRESENTATION_SUMMARY_TH.md) · [Master Study](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study)
