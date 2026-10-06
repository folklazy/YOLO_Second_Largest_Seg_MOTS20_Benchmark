# Second-largest (L/C) — Visual and Qualitative Analysis

## 1. ภาพรวมผลการทดลอง

Tier นี้เสร็จครบ 4 โมเดลบน MOTS20 ด้วย pretrained / no fine-tuning; คงสถานะ PASS WITH WARNINGS
เอกสารนี้อ่านพฤติกรรมจาก prediction จริง ส่วนผลเชิงตัวเลขและ trade-off เต็มอยู่ที่ [RESULTS_SUMMARY_TH.md](RESULTS_SUMMARY_TH.md)

| Model | Mask mAP50-95 | AP75 | Recall |
|---|---|---|---|
| YOLO26l-Seg | 0.586237 | 0.643537 | 0.834387 |
| YOLO11l-Seg | 0.528228 | 0.565728 | 0.809772 |
| YOLOv9c-Seg | 0.517646 | 0.559180 | 0.802930 |
| YOLOv8l-Seg | 0.520145 | 0.558149 | 0.809400 |

## การเลือกกรณีและการอ่านภาพ

คัด 4 กรณีจาก 12 เฟรมใน frozen visualization manifest โดยอ่าน per-frame TP/FP/FN และตรวจ original/GT กับ saved masks เลือก 1 shared anchor (Case 2: MOTS20-09 / 000263) และอีก 3 diagnostic cases ตามพฤติกรรมของ tier นี้ มีทั้งข้อได้เปรียบ ข้อผิดพลาดร่วม กรณีสวนอันดับ และ near-tie/ผลคล้ายกันเพื่อลด cherry-picking ไม่ใช่การสุ่มตัวแทน dataset
ภายในแต่ละ case ต้องใช้เฟรมเดียวกันครบทุกโมเดล ส่วนระหว่าง tier ใช้ภาพร่วมเมื่อมีเหตุผลในการเทียบ error เดียวกัน ไม่บังคับใช้ชุดภาพเหมือนกันทั้งหมด แต่ละ tier มี 4 cases; ชุดใหม่รวม 10 original frames ต่างกันจากเดิม 6 และเพิ่มฉาก MOTS20-11 ข้อมูลที่ซ้ำข้าม tier ไม่ใช่ตัวอย่างอิสระเพิ่ม
[CASE_SELECTION.md](outputs/visualizations/qualitative/selection_v2/CASE_SELECTION.md) บันทึกเหตุผลและแหล่งหลักฐาน
ภาพเดิมมี contact sheet แยกโมเดล จึงสร้าง comparison จาก lossless saved RLE และ original/GT โดยไม่ inference
แถวแรกเป็น Original/GT; แถวถัดมาเรียง YOLO26, YOLO11, YOLOv9, YOLOv8;
ซ้ายเป็น prediction ขวาเป็น unmatched overlay ทั้งหมดใช้ภาพเต็มเฟรมเดียวกันและ scale เท่ากัน
สีของ matched mask ผูกกับ GT ID เดียวกัน; สีส้ม FN, สีแดง FP, สีเทา IGN (ignored prediction)
ใช้ confidence ≥0.25, mask matching IoU ≥0.50 และ ignore policy เดิม
FN หมายถึง GT ที่ไม่มีคู่ผ่านเกณฑ์ อาจมาจาก mask ไม่ผ่าน IoU ไม่ใช่ไม่มี detection เสมอ;
FP หมายถึง prediction ที่ไม่ match valid GT และไม่ถูก ignore จึงไม่จำเป็นต้องเป็นคนที่ไม่มีอยู่จริง
GT panel แสดงเฉพาะ Person; IGN ไม่ถูกนับเป็น FP ตัวเลขรายเฟรมตรวจตรงกับ CSV เดิม

### Case เหล่านี้ช่วยตัดสินใจอย่างไร

