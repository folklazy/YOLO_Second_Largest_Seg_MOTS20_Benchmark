# Largest available YOLO segmentation variants on MOTS20

Run: `benchmark-20260929T0520Z` • **PASS WITH WARNINGS** • completed 2026-09-29T07:46:00.818452+00:00

## 1. ทดสอบอะไร
เปรียบเทียบ pretrained YOLO26x-Seg, YOLO11x-Seg, YOLOv9e-Seg และ YOLOv8x-Seg
กับ Person instance segmentation บน MOTS20 train ครบ 2,862 ภาพ (26,894 GT instances)
โดยไม่ฝึกเพิ่ม เป็นรุ่น segmentation ใหญ่ที่สุดของแต่ละตระกูล ไม่ใช่โมเดลที่มีจำนวน parameters เท่ากัน

## 2. ใช้เงื่อนไขอะไร
Tesla T4 ตัวเดียว, FP32, batch 1, square letterbox 640×640, NMS IoU 0.70,
confidence floor 0.001 สำหรับ AP และ threshold 0.25 สำหรับ P/R/F1 ใช้ภาพและ evaluator เดียวกัน
YOLO26 ใช้ NMS-based one-to-many เช่นเดียวกับรุ่นอื่น Preflight 100 ภาพเลือก AP maxDet=200
วัดความเร็วแยกจาก accuracy จำนวน 100 ภาพ × 3 รอบต่อโมเดล มี warmup และ CUDA synchronization

## 3. ผลหลักเป็นอย่างไร
**YOLO26x-Seg มี Mask mAP50-95 สูงสุด 0.603730**
ส่วน **YOLOv9e-Seg มี inference เร็วสุด 65.888 ms/ภาพ**
ทุกโมเดลประมวลผลครบและผ่าน consistency checks ผลตัวเลขอยู่ในตารางด้านล่าง

## 4. แต่ละโมเดลเด่นด้านไหน
- Mask accuracy สูงสุด: YOLO26x-Seg
- Recall สูงสุด: YOLO26x-Seg (0.846285)
- Neural inference เร็วสุด: YOLOv9e-Seg; pipeline เร็วสุด: YOLOv9e-Seg
- Peak allocated VRAM ต่ำสุด: YOLOv9e-Seg (855.41 MiB)
- Accuracy–inference-latency Pareto frontier: YOLO26x-Seg, YOLO11x-Seg, YOLOv9e-Seg
ไม่ใช้คะแนนรวมถ่วงน้ำหนัก และไม่สรุปว่ารุ่นเดียวดีที่สุดทุกด้าน

## 5. มีปัญหาหรือข้อจำกัดอะไร
มี CPU NNPACK warning ระหว่างตรวจ model complexity และ pycocotools/NumPy deprecation warning
แต่ regression tests ผ่าน 15 ข้อ เก็บ warnings ไว้ใน logs ไม่เปลี่ยน dependencies
ภาพวิดีโอต่อเนื่องมีความสัมพันธ์กัน โมเดลมีความจุต่างกัน และ IoU/Dice เป็นค่าเฉพาะ TP ที่จับคู่สำเร็จ
Timing ชุดแรกมีบางรอบถูก flag เพราะ GPU ยังไม่ idle จึงตัดชุดแรกออกทั้งหมด
และทำใหม่ครบทุกโมเดล 3 รอบ โดยรอ GPU idle ก่อนเริ่มและคงวิธีวัดเดิม
ตารางหลักใช้เฉพาะชุดใหม่ที่ผ่าน contamination checks ครบ
ผลนี้ **ยังไม่เพียงพอสำหรับข้อสรุป final CCTV robustness**

## 6. ควรทำอะไรต่อ
ใช้ผลเป็น preliminary YOLO segmentation comparison ได้ แล้วออกแบบ CCTV robustness experiment
ที่แยก blur, low-light และ camera-angle อย่างชัดเจน พร้อมภาพ/GT ที่เหมาะสมและ protocol ร่วมกัน
หากต้องการแยกผลของ architecture ควรทำ capacity-controlled comparison เพิ่มต่างหาก

## 1. Research question
How do the largest officially available pretrained segmentation checkpoints from
four YOLO generations generalize to MOTS20 Person masks under a common protocol?
No training, fine-tuning, transfer learning or adaptation was performed.

## 2. Experimental protocol
See [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md). Config hash:
`30a3652ba9f88d020bbf2dc7857c72dbb197c92bd5dfec35665966514df95c24`. Protocol hash: `465a6e60b371b29f250eeb8bb5ac4c218be20f114e9e42f7979e5d45aca19366`.
Inference runs sequentially on CUDA:0. Native-resolution masks use retina_masks;
all actual network tensors are 1×3×640×640. Aspect-preserving centered letterbox
has value-114 padding, RGB FP32 /255. Input is 1920×1080→640×360 plus 140 pixels
top/bottom, or 640×480→640×480 plus 80 pixels top/bottom. NMS is box IoU 0.70;
evaluation matches mask IoU 0.50. These are separate operations.

