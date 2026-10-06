# Second-largest (L/C) — การทดสอบ YOLO Instance Segmentation บน MOTS20

## ภาพรวม

เปรียบเทียบการแยก Person เป็นราย instance บน MOTS20 ด้วยโมเดล pretrained โดยไม่ฝึกเพิ่มหรือปรับจูน ประเมินรายเฟรมไม่ใช่การติดตามคน เอกสารนี้ใช้แนะนำ repository และเชื่อมไปยังผลเชิงตัวเลขรายงานเทคนิคและการวิเคราะห์ภาพ

## โมเดลที่ทดสอบ

| ตระกูล | โมเดล | ขนาด |
| --- | --- | --- |
| YOLO26 | YOLO26l-Seg | Second-largest (L/C) |
| YOLO11 | YOLO11l-Seg | Second-largest (L/C) |
| YOLOv9 | YOLOv9c-Seg | Second-largest (L/C) |
| YOLOv8 | YOLOv8l-Seg | Second-largest (L/C) |

## สถานะการทดลอง

COMPLETE / PASS WITH WARNINGS — ครบ 4/4 โมเดล โมเดลละ 2,862 เฟรมและ Person GT รายเฟรม 26,894 instances
รอบทดลอง: `benchmark-20261001T0352Z` ใช้ผลที่บันทึกไว้ ไม่มีการรัน inference ใหม่เพื่อปรับเอกสาร

## ผลลัพธ์หลัก

| โมเดล | Mask mAP50-95 | Recall | F1 | Inference (ms) | Pipeline (ms) | FPS | Peak allocated VRAM (MiB) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| YOLO26l-Seg | 0.586237 | 0.834387 | 0.882145 | 36.266 | 76.403 | 13.089 | 777.52 |
| YOLO11l-Seg | 0.528228 | 0.809772 | 0.866424 | 35.387 | 76.810 | 13.019 | 794.47 |
| YOLOv9c-Seg | 0.517646 | 0.802930 | 0.856956 | 35.293 | 76.921 | 13.000 | 838.49 |
| YOLOv8l-Seg | 0.520145 | 0.809400 | 0.856502 | 40.090 | 83.558 | 11.968 | 855.27 |

## เอกสารประกอบ

- [บทสรุปเชิงตัวเลข](RESULTS_SUMMARY_TH.md)
- [การวิเคราะห์ภาพและพฤติกรรมเชิงคุณภาพ](PRESENTATION_SUMMARY_TH.md)
- [รายงานเทคนิค](REPORT.md)
- [โพรโทคอลการทดลอง](EXPERIMENT_PROTOCOL.md)

## การนำทางในชุดการศึกษา

[Largest (X/E)](https://github.com/folklazy/YOLO_Large_Seg_MOTS20_Benchmark) | [Second-largest (L/C)](https://github.com/folklazy/YOLO_Second_Largest_Seg_MOTS20_Benchmark) | [Medium (M)](https://github.com/folklazy/YOLO_Medium_Seg_MOTS20_Benchmark) | [Small (S)](https://github.com/folklazy/YOLO_Small_Seg_MOTS20_Benchmark) | [Nano (N)](https://github.com/folklazy/YOLO_Nano_Seg_MOTS20_Benchmark) | [การศึกษาหลัก](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study)

## หลักฐานสำหรับตรวจสอบซ้ำ

[ค่าตัวชี้วัด](metrics/) · [การตั้งค่า](configs/) · [หลักฐานและแหล่งที่มา](manifests/) · [ภาพและกราฟ](outputs/) · [บันทึกย้อนหลัง](reports/archive/)

[บทตีความจากรอบเดิม](BENCHMARK_INSIGHTS_TH.md) เป็นบันทึกย้อนหลัง เก็บภาษาตามต้นฉบับ; บทสรุปปัจจุบันใช้เอกสารด้านบน