ชุดนี้ใช้ประกอบการเลือกด้านความครบถ้วนของ instance และ unmatched output โดยอ่านร่วมกับ canonical metrics ไม่ได้ให้ผู้ชนะทุกภาพหรือใช้วัด latency/VRAM Case 2 เป็นเฟรมร่วมเพื่อเทียบข้อจำกัดบน source เดียวกัน อีก 3 cases เลือกตามพฤติกรรมของ tier; หากเฟรม diagnostic ตรงกับ tier อื่น เหตุผลต้องอยู่ใน CASE_SELECTION.md และไม่นับเป็นหลักฐานอิสระเพิ่ม 4 cases ไม่แทน 2,862 เฟรม

| Case | Pain point / บทบาท | ใช้ประกอบการเลือกด้านใด |
|---|---|---|
| 1 | จำแนกโมเดล: GT 2002 เล็กและ FN ของ GT 2054 | เป็นหลักฐานเฉพาะเฟรมที่ YOLO26l เก็บ GT 2002 ได้ แต่อีกสามโมเดลไม่ผ่าน matching; ใช้ประกอบเมื่อ instance เล็กสำคัญ |
| 2 | ข้อจำกัดร่วม: FN/FP ในกลุ่มคนกลางภาพ | ใช้เห็นข้อจำกัดร่วมก่อนเชื่ออันดับ mAP และตรวจว่าข้อผิดพลาดประเภทนี้ยอมรับได้หรือไม่ |
| 3 | สวนอันดับ / ต่าง GT: TP เท่ากันแต่พลาดคนคนละ ID | ใช้เทียบ YOLO26l/YOLO11l ที่ counts เท่ากันแต่พลาดคนต่างชุด และตรวจคู่ใกล้ YOLOv9c/YOLOv8l ซึ่งมี trade-off TP/FP ต่างกัน |
| 4 | nearby-mAP / counterexample: GT 2016 พื้นที่เล็กทางขวาหลังราว | ใช้พิจารณาความครบถ้วนของคนพื้นที่เล็ก: YOLO26l/YOLOv9c match GT 2016 ได้ ส่วน YOLO11l/YOLOv8l ไม่ผ่าน; YOLOv9c จึงเก็บได้มากกว่า YOLOv8l ในเฟรมนี้ |

ภาพขยายเป็น ROI เพิ่มเติมจาก original frames และ saved masks แถวแรก Original/GT ต่อด้วยโมเดลตามลำดับเดิม แต่ละคอลัมน์ใช้พิกัด/scale เดียวกันทุกโมเดล แถว Original/GT ใช้เส้นขาวแสดง valid GT; ในแถวโมเดลเส้นขาวคือ GT ที่ match เส้นส้มคือ FN; สีแดงคือ FP สีเทาคือ ignored prediction พิกัด ROI อยู่บนภาพ ภาพเต็มยังแสดงไว้เพื่อไม่ซ่อน error นอก ROI การขยายไม่เพิ่มรายละเอียดจากต้นฉบับ
ค่าราย GT ด้านล่างเป็น diagnostic ของ saved predictions ที่ confidence ≥0.25: TP ใช้ IoU ของคู่ที่ evaluator จับจริง; FN แสดง IoU สูงสุดของ candidate ที่มี ไม่ใช่ AP และไม่เปลี่ยน benchmark ตัวเลข TP/FP/FN ในคำอธิบายเป็นของเต็มเฟรม ไม่ใช่จำนวนใน ROI

## Case 1 — ความต่างที่ Person ขนาดเล็กกลางภาพ

เหตุผลที่เลือก: ตรวจการเก็บ instance เพิ่มของ accuracy leader พร้อมเห็นข้อผิดพลาดที่ยังมีร่วมกัน · MOTS20-05 / 000419

### ภาพเปรียบเทียบ

![Case 1 MOTS20-05 frame 419](outputs/visualizations/qualitative/case_01_comparison.png)

ภาพขยายจุดที่ต้องตรวจ (ใช้คู่กับภาพเต็มด้านบน):