Valid Person GT is matched first; unmatched predictions are ignored when their
intersection with the union of class-10 masks / prediction area ≥0.50. Fixed
metrics use ≥0.25; AP uses saved NMS candidates >0.001 and common maxDet
200. AP is pooled confidence-ranked frame-level Person mask AP,
not official MOTS tracking evaluation. Matched Dice=2IoU/(1+IoU).

## 3. Dataset description
Only bundled MOTS train GT is used. No test GT, duplicate MOTSLabels, dataset
adaptation, file modification or split creation. All frames and GT RLE decoded;
all image/GT/checkpoint hashes rechecked at completion.
| Sequence | Frames | Resolution W×H | GT Person instances | Ignore regions |
| --- | --- | --- | --- | --- |
| MOTS20-02 | 600 | [1920, 1080] | 7039 | 600 |
| MOTS20-05 | 837 | [640, 480] | 6570 | 802 |
| MOTS20-09 | 525 | [1920, 1080] | 4774 | 525 |
| MOTS20-11 | 900 | [1920, 1080] | 8511 | 900 |

## 4. Model/checkpoint table

| Model | Loaded parameters | Local NMS GFLOPs @640 | Checkpoint MB (decimal) | SHA256 |
| --- | --- | --- | --- | --- |
| YOLO26x-Seg | 70693800 | 338.203341 | 142.129861 | 92b3de0065766a17180d6219858717dc9d03cdce8a3ca9576c97fd75aabb64f3 |
| YOLO11x-Seg | 62142656 | 297.892403 | 125.090821 | 4e53a5f5fd3ee2ae3361c62169c6bb3ed4ae251dd0e57606e230955aa52d919c |
| YOLOv8x-Seg | 71827888 | 329.188813 | 144.101612 | c333d6a7aff884ec821050eacdab29871f3edd10d996cf48746a02f8e01f1b5d |
| YOLOv9e-Seg | 60512800 | 238.332570 | 122.212466 | d7803f5946df2897c1746658bdc46c61c2de1a740ce740804f7099c8abbe660e |

Sources: official Ultralytics assets v8.4.0; exact URLs and full COCO class mapping in checkpoint_manifest.json. Every checkpoint has task=segment and names[0]=person.

## 5. Environment
Hostname `ai-dev-server`; OS `Linux-6.8.0-139-generic-x86_64-with-glibc2.39`; Python 3.12.3;
Ultralytics 8.4.160; PyTorch 2.14.0+cu130;
torchvision 0.29.0+cu130; NumPy 2.5.3;
pycocotools 2.0.11; CUDA runtime 13.0.
Tesla T4, NVIDIA driver 580.178.04, physical VRAM 15,360 MiB;
CUDA-visible device memory approximately 14,911 MiB. CUDA_VISIBLE_DEVICES=None.
No packages changed. Git status/commit unavailable if workspace is not a Git checkout;
captured command return codes and errors are preserved in environment.json.

## 6. Preflight/maxDet validation
25 evenly spaced frames from each sequence, frozen before predictions. All four
models completed the same 100 frames. Strict convergence tolerance is <0.0001
for each AP metric relative to cap 1000. Chosen common cap: **200**.
| Model | maxDet | AP50 | AP75 | mAP50-95 | Converged |
| --- | --- | --- | --- | --- | --- |
| yolo26x-seg.pt | 100 | 0.8914247379931812 | 0.6594682195035353 | 0.5913119168159136 | True |
| yolo26x-seg.pt | 200 | 0.8914247379931812 | 0.6594407508293023 | 0.5913020124122462 | True |
| yolo26x-seg.pt | 300 | 0.8914247379931812 | 0.6594407508293023 | 0.5913020124122462 | True |
| yolo26x-seg.pt | 1000 | 0.8914247379931812 | 0.6594407508293023 | 0.5913020124122462 | True |
| yolo11x-seg.pt | 100 | 0.869726178583301 | 0.5501213194371468 | 0.5222694869076595 | True |
| yolo11x-seg.pt | 200 | 0.8696828727807027 | 0.5501213194371468 | 0.5222573066208922 | True |
| yolo11x-seg.pt | 300 | 0.8696828727807027 | 0.5501213194371468 | 0.5222573066208922 | True |
| yolo11x-seg.pt | 1000 | 0.8696828727807027 | 0.5501213194371468 | 0.5222573066208922 | True |
| yolov8x-seg.pt | 100 | 0.8581125989783609 | 0.5291760591396858 | 0.5113113149963143 | False |
| yolov8x-seg.pt | 200 | 0.8582797059087911 | 0.5291760591396858 | 0.5113197530372843 | True |
| yolov8x-seg.pt | 300 | 0.8582797059087911 | 0.5291760591396858 | 0.5113197530372843 | True |
| yolov8x-seg.pt | 1000 | 0.8582797059087911 | 0.5291760591396858 | 0.5113197530372843 | True |
| yolov9e-seg.pt | 100 | 0.8734699597099348 | 0.5421990971286696 | 0.5198198052789527 | False |
| yolov9e-seg.pt | 200 | 0.8734646402711257 | 0.5421990971286696 | 0.5199842898367218 | True |
| yolov9e-seg.pt | 300 | 0.8734646402711257 | 0.5421990971286696 | 0.5199842898367218 | True |
| yolov9e-seg.pt | 1000 | 0.8734646402711257 | 0.5421990971286696 | 0.5199842898367218 | True |

