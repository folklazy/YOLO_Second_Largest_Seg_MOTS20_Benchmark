# Second-largest (L/C)

## สรุปแบบกระชับ

- ทดสอบ YOLO26l-Seg, YOLO11l-Seg, YOLOv9c-Seg, YOLOv8l-Seg สำหรับ Person instance segmentation
- MOTS20 2,862 frames และ 26,894 Person GT instances เป็น annotation รายเฟรม ไม่ใช่จำนวนบุคคลไม่ซ้ำ
- ใช้ pretrained checkpoints / no fine-tuning ภายใต้ controlled benchmark เดียวกัน
- Accuracy สูงสุด: YOLO26l-Seg — Mask mAP50-95 0.586237
- Inference เร็วสุด: YOLOv9c-Seg; pipeline เร็วสุด: YOLO26l-Seg
- Peak allocated VRAM ต่ำสุด: YOLO26l-Seg
- ค่าความต่างเล็กมากเป็นเพียง near-tied descriptively ไม่ได้พิสูจน์ statistical significance
- คง PASS WITH WARNINGS และใช้ผลย้อนหลังเดิมทั้งหมด ไม่รัน inference ใหม่

## โมเดลที่ทดสอบ

1. YOLO26: `yolo26l-seg.pt`
2. YOLO11: `yolo11l-seg.pt`
3. YOLOv9: `yolov9c-seg.pt`
4. YOLOv8: `yolov8l-seg.pt`

## 1. ผลลัพธ์หลัก

YOLO26l-Seg มี Mask mAP50-95 สูงสุด 0.586237 ส่วน YOLOv9c-Seg มี inference mean ต่ำสุด และ YOLO26l-Seg มี pipeline mean ต่ำสุด

YOLO26l-Seg ใช้ peak allocated VRAM ต่ำสุด การเลือกจึงต้องแยก accuracy, เวลา forward, pipeline และ memory; ความต่างเล็กมากไม่ควรตีความเป็นความเหนือกว่าทางสถิติ

## 2. ผลรวมโมเดล

| Model | Mask mAP50-95 | AP50 | AP75 | Precision | Recall | F1 | TP-only IoU | TP-only Dice | Inference ms | Pipeline ms | FPS | Peak VRAM allocated MiB | Parameters |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YOLO26l-Seg | 0.586237 | 0.889890 | 0.643537 | 0.935702 | 0.834387 | 0.882145 | 0.825340 | 0.900714 | 36.266 | 76.403 | 13.089 | 777.52 | 31,515,528 |
| YOLO11l-Seg | 0.528228 | 0.867132 | 0.565728 | 0.931599 | 0.809772 | 0.866424 | 0.801233 | 0.885822 | 35.387 | 76.810 | 13.019 | 794.47 | 27,678,368 |
| YOLOv9c-Seg | 0.517646 | 0.855414 | 0.559180 | 0.918776 | 0.802930 | 0.856956 | 0.798288 | 0.883840 | 35.293 | 76.921 | 13.000 | 838.49 | 27,897,120 |
| YOLOv8l-Seg | 0.520145 | 0.859978 | 0.558149 | 0.909425 | 0.809400 | 0.856502 | 0.797581 | 0.883410 | 40.090 | 83.558 | 11.968 | 855.27 | 45,997,728 |


## 3. สรุปผลจากตาราง

### YOLO26l-Seg

อันดับเชิงตัวเลข: accuracy 1, inference speed 3, VRAM ต่ำ 1 จากโมเดลใน tier นี้ จุดเด่นคือ accuracy / VRAM; จุดที่ด้อยกว่าคือ inference speed เหมาะเป็นตัวเลือกเริ่มต้นเมื่อให้ความสำคัญกับ accuracy แต่ต้องตรวจ latency ตามข้อจำกัดจริง

### YOLO11l-Seg

อันดับเชิงตัวเลข: accuracy 2, inference speed 2, VRAM ต่ำ 2 จากโมเดลใน tier นี้ จุดเด่นคือ accuracy / inference speed / VRAM; จุดที่ด้อยกว่าคือ ไม่ได้ชนะทุกเป้าหมายพร้อมกัน ควรเปรียบเทียบกับตัวนำตามข้อจำกัดของงาน ไม่สรุปว่าลำดับที่ใกล้กันมีนัยสำคัญ

### YOLOv9c-Seg

อันดับเชิงตัวเลข: accuracy 4, inference speed 1, VRAM ต่ำ 3 จากโมเดลใน tier นี้ จุดเด่นคือ inference speed; จุดที่ด้อยกว่าคือ accuracy / VRAM เหมาะพิจารณาเมื่อจำกัดเวลา forward และยอมรับ accuracy ที่ต่ำกว่าตัวนำได้