![Case 1 focus — identical region across models](outputs/visualizations/qualitative/case_01_focus.png)

### สิ่งที่เห็นจากภาพ

- YOLO26l เก็บ GT 2002 ซึ่งเป็น Person ขนาดเล็กกลางภาพได้; YOLO11l, YOLOv9c และ YOLOv8l มี FN 2002
- ทั้งสี่โมเดลมี FN 2054 ตรงช่วงขาริมขวา; YOLO11l มี mask แดง FP เพิ่มตรงบริเวณแขน/ถุงของคนใหญ่ริมขวา


ตรวจ matching ราย GT จาก saved masks:

| GT | YOLO26l-Seg | YOLO11l-Seg | YOLOv9c-Seg | YOLOv8l-Seg |
|---|---|---|---|---|
| 2002 | TP IoU 0.619 | FN; best IoU 0.127 | FN; best IoU 0.047 | FN; best IoU 0.150 |
| 2054 | FN; best IoU 0.000 | FN; best IoU 0.076 | FN; best IoU 0.000 | FN; best IoU 0.000 |

IoU 0.000 คือค่าที่ปัดสามตำแหน่ง ไม่ยืนยันว่าไม่มี prediction; candidate อาจมีพื้นที่ทับ GT ต่ำหรือมีคู่กับ GT อื่นแล้ว FN จึงต้องอ่านร่วมกับภาพและ full-frame matching

### วิเคราะห์

ความต่างอยู่ที่การแยก instance ขนาดเล็กกลางภาพ ขณะที่คนใหญ่และคู่กลางภาพดูคล้ายกัน การเก็บเพิ่มหนึ่งคนอาจช่วย Recall แต่ FP ริมขวาของ YOLO11 แสดงว่าจำนวน mask มากขึ้นไม่ได้หมายถึงผลดีขึ้นเสมอ FN 2054 มีพื้นที่ GT ที่มองเห็นน้อยตรงขาของคนริมขวา ตัวอย่างนี้ชี้ให้ดูบริเวณเฉพาะ instance แทนตัดสินจากคนใหญ่เพียงอย่างเดียว โดยไม่จัดระดับความรุนแรงของ occlusion

### เชื่อมกับผลเชิงตัวเลข

การเก็บ GT 2002 ของ YOLO26l สอดคล้องในทิศทางกับ Recall รวม 0.834387 ที่สูงกว่า YOLOv8l (0.809400) แต่เฟรมเดียวไม่อธิบายช่องว่าง Recall ทั้ง dataset


### ใช้ประกอบการเลือกอย่างไร

**Pain point / บทบาท:** จำแนกโมเดล — GT 2002 เล็กและ FN ของ GT 2054

**ใช้ประกอบการเลือก:** เป็นหลักฐานเฉพาะเฟรมที่ YOLO26l เก็บ GT 2002 ได้ แต่อีกสามโมเดลไม่ผ่าน matching; ใช้ประกอบเมื่อ instance เล็กสำคัญ

**ขอบเขตหลักฐาน:** ทุกโมเดลยังพลาด GT 2054 และ YOLO11l มี FP เพิ่มริมขวา ไม่ใช้ชนะทุกสภาพภาพ

## Case 2 — พลาดร่วมกันในกลุ่มคนซ้อนกัน

เหตุผลที่เลือก: shared anchor ของทั้งห้า tier เพื่อเทียบข้อผิดพลาดบน source frame เดียวกัน;  แสดงข้อจำกัดร่วมและ FP ของทุกโมเดล แทนเลือกแต่ภาพที่ตัวนำได้เปรียบ · MOTS20-09 / 000263

### ภาพเปรียบเทียบ

![Case 2 MOTS20-09 frame 263](outputs/visualizations/qualitative/case_02_comparison.png)

ภาพขยายจุดที่ต้องตรวจ (ใช้คู่กับภาพเต็มด้านบน):