Full-run post-NMS counts before evaluator capping:

| Model | Min | Max | Mean | Saved predictions |
| --- | --- | --- | --- | --- |
| YOLO26x-Seg | 8 | 164 | 71.368623 | 204249 |
| YOLO11x-Seg | 7 | 156 | 70.044025 | 200368 |
| YOLOv8x-Seg | 8 | 163 | 78.448987 | 224511 |
| YOLOv9e-Seg | 7 | 156 | 72.154088 | 206362 |

## 7. Overall accuracy comparison

| Model | Mask mAP50-95 | AP50 | AP75 | Precision | Recall | F1 | TP-only IoU | TP-only Dice | Inference ms | Pipeline ms | FPS | Peak allocated MiB | Params | Checkpoint MB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YOLO26x-Seg | 0.603730 | 0.903687 | 0.664426 | 0.946008 | 0.846285 | 0.893372 | 0.828873 | 0.902919 | 72.458246 | 109.638635 | 9.120872 | 952.184082 | 70693800 | 142.129861 |
| YOLO11x-Seg | 0.536674 | 0.875806 | 0.575845 | 0.938702 | 0.822228 | 0.876613 | 0.801385 | 0.886046 | 69.406033 | 105.885185 | 9.444192 | 942.478027 | 62142656 | 125.090821 |
| YOLOv9e-Seg | 0.536642 | 0.882037 | 0.572100 | 0.934230 | 0.826578 | 0.877113 | 0.799298 | 0.884605 | 65.887918 | 103.375589 | 9.673464 | 855.407227 | 60512800 | 122.212466 |
| YOLOv8x-Seg | 0.524758 | 0.866402 | 0.560452 | 0.921598 | 0.814271 | 0.864616 | 0.798136 | 0.883841 | 67.842816 | 109.441223 | 9.137325 | 1001.133301 | 71827888 | 144.101612 |

Counts use confidence ≥0.25; AP-floor prediction counts are separate. Micro P/R/F1 derive from pooled counts.

| Model | GT | AP-floor predictions | Fixed-threshold predictions | TP | FP | FN | Ignored |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26x-seg.pt | 26894 | 204249 | 29190 | 22760 | 1299 | 4134 | 5131 |
| yolo11x-seg.pt | 26894 | 200368 | 27376 | 22113 | 1444 | 4781 | 3819 |
| yolov8x-seg.pt | 26894 | 224511 | 27833 | 21899 | 1863 | 4995 | 4071 |
| yolov9e-seg.pt | 26894 | 206362 | 28274 | 22230 | 1565 | 4664 | 4479 |

## 8. Per-sequence comparison

