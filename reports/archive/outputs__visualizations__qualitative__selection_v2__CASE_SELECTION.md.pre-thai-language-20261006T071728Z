# Second_Largest — qualitative case selection v2

คัดจาก 12 frozen visualization frames โดยตรวจ per-frame metrics, original/GT และ saved RLE ที่ confidence ≥0.25 / mask matching IoU ≥0.50 ตาม evaluator/ignore policy เดิม ไม่รัน inference

1 shared anchor + 3 cases ตามพฤติกรรมของ tier ไม่บังคับภาพทั้งหมดตรงกันระหว่าง tier; ภายใน case ใช้เฟรมเต็มเดียวกันทุกโมเดล ROI เป็นภาพเสริม ไม่ซ่อน full-frame errors

| Case | Sequence / frame | Why selected / decision use | Source comparison |
|---|---|---|---|
| 1 | MOTS20-05 / 000419 | tier diagnostic: small GT recovered by accuracy leader; เป็นหลักฐานเฉพาะเฟรมที่ YOLO26l เก็บ GT 2002 ได้ แต่อีกสามโมเดลไม่ผ่าน matching; ใช้ประกอบเมื่อ instance เล็กสำคัญ | reuse existing image |
| 2 | MOTS20-09 / 000263 | shared anchor: common failure; ใช้เห็นข้อจำกัดร่วมก่อนเชื่ออันดับ mAP และตรวจว่าข้อผิดพลาดประเภทนี้ยอมรับได้หรือไม่ | reuse existing image |
| 3 | MOTS20-02 / 000001 | counterexample: equal counts, different GT and TP/FP trade-off; ใช้เทียบ YOLO26l/YOLO11l ที่ counts เท่ากันแต่พลาดคนต่างชุด และตรวจคู่ใกล้ YOLOv9c/YOLOv8l ซึ่งมี trade-off TP/FP ต่างกัน | reuse existing image |
| 4 | MOTS20-11 / 000001 | nearby-mAP pair: extra matched GT despite lower aggregate Recall; ใช้พิจารณาความครบถ้วนของคนพื้นที่เล็ก: YOLO26l/YOLOv9c match GT 2016 ได้ ส่วน YOLO11l/YOLOv8l ไม่ผ่าน; YOLOv9c จึงเก็บได้มากกว่า YOLOv8l ในเฟรมนี้ | new composite from saved predictions |

## ทำไมบางภาพยังตรงกับ tier อื่น

Case 2 (09/263) ใช้ร่วมเพื่อเทียบ FN/FP บน GT ชุดเดียวกัน กรณีอื่นซ้ำได้เมื่อ error เดียวกันช่วยตรวจคนละโมเดล: 05/419 ใช้ L/M ตรวจ GT 2002; 02/1 ใช้ L/M ตรวจ equal counts และ GT ต่างชุด; 02/600 ใช้ Largest/Small ตรวจกรณีสวนอันดับ; 02/300 ใช้ Small/Nano ตรวจ TP–FP trade-off; 11/1 ใช้ L/N แต่ L ตรวจ GT 2016 ส่วน N ตรวจ GT 2028 และ extra mask; 11/450 ใช้ Largest/Medium ตรวจ coverage เท่ากันกับ extra output ของคนละชุดโมเดล ไม่ใช้จำนวนภาพซ้ำเป็นหลักฐานอิสระเพิ่ม

## การแทน case เดิม

เดิม Case 4 (09/1) TP 6 / FP 0 / FN 0 ทุกโมเดล; 11/1 แยก GT 2016 ของคู่ mAP ใกล้กันและคง FN ร่วมไว้ ภาพ/หลักฐานเก่ายังคงเดิมเพื่อ audit; presentation เก่าเก็บใน reports/archive

## ขอบเขต

ทั้งห้า tier มี 20 case slots แต่ใช้ original frames ต่างกัน 10 เฟรม (เดิม 6) ชุดใหม่มี MOTS20-11 และยังมี common failure / counterexample ไม่เลือกเฉพาะ frame ที่ accuracy leader ชนะ ทั้งนี้ pool 12 เฟรมไม่แทน dataset; ไม่อ้างว่าเป็นเฟรมที่ต่างที่สุดใน 2,862 เฟรม ไม่ใช้ภาพวัด latency/VRAM หรือ statistical significance

[Candidate pool](CANDIDATE_POOL.json) · [Case evidence](CASE_EVIDENCE.json) · [Focus evidence](FOCUS_EVIDENCE.json) · [Decision audit](CASE_DECISION_AUDIT.json) · [Active selection](../../../../manifests/QUALITATIVE_SELECTION.json)