![Case 2 focus — identical region across models](outputs/visualizations/qualitative/case_02_focus.png)

### สิ่งที่เห็นจากภาพ

- ทุกโมเดลมี FN ของ GT 2001/2002/2011 ในกลุ่มคนกลางภาพ และ 2023 ริมขวา; GT บางส่วนอยู่หลังคนอื่นและมองเห็นเป็นพื้นที่เล็ก
- ทุกโมเดลมี FP แดงบริเวณคนกลางภาพ ถึงแม้หลายคนด้านหน้าจะมี matched mask แล้ว
- YOLO26l และ YOLO11l เก็บได้ 9 instances; YOLOv8l และ YOLOv9c เก็บได้ 8 instances แต่ทั้งหมดก็ยังมี FN หลายตำแหน่ง


ตรวจ matching ราย GT จาก saved masks:

| GT | YOLO26l-Seg | YOLO11l-Seg | YOLOv9c-Seg | YOLOv8l-Seg |
|---|---|---|---|---|
| 2001 | FN; best IoU 0.243 | FN; best IoU 0.253 | FN; best IoU 0.252 | FN; best IoU 0.236 |
| 2002 | FN; best IoU 0.010 | FN; best IoU 0.009 | FN; best IoU 0.013 | FN; best IoU 0.010 |
| 2007 | TP IoU 0.631 | TP IoU 0.557 | FN; best IoU 0.050 | FN; best IoU 0.052 |
| 2011 | FN; best IoU 0.366 | FN; best IoU 0.373 | FN; best IoU 0.387 | FN; best IoU 0.368 |

IoU 0.000 คือค่าที่ปัดสามตำแหน่ง ไม่ยืนยันว่าไม่มี prediction; candidate อาจมีพื้นที่ทับ GT ต่ำหรือมีคู่กับ GT อื่นแล้ว FN จึงต้องอ่านร่วมกับภาพและ full-frame matching

### วิเคราะห์

ส่วนที่พลาดไม่ได้มีเฉพาะคนไกล แต่รวมพื้นที่ GT เล็กในกลุ่มคนที่ซ้อนกันด้วย FP บาง mask อยู่บนคนจริงที่ไม่ match ตามเกณฑ์ จึงควรอ่านว่า segmentation/matching error ก่อนเรียกว่า hallucinated person จำนวนคนที่เก็บได้เพิ่มยังเกิดพร้อม FP ได้ ภาพนี้ไม่พิสูจน์สาเหตุของ error หรือความทนทานต่อ occlusion ของทั้ง dataset

### เชื่อมกับผลเชิงตัวเลข

แม้ YOLO26l มี mAP/AP75 รวมสูงสุด ก็ยังเกิด FN และ FP ในกรณีนี้; ภาพช่วยเห็นข้อจำกัดที่คะแนนเฉลี่ยไม่แสดง การสรุปจำนวน FN/FP ทั้ง dataset ต้องอ่าน canonical CSV ไม่คูณจากกรณีนี้


### ใช้ประกอบการเลือกอย่างไร

**Pain point / บทบาท:** ข้อจำกัดร่วม — FN/FP ในกลุ่มคนกลางภาพ

**ใช้ประกอบการเลือก:** ใช้เห็นข้อจำกัดร่วมก่อนเชื่ออันดับ mAP และตรวจว่าข้อผิดพลาดประเภทนี้ยอมรับได้หรือไม่

**ขอบเขตหลักฐาน:** TP มากกว่าไม่ได้แปลว่าไม่มี FP หรือว่า segmentation ของทุกคนดีกว่า

## Case 3 — กรณีสวนอันดับและ trade-off ของ detection

เหตุผลที่เลือก: รวมตัวอย่างที่ accuracy leader ไม่ได้เก็บ Person มากที่สุด · MOTS20-02 / 000001

### ภาพเปรียบเทียบ

![Case 3 detection trade-off](outputs/visualizations/qualitative/case_03_comparison.png)