| Model | Sequence | Frames | GT | Predictions >.001 | TP | FP | FN | Precision | Recall | F1 | AP50 | AP75 | mAP50-95 | TP IoU | TP Dice | Ignored |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26x-seg.pt | MOTS20-02 | 600 | 7039 | 67102 | 5607 | 344 | 1432 | 0.9421945891446816 | 0.796562011649382 | 0.8632794457274827 | 0.8690592583473831 | 0.4783759298602578 | 0.48631736489491567 | 0.7823362333590935 | 0.8744356283828889 | 2391 |
| yolo26x-seg.pt | MOTS20-05 | 837 | 6570 | 44064 | 5641 | 457 | 929 | 0.9250573958674976 | 0.8585996955859969 | 0.8905904641616672 | 0.9105367563162389 | 0.7125914117975243 | 0.649731825113062 | 0.8506416141755306 | 0.9155273668272643 | 782 |
| yolo26x-seg.pt | MOTS20-09 | 525 | 4774 | 29639 | 4233 | 201 | 541 | 0.9546684709066305 | 0.8866778382907415 | 0.9194178974804518 | 0.9146228954524609 | 0.7046064877194699 | 0.6101132541358061 | 0.8240201658566898 | 0.9003149638261093 | 1039 |
| yolo26x-seg.pt | MOTS20-11 | 900 | 8511 | 63444 | 7279 | 297 | 1232 | 0.9607972544878564 | 0.8552461520385384 | 0.9049543109342948 | 0.9203705149172317 | 0.746006317898914 | 0.656433015958394 | 0.8506709721652019 | 0.9166014666018036 | 919 |
| yolo11x-seg.pt | MOTS20-02 | 600 | 7039 | 64598 | 5343 | 336 | 1696 | 0.9408346539883783 | 0.7590566841880949 | 0.8402264506997955 | 0.8326945983006856 | 0.36408622343000285 | 0.41681473593916174 | 0.7514886375644309 | 0.8546608425048614 | 1667 |
| yolo11x-seg.pt | MOTS20-05 | 837 | 6570 | 46189 | 5515 | 494 | 1055 | 0.9177899816941255 | 0.8394216133942162 | 0.8768582558231974 | 0.8930780326526452 | 0.6585949281025764 | 0.6040701958359443 | 0.8329470598192477 | 0.9049178277333145 | 611 |
| yolo11x-seg.pt | MOTS20-09 | 525 | 4774 | 32254 | 4146 | 244 | 628 | 0.9444191343963554 | 0.8684541265186426 | 0.9048450458315146 | 0.8907833000806089 | 0.5797240007105077 | 0.5331389794454843 | 0.7894614204326661 | 0.8789739506587231 | 867 |
| yolo11x-seg.pt | MOTS20-11 | 900 | 8511 | 57327 | 7109 | 370 | 1402 | 0.9505281454739939 | 0.83527200093996 | 0.8891807379612258 | 0.8933619063241153 | 0.6764579388657059 | 0.5823634982019754 | 0.8213563140815326 | 0.8991190688825852 | 674 |
| yolov8x-seg.pt | MOTS20-02 | 600 | 7039 | 71304 | 5370 | 641 | 1669 | 0.8933621693561803 | 0.7628924563148174 | 0.8229885057471265 | 0.8234823567044507 | 0.36400222758251033 | 0.4107869280657733 | 0.750315393012812 | 0.8536586911315451 | 1652 |
| yolov8x-seg.pt | MOTS20-05 | 837 | 6570 | 42109 | 5385 | 417 | 1185 | 0.9281282316442606 | 0.819634703196347 | 0.8705140640155189 | 0.8803484702225787 | 0.6327572436118705 | 0.5863085143554491 | 0.8291405226882803 | 0.9023456821053181 | 559 |
| yolov8x-seg.pt | MOTS20-09 | 525 | 4774 | 37216 | 4088 | 252 | 686 | 0.9419354838709677 | 0.8563049853372434 | 0.8970814132104454 | 0.8833580080081453 | 0.5590863028350296 | 0.5218316930836745 | 0.7873833907622595 | 0.8775777724093042 | 1146 |
| yolov8x-seg.pt | MOTS20-11 | 900 | 8511 | 73882 | 7056 | 553 | 1455 | 0.9273229070837167 | 0.8290447655974621 | 0.8754342431761787 | 0.8804443748143892 | 0.6591035133501246 | 0.5689943193423534 | 0.8170987041479278 | 0.8963189747151283 | 714 |
| yolov9e-seg.pt | MOTS20-02 | 600 | 7039 | 62934 | 5424 | 403 | 1615 | 0.9308391968422859 | 0.7705640005682626 | 0.8431524949479248 | 0.8459408968234332 | 0.3737092744988751 | 0.42284450581385846 | 0.7513954429289432 | 0.8544845080902308 | 2008 |
| yolov9e-seg.pt | MOTS20-05 | 837 | 6570 | 40529 | 5481 | 363 | 1089 | 0.9378850102669405 | 0.8342465753424657 | 0.8830352827452875 | 0.8938493410226884 | 0.6519113569226646 | 0.6021198253240554 | 0.832231154385717 | 0.9043016312035629 | 645 |
| yolov9e-seg.pt | MOTS20-09 | 525 | 4774 | 34280 | 4113 | 197 | 661 | 0.954292343387471 | 0.8615416841223292 | 0.9055482166446499 | 0.8903224424150247 | 0.5674049090368587 | 0.527401909823149 | 0.788039960996787 | 0.8780704833327128 | 984 |
| yolov9e-seg.pt | MOTS20-11 | 900 | 8511 | 68619 | 7212 | 602 | 1299 | 0.922958791911953 | 0.8473739866055693 | 0.8835528330781011 | 0.8965131312749289 | 0.6674113584497305 | 0.5818630057009012 | 0.8167154916779128 | 0.8960148359980267 | 842 |

## 9. Mask-quality analysis

Conditional on matched TP only, not dataset-wide mask accuracy. Population standard deviation.

| Model | TP-only metric | Mean | Median | Std | P25 | P75 |
| --- | --- | --- | --- | --- | --- | --- |
| yolo26x-seg.pt | iou | 0.8288725823581055 | 0.8566006100969179 | 0.10031858789237338 | 0.7728837398752542 | 0.9052878352385243 |
| yolo26x-seg.pt | dice | 0.9029185308385722 | 0.9227623921169141 | 0.06417506691483897 | 0.8718944423527674 | 0.9502898391251945 |
| yolo11x-seg.pt | iou | 0.8013854253755417 | 0.8230842005676443 | 0.10135619073488292 | 0.7389558232931727 | 0.8786688203023821 |
| yolo11x-seg.pt | dice | 0.8860461340193582 | 0.9029579657498702 | 0.06586549896683025 | 0.8498845265588915 | 0.9354164084768868 |
| yolov8x-seg.pt | iou | 0.7981363136699888 | 0.820675105485232 | 0.10373432255235793 | 0.7327504313074622 | 0.8776519643752669 |
| yolov8x-seg.pt | dice | 0.8838414214673144 | 0.9015063731170335 | 0.06769110400696646 | 0.8457656890983678 | 0.9348398755614269 |
| yolov9e-seg.pt | iou | 0.7992977204316506 | 0.820444785573883 | 0.10328030031454467 | 0.73465280927405 | 0.878353833698633 |
| yolov9e-seg.pt | dice | 0.8846047731746899 | 0.9013673933461932 | 0.06724052885653092 | 0.8470315273053401 | 0.9352378853644072 |