### YOLOv8l-Seg

อันดับเชิงตัวเลข: accuracy 3, inference speed 4, VRAM ต่ำ 4 จากโมเดลใน tier นี้ จุดเด่นคือ เป็นจุดอ้างอิงของตระกูลใน tier นี้; จุดที่ด้อยกว่าคือ accuracy / inference speed / VRAM ควรเปรียบเทียบกับตัวนำตามข้อจำกัดของงาน ไม่สรุปว่าลำดับที่ใกล้กันมีนัยสำคัญ

## 4. Insight ที่สำคัญ

- Observation: YOLO26l-Seg นำด้าน Mask mAP50-95 แต่การเลือกต้องพิจารณา inference และ pipeline แยกกัน
- Observation: YOLO26l-Seg ใช้ peak allocated VRAM ต่ำสุด; จำนวน parameters ไม่ใช่ตัวแทน VRAM โดยตรง
- Observation: YOLOv9c และ YOLO11l มี inference mean ใกล้กัน และ pipeline ของสามตัวนำใกล้กัน
- Interpretation: ผลนี้ช่วยเลือก candidate for later CCTV robustness evaluation ยังไม่ใช่ข้อยืนยัน deployment

## 5. Trade-off

### Accuracy

YOLO26l-Seg มี Mask mAP50-95 สูงสุดในชุดนี้

### Speed

YOLOv9c-Seg มี inference mean ต่ำสุด ส่วน YOLO26l-Seg มี pipeline mean ต่ำสุด; FPS ไม่รวม RLE preparation

### Memory / Resource

YOLO26l-Seg มี peak allocated VRAM ต่ำสุด ต้องแยกจาก whole-device GPU memory

### ภาพรวม

เลือกตามข้อจำกัดจริง ไม่รวมเป็น weighted score และไม่อนุมานสาเหตุจาก architecture เพียงอย่างเดียว

## 6. ถ้าต้องเลือกจาก Tier นี้

| Priority | Recommended model | Reason |
|---|---|---|
| Accuracy | YOLO26l-Seg | Mask mAP50-95 สูงสุด |
| Speed | YOLOv9c-Seg (inference); YOLO26l-Seg (pipeline) | แยกตามส่วนที่เป็นข้อจำกัด |
| Low VRAM | YOLO26l-Seg | peak allocated ต่ำสุด |
| Balanced trade-off | YOLO26l-Seg | accuracy สูงสุด พร้อม pipeline และ VRAM ต่ำสุด แต่ไม่ได้มี forward ต่ำสุด |


## 7. ข้อควรระวังในการตีความ

ผลนี้เป็น Person instance segmentation รายเฟรมบน MOTS20 ไม่ใช่ MOTS tracking; TP-only IoU/Dice พิจารณาเฉพาะคู่ที่ match ได้ ภาพวิดีโอต่อเนื่องสัมพันธ์กันและไม่ได้ทดสอบ statistical significance ค่าใกล้กันควรอ่านว่า near-tied descriptively รุ่น E/X และ C/L ไม่ใช่ capacity เท่ากัน ผลยังไม่ยืนยัน blur, low-light, มุมกล้อง, ระดับ occlusion หรือความพร้อมใช้งาน CCTV; เป็น candidate for later CCTV robustness evaluation เท่านั้น

คง PASS WITH WARNINGS; pipeline ไม่รวม RLE preparation และ disk I/O

## 8. สรุปสำหรับคุยกับพี่

- รอบนี้เทียบ Second-largest (L/C) ด้วย pretrained YOLO บน MOTS20 โดยใช้เงื่อนไขเดียวกัน
- ตัวนำด้าน accuracy คือ YOLO26l-Seg แต่ตัวที่ forward เร็วสุดคือ YOLOv9c-Seg
- ถ้าจำกัด VRAM ให้เริ่มพิจารณา YOLO26l-Seg โดยดู accuracy ที่ยอมรับได้ประกอบ
- จุดที่ต้องระวังคือค่าที่ใกล้กันยังไม่ได้พิสูจน์นัยสำคัญ และ FPS ไม่ใช่ throughput ของระบบ CCTV เต็มรูปแบบ
- ขั้นถัดไปควรเติม tier ที่ยังไม่ทดสอบด้วย protocol เดิม หลังได้รับอนุมัติเท่านั้น

## รายละเอียดเต็ม

[REPORT.md](REPORT.md) · [metrics/TIER_RESULTS.csv](metrics/TIER_RESULTS.csv) · [Master Study](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study)