ภาพขยายจุดที่ต้องตรวจ (ใช้คู่กับภาพเต็มด้านบน):

![Case 3 focus — identical region across models](outputs/visualizations/qualitative/case_03_focus.png)

### สิ่งที่เห็นจากภาพ

- YOLOv8l match ได้ 10 instances มากกว่า YOLO26l/YOLO11l ที่ได้ 9 และ YOLOv9c ที่ได้ 8 แต่มี FP 2 masks กลางฉากและบริเวณวัตถุใต้ร่มริมขวา
- YOLO26l และ YOLO11l มี FN เท่ากัน 3 แต่คนที่พลาดต่างกัน: YOLO26l พลาด 2020/2023 ในกลุ่มซ้าย ขณะที่ YOLO11l พลาด 2026 ทางซ้ายและ 2017 กลางภาพ; ทั้งคู่พลาด 2031


ตรวจ matching ราย GT จาก saved masks:

| GT | YOLO26l-Seg | YOLO11l-Seg | YOLOv9c-Seg | YOLOv8l-Seg |
|---|---|---|---|---|
| 2017 | TP IoU 0.502 | FN; best IoU 0.000 | FN; best IoU 0.000 | FN; best IoU 0.495 |
| 2020 | FN; best IoU 0.021 | TP IoU 0.552 | FN; best IoU 0.047 | TP IoU 0.599 |
| 2023 | FN; best IoU 0.067 | TP IoU 0.647 | FN; best IoU 0.086 | TP IoU 0.650 |
| 2026 | TP IoU 0.640 | FN; best IoU 0.000 | TP IoU 0.582 | TP IoU 0.706 |

IoU 0.000 คือค่าที่ปัดสามตำแหน่ง ไม่ยืนยันว่าไม่มี prediction; candidate อาจมีพื้นที่ทับ GT ต่ำหรือมีคู่กับ GT อื่นแล้ว FN จึงต้องอ่านร่วมกับภาพและ full-frame matching

### วิเคราะห์

YOLOv8l เก็บได้มากกว่าแต่แลกกับ FP; YOLO26l/YOLO11l มี TP/FP/FN เท่ากันแต่พลาดคนคนละตำแหน่ง สรุปคุณภาพจากจำนวนรวมเพียงอย่างเดียวจึงซ่อนความต่างของ error behavior ไม่มีการเปลี่ยน confidence ให้โมเดลใดเป็นพิเศษ และบริเวณ FP ริมขวายังคงแสดงเต็มภาพ ไม่ crop เพื่อซ่อน error

### เชื่อมกับผลเชิงตัวเลข

YOLO26l มี Recall รวมสูงสุด 0.834387 แต่ไม่ได้มี TP สูงสุดทุกเฟรม; AP75 ใช้ mask IoU 0.75 และ confidence ranking จึงไม่แทนด้วย TP ที่ IoU 0.50 ของเฟรมนี้ ความต่างของ matched-mask IoU ใช้เฉพาะคู่ที่ผ่าน matching และไม่รวมคนที่พลาด


### ใช้ประกอบการเลือกอย่างไร

**Pain point / บทบาท:** สวนอันดับ / ต่าง GT — TP เท่ากันแต่พลาดคนคนละ ID

**ใช้ประกอบการเลือก:** ใช้เทียบ YOLO26l/YOLO11l ที่ counts เท่ากันแต่พลาดคนต่างชุด และตรวจคู่ใกล้ YOLOv9c/YOLOv8l ซึ่งมี trade-off TP/FP ต่างกัน

**ขอบเขตหลักฐาน:** GT 2017 มี prediction ของ YOLOv8l ที่ใกล้เกณฑ์ matching; ไม่ควรอ่าน FN ว่าไม่มี detection ทุกครั้ง

## Case 4 — คนหลังราวที่คู่ mAP ใกล้กันเก็บได้ต่างกัน