## 10. Person-size descriptive distribution

Relative mask area = GT mask pixels / source image pixels. No size categories are invented.

| min | p10 | p25 | median | p75 | p90 | max |
| --- | --- | --- | --- | --- | --- | --- |
| 0.000001 | 0.000811 | 0.001683 | 0.006268 | 0.021349 | 0.058746 | 0.330098 |

Every GT instance has mask area, bbox width/height/area, image dimensions and both normalized areas in `metrics/gt_instances.csv`.

## 11. Crowd descriptive analysis

Grouped by exact valid GT person count per frame; this is **not an occlusion severity label**. The following rows describe the empirical minimum, middle and maximum occupied count levels; complete exact-count distributions are saved in each model’s crowd CSV. Sequence and person-size composition can confound these comparisons.

| Model | GT/frame | Frames | TP | FP | FN | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26x-seg.pt | 3 | 14 | 42 | 2 | 0 | 0.9545454545454546 | 1.0 | 0.9767441860465116 |
| yolo26x-seg.pt | 10 | 539 | 4657 | 251 | 733 | 0.9488590057049715 | 0.8640074211502783 | 0.9044474655272868 |
| yolo26x-seg.pt | 16 | 6 | 71 | 4 | 25 | 0.9466666666666667 | 0.7395833333333334 | 0.8304093567251462 |
| yolo11x-seg.pt | 3 | 14 | 42 | 2 | 0 | 0.9545454545454546 | 1.0 | 0.9767441860465116 |
| yolo11x-seg.pt | 10 | 539 | 4545 | 276 | 845 | 0.9427504667081519 | 0.8432282003710575 | 0.890216433258251 |
| yolo11x-seg.pt | 16 | 6 | 64 | 0 | 32 | 1.0 | 0.6666666666666666 | 0.8 |
| yolov8x-seg.pt | 3 | 14 | 42 | 1 | 0 | 0.9767441860465116 | 1.0 | 0.9882352941176471 |
| yolov8x-seg.pt | 10 | 539 | 4488 | 376 | 902 | 0.9226973684210527 | 0.8326530612244898 | 0.8753657109420714 |
| yolov8x-seg.pt | 16 | 6 | 71 | 4 | 25 | 0.9466666666666667 | 0.7395833333333334 | 0.8304093567251462 |
| yolov9e-seg.pt | 3 | 14 | 42 | 1 | 0 | 0.9767441860465116 | 1.0 | 0.9882352941176471 |
| yolov9e-seg.pt | 10 | 539 | 4556 | 317 | 834 | 0.9349476708393187 | 0.8452690166975881 | 0.887849556659846 |
| yolov9e-seg.pt | 16 | 6 | 73 | 2 | 23 | 0.9733333333333334 | 0.7604166666666666 | 0.8538011695906432 |

## 12. Speed comparison

Three clean 100-frame rounds/model after 10 untimed warmups per run. CUDA synchronization at stage boundaries; disk I/O and evaluator are excluded. Pipeline includes preprocessing, forward, NMS/native masks, binary validation, lossless packing and CPU transfer. RLE preparation is separate. Mean-derived FPS is not mean instantaneous FPS.