เหตุผลที่เลือก: ตรวจคู่ YOLOv9c/YOLOv8l ในฉากที่ไม่ได้ปรากฏในชุดเดิม และมีข้อผิดพลาดร่วมไว้เทียบ · MOTS20-11 / 000001

### ภาพเปรียบเทียบ

![Case 4 Second_Largest MOTS20-11 frame 1](outputs/visualizations/qualitative/selection_v2/case_04_comparison.png)

ภาพขยายจุดที่ต้องตรวจ (ใช้คู่กับภาพเต็มด้านบน):

![Case 4 focus — identical region across models](outputs/visualizations/qualitative/selection_v2/case_04_focus.png)

### สิ่งที่เห็นจากภาพ

- GT 2016 เป็นพื้นที่ Person เล็กที่มองเห็นเหนือราวด้านขวา; YOLO26l/YOLOv9c match ได้ แต่ YOLO11l/YOLOv8l มี FN
- ทุกโมเดลมี FN ของ GT 2013/2015/2029 หลังราวและ GT 2079 ด้านหลังคนกลางภาพ; ROI ขวาแสดง 2013/2079 ที่ยังไม่ผ่าน matching
- YOLO26l/YOLO11l/YOLOv9c/YOLOv8l มี TP 10/9/10/9 และ FN 4/5/4/5; ไม่มี FP ในทั้งสี่โมเดล คนใหญ่ด้านหน้าถูกเก็บในหลายโมเดล

ตรวจ matching ราย GT จาก saved masks:

| GT | YOLO26l-Seg | YOLO11l-Seg | YOLOv9c-Seg | YOLOv8l-Seg |
|---|---|---|---|---|
| 2013 | FN; best IoU 0.000 | FN; best IoU 0.000 | FN; best IoU 0.000 | FN; best IoU 0.000 |
| 2016 | TP IoU 0.665 | FN; best IoU 0.000 | TP IoU 0.559 | FN; best IoU 0.000 |
| 2079 | FN; best IoU 0.005 | FN; best IoU 0.009 | FN; best IoU 0.012 | FN; best IoU 0.012 |

IoU ที่ปัดเป็น 0.000 ไม่ยืนยันว่าไม่มี prediction; FN หมายถึงไม่มีคู่ผ่าน evaluator ตาม policy เดิม

### วิเคราะห์

คนใหญ่ในภาพเต็มทำให้ผลดูใกล้กัน แต่ ROI ที่ราวแสดง instance-level difference ซึ่งเปลี่ยนความครบถ้วนได้จริง GT 2016 ของ YOLOv9c มี matched IoU 0.559 เทียบกับ YOLO26l 0.665; เป็นการเทียบคนเดียวกัน ไม่ใช่ mean ของคนคนละชุด อีก ROI แสดงข้อจำกัดร่วมเพื่อไม่ให้กรณีนี้ถูกอ่านเป็นชัยชนะต่อทุกคนตัวเล็ก

### เชื่อมกับผลเชิงตัวเลข

YOLOv9c/YOLOv8l มี mAP 0.517646/0.520145 ค่อนข้างใกล้กัน แม้ YOLOv8l มี Recall รวมสูงกว่า เฟรมนี้ YOLOv9c กลับ match มากกว่าหนึ่ง GT กรณีนี้ร่วมกับ Case 3 จึงแสดง error trade-off คนละทิศทาง ไม่ใช่หลักฐานว่าคู่ใดเหนือกว่าทุกเฟรม

### ใช้ประกอบการเลือกอย่างไร

**Pain point / บทบาท:** nearby-mAP / counterexample — GT 2016 พื้นที่เล็กทางขวาหลังราว

**ใช้ประกอบการเลือก:** ใช้พิจารณาความครบถ้วนของคนพื้นที่เล็ก: YOLO26l/YOLOv9c match GT 2016 ได้ ส่วน YOLO11l/YOLOv8l ไม่ผ่าน; YOLOv9c จึงเก็บได้มากกว่า YOLOv8l ในเฟรมนี้

**ขอบเขตหลักฐาน:** Recall รวมของ YOLOv9c ต่ำกว่า YOLOv8l แม้เฟรมนี้มี TP มากกว่า; ไม่จัดอันดับ dataset ใหม่จาก GT เดียว และทุกโมเดลยังมี FN ร่วม

## Failure Analysis

| Failure pattern | Models observed | Visual case | Interpretation |
|---|---|---|---|
| Person พื้นที่เล็กไม่มีคู่ผ่านเกณฑ์ | ทุกโมเดล (2054); YOLO11l/YOLOv9c/YOLOv8l (2002) | Case 1 | ข้อผิดพลาดต่าง GT ต้องดู coverage ร่วมกับ matching |
| Unmatched GT ในกลุ่มคน | ทุกโมเดล | Case 2 | ข้อจำกัดร่วม ไม่อนุมานความถี่หรือสาเหตุ |
| คนพื้นที่เล็กหลังราวไม่ผ่าน matching | YOLO11l/YOLOv8l (2016); ทุกโมเดล (2013/2079) | Case 4 | ความต่างของ GT 2016 ไม่ชดเชย FN ร่วมทั้งหมด |
| Unmatched outputs / extra masks | ทุกโมเดลใน Case 2; YOLOv8l ใน Case 3 | Case 2/3 | พิจารณา TP/FP ร่วมกัน; ไม่ใช่คนที่ไม่มีจริงโดยอัตโนมัติ |

เป็นประเภท error ที่พบในกรณีที่เลือก ไม่ใช่อัตราหรือความถี่ทั้ง dataset ไม่ระบุ merging/fragmentation/boundary leakage หากไม่มีหลักฐานพอ

## Near-tie visual check

YOLOv9c/YOLOv8l มี mAP 0.517646/0.520145 ค่อนข้างใกล้กัน Case 3 YOLOv8l เก็บได้มากกว่าแต่มี FP เพิ่ม ขณะที่ Case 4 YOLOv9c เก็บ GT 2016 เพิ่มได้โดยไม่มี FP ทั้งคู่ ภาพจึงแสดง error trade-off คนละทิศทาง แม้ Recall รวมของ YOLOv8l สูงกว่า ไม่มีฐานให้ประกาศความเหนือกว่าทุกเฟรมหรือ statistical superiority; inference YOLOv9c/YOLO11l ต่าง 0.094 ms ตาม benchmark ซึ่งภาพใช้ยืนยันไม่ได้

## สิ่งที่เรียนรู้จากภาพจริง

### Observation 1

Case 1 คนใหญ่ถูกเก็บในทุกโมเดล แต่ GT 2002 เป็นจุดที่ผลต่างกัน

**Interpretation:** การดูเฉพาะ Person ใหญ่ด้านหน้าอาจซ่อน instance-level error; ต้องตรวจ GT ของคนเล็กด้วย ไม่ใช่ข้อสรุป robustness ทุก scale

### Observation 2

Case 2 ทุกโมเดลพลาด GT ในกลุ่มคนกลางภาพ และมี unmatched prediction บนคนจริง

**Interpretation:** การแบ่ง instance และการผ่าน mask IoU เป็นคนละเรื่องกับแค่เห็นว่ามีคน; FP/FN จึงควรอ่านคู่กับ GT และ ignore policy

### Observation 3

Case 3 มีโมเดลอื่นเก็บ valid Person มากกว่า accuracy leader และ YOLO26/YOLO11 พลาดคนคนละชุด

**Interpretation:** อันดับรวมไม่ใช่คำรับรองทุกเฟรม; คะแนนหรือ counts ที่ใกล้กันอาจเกิดจาก error ต่างตำแหน่ง

### Observation 4

Case 4 YOLO26l/YOLOv9c match GT 2016 ได้ แต่ YOLO11l/YOLOv8l พลาด; ทุกโมเดลยังพลาด 2013/2079