| Model | Stage | Mean ms | Median ms | Std ms | P50 ms | P95 ms |
| --- | --- | --- | --- | --- | --- | --- |
| yolo26x-seg.pt | preprocess_ms | 1.7167626899511863 | 1.892169937491417 | 0.464661784295447 | 1.892169937491417 | 2.2339110146276653 |
| yolo26x-seg.pt | inference_ms | 72.45824582952385 | 72.41080002859235 | 2.948514540295626 | 72.41080002859235 | 77.5124221923761 |
| yolo26x-seg.pt | ultralytics_postprocess_inclusive_ms | 25.006894808805857 | 24.514787015505135 | 14.690059514788578 | 24.514787015505135 | 47.82624538638629 |
| yolo26x-seg.pt | postprocess_ms | 35.46362601841489 | 34.887362038716674 | 21.141890684377817 | 34.887362038716674 | 68.0255068873521 |
| yolo26x-seg.pt | total_ms | 109.63863453788993 | 108.25321997981519 | 20.387884384645993 | 108.25321997981519 | 141.45580357289873 |
| yolo26x-seg.pt | rle_preparation_ms | 205.00718040120168 | 193.09201394207776 | 135.15159051464005 | 193.09201394207776 | 414.7693427628838 |
| yolo11x-seg.pt | preprocess_ms | 1.6817618914258976 | 1.8771104514598846 | 0.4463950470803504 | 1.8771104514598846 | 2.152429352281615 |
| yolo11x-seg.pt | inference_ms | 69.40603260455343 | 69.32149745989591 | 2.5951518051472395 | 69.32149745989591 | 73.66367133217864 |
| yolo11x-seg.pt | ultralytics_postprocess_inclusive_ms | 24.32377590991867 | 24.613763962406665 | 13.921723213171969 | 24.613763962406665 | 46.90536530688405 |
| yolo11x-seg.pt | postprocess_ms | 34.79739082239879 | 35.06641200510785 | 20.684807773726153 | 35.06641200510785 | 66.8228063150309 |
| yolo11x-seg.pt | total_ms | 105.8851853183781 | 105.7572599966079 | 19.95579777841518 | 105.7572599966079 | 137.07756671356037 |
| yolo11x-seg.pt | rle_preparation_ms | 195.78215693084834 | 196.3893930078484 | 124.5069363472894 | 196.3893930078484 | 395.22712748730555 |
| yolov8x-seg.pt | preprocess_ms | 1.7109290533699095 | 1.8951594829559326 | 0.4484185990893131 | 1.8951594829559326 | 2.155718789435924 |
| yolov8x-seg.pt | inference_ms | 67.84281638412115 | 67.54667102359235 | 2.9995559670758762 | 67.54667102359235 | 73.06390318553895 |
| yolov8x-seg.pt | ultralytics_postprocess_inclusive_ms | 28.017258798936382 | 29.072825505863875 | 15.507438386911957 | 29.072825505863875 | 50.353212567279115 |
| yolov8x-seg.pt | postprocess_ms | 39.887478031062834 | 41.12596053164452 | 22.6437704207964 | 41.12596053164452 | 72.27991710533388 |
| yolov8x-seg.pt | total_ms | 109.4412234685539 | 111.60842649405822 | 21.768410913994373 | 111.60842649405822 | 141.43426650553013 |
| yolov8x-seg.pt | rle_preparation_ms | 232.7185331750661 | 240.9210245241411 | 144.79963841931664 | 240.9210245241411 | 449.3927799689118 |
| yolov9e-seg.pt | preprocess_ms | 1.6976542592359085 | 1.882335520349443 | 0.4473808885507152 | 1.882335520349443 | 2.133987337583676 |
| yolov9e-seg.pt | inference_ms | 65.8879176088764 | 65.47189352568239 | 1.7955623659753566 | 65.47189352568239 | 69.70694710616954 |
| yolov9e-seg.pt | ultralytics_postprocess_inclusive_ms | 24.84472477498154 | 26.218582992441952 | 13.586228089396748 | 26.218582992441952 | 42.941240477375686 |
| yolov9e-seg.pt | postprocess_ms | 35.790017519611865 | 37.73311199620366 | 19.837235940943273 | 37.73311199620366 | 62.16129051172175 |
| yolov9e-seg.pt | total_ms | 103.37558938772418 | 105.37048644619063 | 19.104957169023557 | 105.37048644619063 | 129.47158256429248 |
| yolov9e-seg.pt | rle_preparation_ms | 215.13600670848973 | 231.61909345071763 | 131.79509158877772 | 231.61909345071763 | 394.28571080206893 |

Seed 20260929; model order by round: `[["yolo26x-seg.pt", "yolo11x-seg.pt", "yolov8x-seg.pt", "yolov9e-seg.pt"], ["yolo11x-seg.pt", "yolov8x-seg.pt", "yolov9e-seg.pt", "yolo26x-seg.pt"], ["yolov8x-seg.pt", "yolov9e-seg.pt", "yolo26x-seg.pt", "yolo11x-seg.pt"]]`. All timing GPU-state samples, processes, clocks, temperature and power are preserved.

## 13. GPU-memory comparison

Peak CUDA allocator values after warmup, including resident model. Max across clean timing rounds. Reserved cache is not equivalent to live allocated tensors or whole-device VRAM.

| Model | Baseline allocated MiB | Baseline reserved MiB | Peak allocated MiB | Peak reserved MiB |
| --- | --- | --- | --- | --- |
| yolo26x-seg.pt | 277.7119140625 | 1044.0 | 952.18408203125 | 1358.0 |
| yolo11x-seg.pt | 274.3876953125 | 1000.0 | 942.47802734375 | 2238.0 |
| yolov8x-seg.pt | 310.5263671875 | 1238.0 | 1001.13330078125 | 2370.0 |
| yolov9e-seg.pt | 263.52783203125 | 1412.0 | 855.4072265625 | 1938.0 |

## 14. Parameter/model-size comparison

Local loaded checkpoint parameter count is primary. Runtime fusion removes BatchNorm and, where applicable, unused heads; it can differ from documentation or loaded representation. Local GFLOPs are Ultralytics/THOP estimates for NMS forward at 640, not measured hardware operations. CPU NNPACK warnings occurred during this inspection. Loading is supplementary and excluded from FPS.

| Model | Loaded params | Fused runtime params | GFLOPs | Checkpoint MB | Mean timing load s |
| --- | --- | --- | --- | --- | --- |
| YOLO26x-Seg | 70693800 | 62819132 | 338.203341 | 142.129861 | 0.8367087880227094 |
| YOLO11x-Seg | 62142656 | 62094528 | 297.892403 | 125.090821 | 1.1474306492988642 |
| YOLOv8x-Seg | 71827888 | 71797696 | 329.188813 | 144.101612 | 0.5170126649706314 |
| YOLOv9e-Seg | 60512800 | 59743360 | 238.332570 | 122.212466 | 1.0485705396470923 |

## 15. Qualitative results

Twelve predetermined frames (three/sequence), identical for all four models. Each sheet shows source, GT, predictions, TP matches, FN/FP, and ignore regions. No post-hoc examples are mixed with these.

### MOTS20-02, predetermined frame 1

[YOLO26x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolo26x-seg/MOTS20-02_000001.jpg) · [YOLO11x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolo11x-seg/MOTS20-02_000001.jpg) · [YOLOv9e-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolov9e-seg/MOTS20-02_000001.jpg) · [YOLOv8x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolov8x-seg/MOTS20-02_000001.jpg) · 

### MOTS20-05, predetermined frame 1

[YOLO26x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolo26x-seg/MOTS20-05_000001.jpg) · [YOLO11x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolo11x-seg/MOTS20-05_000001.jpg) · [YOLOv9e-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolov9e-seg/MOTS20-05_000001.jpg) · [YOLOv8x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolov8x-seg/MOTS20-05_000001.jpg) · 

### MOTS20-09, predetermined frame 1

[YOLO26x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolo26x-seg/MOTS20-09_000001.jpg) · [YOLO11x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolo11x-seg/MOTS20-09_000001.jpg) · [YOLOv9e-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolov9e-seg/MOTS20-09_000001.jpg) · [YOLOv8x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolov8x-seg/MOTS20-09_000001.jpg) · 

### MOTS20-11, predetermined frame 1

[YOLO26x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolo26x-seg/MOTS20-11_000001.jpg) · [YOLO11x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolo11x-seg/MOTS20-11_000001.jpg) · [YOLOv9e-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolov9e-seg/MOTS20-11_000001.jpg) · [YOLOv8x-Seg contact sheet](outputs/visualizations/benchmark-20260929T0520Z/yolov8x-seg/MOTS20-11_000001.jpg) · 


Research plots (all bar axes start at zero; AP axes use 0–1):

![mask_map](outputs/plots/benchmark-20260929T0520Z/mask_map.png)

![ap50_ap75](outputs/plots/benchmark-20260929T0520Z/ap50_ap75.png)

![precision_recall_f1](outputs/plots/benchmark-20260929T0520Z/precision_recall_f1.png)

![matched_mask_quality](outputs/plots/benchmark-20260929T0520Z/matched_mask_quality.png)

![inference_latency](outputs/plots/benchmark-20260929T0520Z/inference_latency.png)

![pipeline_latency](outputs/plots/benchmark-20260929T0520Z/pipeline_latency.png)

![fps](outputs/plots/benchmark-20260929T0520Z/fps.png)

![peak_vram](outputs/plots/benchmark-20260929T0520Z/peak_vram.png)

![accuracy_vs_latency](outputs/plots/benchmark-20260929T0520Z/readable/accuracy_vs_latency.png)

![accuracy_vs_parameters](outputs/plots/benchmark-20260929T0520Z/readable/accuracy_vs_parameters.png)

## 16. Warnings/failures
CPU NNPACK unsupported-hardware warnings appeared during model complexity inspection.
pycocotools emits a NumPy copy-keyword DeprecationWarning; all 15 pilot regression
tests passed. No dependencies were changed to suppress warnings. No OOM, failed
accuracy frames, resumed runs or contaminated primary timing runs occurred.
The original timing pass contained non-idle start flags, despite no other
compute process being observed. Its entire pass is excluded from primary
speed results and preserved unchanged. All four models and all three rounds
were repeated in `timing/benchmark-20260929T0520Z/clean_repetition/`, waiting for the
already specified idle condition before loading. The measured loop, settings,
frame order, seed, warmup and statistics are unchanged. Generated recovery
source and exact substitutions are archived under `logs/benchmark-20260929T0520Z/`.
No flagged original run was reclassified as clean.
The execution sandbox initially failed its namespace initialization; benchmark
commands ran through the explicitly approved execution path. This does not change
inference settings. Stdout/stderr and failure records, if any, are retained.

## 17. Threats to validity
Largest variants have unequal capacity and training recipes: not architecture-only
or parameter-matched evidence. Native resolution and scene difficulty vary by
sequence, although each model sees identical inputs. Video frames are correlated;
no independent-image significance test is claimed. Person-only COCO-style AP with
the pilot's fixed ignore policy is not official MOTS tracking evaluation.
Fixed thresholds were not optimized by model. Preflight maxDet convergence is
sample-based, not proof of full-population cap convergence. Full candidate counts
are retained for later cap analysis. The same source frames in three speed rounds
improve repeatability but do not characterize every deployment workload. Shared
GPU telemetry cannot rule out every transient system effect. TP-only mask scores
exclude misses and must be interpreted with recall.

## 18. Interpretation
YOLO26x-Seg has the highest measured mask accuracy; YOLOv9e-Seg has the lowest mean neural inference latency; YOLOv9e-Seg uses the lowest peak allocated memory. The empirical accuracy–inference-latency Pareto set is YOLO26x-Seg, YOLO11x-Seg, YOLOv9e-Seg. This is a descriptive trade-off, not a combined score or statistical superiority claim. YOLO11x and YOLOv9e differ by only about 0.000032 in overall mask mAP50-95; treat their accuracy as near-tied descriptive measurements, not established superiority.