**Interpretation:** กรณีนี้แยกพฤติกรรมราย GT ของคู่คะแนนใกล้ และเป็นข้อยกเว้นต่ออันดับ Recall รวม ไม่ใช่ผู้ชนะทุกคนพื้นที่เล็ก

## เมื่อดูทั้งตัวเลขและภาพร่วมกัน

YOLO26l นำ mAP/AP75/Recall รวม ส่วนภาพช่วยตรวจว่าความต่างอยู่ที่ GT ใดและมี output เพิ่มแบบไหน Case 1 แสดง instance ที่เก็บเพิ่ม แต่ Case 2 ยังมีข้อผิดพลาดร่วม และ Case 3 เป็นกรณีสวนอันดับ coverage Case 4 แยก GT 2016 ของคู่ mAP ใกล้กัน พร้อมข้อจำกัดร่วม จึงไม่ใช้ภาพใดภาพหนึ่งอธิบายคะแนนทั้ง dataset AP75 รวม confidence ranking และ stricter IoU ซึ่งภาพที่ confidence 0.25/matching 0.50 แสดงไม่ครบ; TP-only quality อาจใช้ GT คนละชุด

Latency และ VRAM เป็น system-level measurements อ่านจาก benchmark แยกจากภาพ segmentation ไม่สามารถอนุมานสาเหตุหรือวัดสองค่านี้จาก mask

## ถ้าพิจารณาทั้งผลเชิงตัวเลขและภาพ

| Priority | Candidate | Evidence |
|---|---|---|
| Accuracy | YOLO26l-Seg | mAP/AP75/Recall รวมสูงสุด; Case 1 แสดง GT ที่เก็บเพิ่ม; Case 2/3/4 ช่วยตรวจข้อจำกัดและ error trade-off |
| Speed | YOLOv9c-Seg (inference); YOLO26l-Seg (pipeline) | Clean timing benchmark; ภาพไม่วัดเวลา |
| Low VRAM | YOLO26l-Seg | Peak allocated VRAM benchmark; ภาพไม่วัด memory |
| Balanced | YOLO26l-Seg หากยอมรับ inference 36.266 ms | Accuracy/pipeline/VRAM นำพร้อมกัน แต่ inference ไม่เร็วสุด; Case 3 ยังมีโมเดลเก็บคนได้มากกว่า |

เป็น candidate สำหรับ cross-tier และ CCTV robustness evaluation ภายหลัง ไม่มี weighted score หรือข้อยืนยัน final CCTV superiority

## ข้อจำกัด

- เฟรมที่เลือกเป็นตัวอย่างเชิงคุณภาพจาก 12 เฟรมเดิม ไม่แทน dataset-level metrics และไม่ใช่ representative sample
- มีทั้งข้อได้เปรียบ ข้อผิดพลาด กรณีสวนอันดับ และผลคล้ายกันเพื่อลด cherry-picking; ยังอาจพลาด error ชนิดอื่นนอก selection pool
- MOTS20 ไม่ใช่ผลทดสอบ CCTV robustness ขั้นสุดท้าย; ไม่อนุมาน blur/low-light/มุมกล้องหรือระดับ occlusion
- Qualitative observations และ numerical near ties ไม่ใช่ statistical significance
- ภาพย่อ/overlay อาจบังรายละเอียดขอบ; ตรวจ saved RLE หากต้องการตรวจพิกเซล ไม่อธิบายสาเหตุจาก architecture

## รายละเอียดเต็ม

[Quantitative summary](RESULTS_SUMMARY_TH.md) · [REPORT.md](REPORT.md) · [TIER_RESULTS.csv](metrics/TIER_RESULTS.csv) ·
[Case evidence](outputs/visualizations/qualitative/selection_v2/CASE_EVIDENCE.json) ·
[Master Study](https://github.com/folklazy/YOLO_Instance_Segmentation_MOTS20_Scaling_Study)