## 19. Conclusions
**A. Preliminary YOLO instance-segmentation comparison: YES**, within this exact
largest-variant, pretrained, MOTS20 Person frame-level protocol.
**B. Final CCTV robustness conclusions: NO.** No controlled blur, illumination,
camera-angle categories or explicit occlusion severity labels were tested.
Next: a separate preregistered CCTV robustness experiment; optionally a separate
capacity-controlled YOLO comparison to examine architecture effects.

Final protocol consistency checks:

| Item | PASS/FAIL | Evidence |
| --- | --- | --- |
| Frozen config/protocol | PASS | SHA256 at Phase 4 start versus final |
| Frozen implementation | PASS | Every benchmark/frozen-pilot Python source |
| Validated evaluator and pilot preserved | PASS | Original and frozen snapshot hashes |
| Image manifest unchanged | PASS | Ordered list, dimensions and original image hashes |
| Predetermined sample lists unchanged | PASS | Preflight/timing/visualization hashes frozen before full run |
| Dataset images unchanged | PASS | Rehash every one of 2,862 original image files |
| Ground truth and sequence metadata unchanged | PASS | All GT and seqinfo SHA256 |
| Checkpoints unchanged | PASS | All four checkpoint SHA256 |
| YOLO26x-Seg exact frame list/count | PASS | Successful metadata plus per-frame file audit |
| YOLO26x-Seg saved predictions and tensor shapes | PASS | Lossless RLE/class/score/dimensions checked on every saved frame |
| YOLO11x-Seg exact frame list/count | PASS | Successful metadata plus per-frame file audit |
| YOLO11x-Seg saved predictions and tensor shapes | PASS | Lossless RLE/class/score/dimensions checked on every saved frame |
| YOLOv8x-Seg exact frame list/count | PASS | Successful metadata plus per-frame file audit |
| YOLOv8x-Seg saved predictions and tensor shapes | PASS | Lossless RLE/class/score/dimensions checked on every saved frame |
| YOLOv9e-Seg exact frame list/count | PASS | Successful metadata plus per-frame file audit |
| YOLOv9e-Seg saved predictions and tensor shapes | PASS | Lossless RLE/class/score/dimensions checked on every saved frame |
| Common ap_max_dets | PASS | 200 |
| Common fixed_confidence | PASS | 0.25 |
| Common ap_confidence_floor | PASS | 0.001 |
| Common nms_iou | PASS | 0.7 |
| Common max_detections | PASS | 1000 |
| Common precision | PASS | fp32 |
| Common imgsz | PASS | 640 |
| Common batch | PASS | 1 |
| Common rect | PASS | False |
| Common retina_masks | PASS | True |
| Common matching_iou | PASS | 0.5 |
| Common ignore_prediction_ioa | PASS | 0.5 |
| NMS one-to-many path and CUDA FP32 | PASS | Backend state asserted at load |
| Same evaluator manifest | PASS | One source_manifest SHA256 |
| Same frozen protocol and config | PASS | Each model metadata |
| Three clean timing rounds per model | PASS | Contaminated rounds excluded from primary table |
| Same exact timing frame order for every round | PASS | 100 identical ordered frame keys × 12 runs |
| No contaminated timing in primary table | PASS | Before/during/after telemetry and other-process audit |
| Complete accuracy metrics | PASS | 4 overall plus 16 sequence records |
| Complete timing metrics | PASS | Dedicated timing, evaluator preparation excluded |

## 20. Exact artifact paths
All paths below are relative to workspace `YOLO_Large_Seg_MOTS20_Benchmark/`:

- Main report: `REPORT.md`; preserved summary: `reports/benchmark-20260929T0520Z/SUMMARY.md`
- Frozen protocol/config: `EXPERIMENT_PROTOCOL.md`, `configs/benchmark.yaml`
- Environment/data/checkpoint/source manifests: `manifests/`
- Exact all-frame list/hashes: `manifests/images.json`
- Predetermined frame lists: `manifests/{preflight,timing,visualization}_frames.json`
- Full-run freeze/order: `manifests/benchmark-20260929T0520Z_full_freeze.json`
- Comparison, per-sequence, preflight, consistency CSVs: `metrics/benchmark-20260929T0520Z/`
- Per-frame/matched-instance metrics: `metrics/benchmark-20260929T0520Z/{per_frame,per_instance}/`
- GT instance sizes/counts: `metrics/gt_instances.csv`, `metrics/gt_frames.csv`
- Lossless per-frame predictions/audits: `predictions/benchmark-20260929T0520Z/{preflight,accuracy}/`
- Timing measurements and telemetry: `timing/benchmark-20260929T0520Z/`
- Stdout/stderr and regression logs: `logs/benchmark-20260929T0520Z/`
- Plots, PDF copies and values: `outputs/plots/benchmark-20260929T0520Z/`
- Predetermined qualitative sheets: `outputs/visualizations/benchmark-20260929T0520Z/`

Model weights remain in workspace `models/`; dataset and pilot are unchanged.
