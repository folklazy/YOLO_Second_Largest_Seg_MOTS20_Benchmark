"""Measured cross-tier deltas and Thai interpretation. No inference or metric changes."""
import sys
import shutil
from pathlib import Path
import report_base as base
from validate import EXP, ROOT, sha, write, now
import matplotlib.pyplot as plt
import numpy as np

PAIRS = [('YOLO26', 'YOLO26x-Seg', 'YOLO26l-Seg'), ('YOLO11', 'YOLO11x-Seg', 'YOLO11l-Seg'),
         ('YOLOv8', 'YOLOv8x-Seg', 'YOLOv8l-Seg'), ('YOLOv9', 'YOLOv9e-Seg', 'YOLOv9c-Seg')]
METRICS = ['map50_95', 'ap50', 'ap75', 'recall', 'f1', 'inference_ms', 'pipeline_ms', 'fps',
           'peak_allocated_mib', 'parameters', 'checkpoint_mb']

def numeric(rows):
    return [{k: v if k == 'model' else float(v) for k, v in row.items()} for row in rows]

def main(run):
    previous = ROOT / 'YOLO_Large_Seg_MOTS20_Benchmark'
    audit = base.read(EXP / 'manifests/shared_input_audit.json')
    for relative, digest in audit['reference_hashes'].items():
        assert sha(previous / relative) == digest, f'Reference changed: {relative}'
    base.main(run)
    current = numeric(base.rows(EXP / 'metrics/comparison_summary.csv'))
    largest = numeric(base.rows(previous / 'metrics/comparison_summary.csv'))
    out = EXP / 'metrics' / run
    plot = EXP / 'outputs/plots' / run
    cross, details = [], []
    for family, large, small in PAIRS:
        a = next(r for r in largest if r['model'] == large)
        b = next(r for r in current if r['model'] == small)
        row = {'family': family, 'largest': large, 'second_largest': small}
        for key in METRICS:
            row['largest_' + key] = a[key]
            row['second_' + key] = b[key]
            row['delta_' + key] = b[key] - a[key]
            row['relative_percent_' + key] = 100 * (b[key] / a[key] - 1)
            details.append({'family': family, 'metric': key, 'largest': a[key], 'second_largest': b[key],
                            'absolute_delta': b[key] - a[key],
                            'percentage_point_delta': 100 * (b[key] - a[key]) if key in METRICS[:5] else '',
                            'relative_percent_delta': row['relative_percent_' + key]})
        cross.append(row)
    base.csvwrite(out / 'cross_tier_summary.csv', cross)
    base.csvwrite(out / 'cross_tier_all_deltas.csv', details)
    base.csvwrite(plot / 'cross_tier_plot_values.csv', cross)
    for key, title, filename in [('map50_95', 'Mask mAP50-95 (0–1)', 'cross_tier_map'),
                                 ('inference_ms', 'Mean neural inference (ms)', 'cross_tier_latency'),
                                 ('peak_allocated_mib', 'Peak allocated VRAM (MiB)', 'cross_tier_vram')]:
        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(4)
        for offset, prefix, label in [(-.2, 'largest_', 'Largest'), (.2, 'second_', 'Second-largest')]:
            bars = ax.bar(x + offset, [r[prefix + key] for r in cross], .4, label=label)
            ax.bar_label(bars, fmt='%.3f', padding=3, fontsize=8)
        ax.set_xticks(x, [r['family'] for r in cross]); ax.set_ylabel(title)
        ax.set_ylim(bottom=0)
        if key == 'map50_95': ax.set_ylim(0, 1)
        ax.legend(); ax.grid(axis='y', alpha=.2); ax.set_axisbelow(True)
        fig.tight_layout(); fig.savefig(plot / (filename + '.png'), dpi=180); plt.close(fig)
    for key, filename, xlabel in [('inference_ms', 'delta_accuracy_vs_latency', 'Latency reduction (ms; positive = faster)'),
                                  ('parameters', 'delta_accuracy_vs_parameters', 'Loaded parameter reduction (millions)')]:
        fig, ax = plt.subplots(figsize=(10, 6))
        coords = [(-r['delta_' + key] / (1e6 if key == 'parameters' else 1), 100 * r['delta_map50_95']) for r in cross]
        for i, (r, (x, y)) in enumerate(zip(cross, coords)):
            ax.scatter(x, y, s=60)
            ax.annotate(r['family'], (x, y), xytext=(8, 10 + i * 8), textcoords='offset points', arrowprops={'arrowstyle': '-', 'alpha': .4})
        ax.axhline(0, color='gray', linewidth=.8); ax.axvline(0, color='gray', linewidth=.8)
        ax.set_xlabel(xlabel); ax.set_ylabel('Second-largest minus largest mAP (percentage points)')
        bound = max(1, max(abs(y) for _, y in coords) * 1.3)
        ax.set_ylim(-bound, bound); ax.grid(alpha=.2)
        fig.tight_layout(); fig.savefig(plot / (filename + '.png'), dpi=180); plt.close(fig)
    best = max(current, key=lambda r: r['map50_95'])
    fast = min(current, key=lambda r: r['inference_ms'])
    pipeline = min(current, key=lambda r: r['pipeline_ms'])
    low = min(current, key=lambda r: r['peak_allocated_mib'])
    pareto = [r['model'] for r in current if not any(o['map50_95'] >= r['map50_95'] and o['inference_ms'] <= r['inference_ms'] and
              (o['map50_95'] > r['map50_95'] or o['inference_ms'] < r['inference_ms']) for o in current)]
    scaling = '\n'.join(f"- **{r['largest']} → {r['second_largest']}**: mAP {r['largest_map50_95']:.6f} → {r['second_map50_95']:.6f} "
                        f"(Δ {100*r['delta_map50_95']:+.3f} percentage points); inference {r['largest_inference_ms']:.3f} → {r['second_inference_ms']:.3f} ms "
                        f"(Δ {r['relative_percent_inference_ms']:+.2f}%); peak VRAM {r['largest_peak_allocated_mib']:.2f} → {r['second_peak_allocated_mib']:.2f} MiB "
                        f"(Δ {r['relative_percent_peak_allocated_mib']:+.2f}%)" for r in cross)
    practical = '\n'.join(f"- **{r['model']}**: mAP {r['map50_95']:.6f}, recall {r['recall']:.4f}, inference {r['inference_ms']:.3f} ms, "
                          f"pipeline {r['pipeline_ms']:.3f} ms ({r['fps']:.2f} FPS), peak VRAM {r['peak_allocated_mib']:.2f} MiB" for r in current)
    summary = f'''# Experiment 2: Second-largest available variant comparison

Run `{run}` — **PASS WITH WARNINGS**

## 1. ทดสอบอะไร

เปรียบเทียบ YOLO26l-Seg, YOLO11l-Seg, YOLOv8l-Seg และ YOLOv9c-Seg บน Person instance segmentation ของ MOTS20 train ทั้ง 2,862 ภาพ (26,894 GT instances) ไม่มีการฝึกเพิ่ม โมเดลเป็นรุ่นใหญ่เป็นอันดับสองที่มีให้ใช้ในแต่ละตระกูล YOLOv9 ใช้ c ไม่ใช่ L และทั้งสี่รุ่นมี capacity ไม่เท่ากัน

## 2. เงื่อนไขการทดลอง

ใช้ Tesla T4, CUDA:0, FP32, batch=1 และ input 1×3×640×640 เหมือนกันทุกโมเดล ไม่ใช้ augmentation ใช้ native masks, square letterbox และ YOLO26 one-to-many NMS ตาม Experiment 1 ทุกภาพและ GT ผ่านการตรวจ hashes ว่าตรงกัน ใช้ภาพ preflight/timing/visualization เดิม evaluator เดิม confidence floor=0.001, fixed threshold=0.25, NMS IoU=0.70 และ evaluation mask IoU=0.50 คง AP maxDet=200 หลังผ่าน convergence test วัด timing แยก 100 ภาพ × 3 รอบหลัง warmup 10 ครั้งต่อรอบ

## 3. ผลหลัก

**Accuracy สูงสุด: {best['model']} (mAP50-95={best['map50_95']:.6f})**
**Inference เร็วสุด: {fast['model']} ({fast['inference_ms']:.3f} ms)**
**Pipeline เร็วสุด: {pipeline['model']} ({pipeline['pipeline_ms']:.3f} ms; {pipeline['fps']:.2f} FPS)**
**Peak allocated VRAM ต่ำสุด: {low['model']} ({low['peak_allocated_mib']:.2f} MiB)**

ความแม่นยำ ความเร็ว และหน่วยความจำเป็นคนละเป้าหมาย ให้เลือกตามข้อจำกัดงาน ไม่รวมเป็นคะแนนถ่วงน้ำหนัก ชุด Pareto สำหรับ mAP–inference คือ {', '.join(pareto)}

## 4. แต่ละโมเดลเด่นด้านไหน

{practical}

## 5. เทียบกับรุ่นใหญ่สุดที่ทดสอบก่อนหน้า

{scaling}

Δ หมายถึง second-largest ลบ largest: ค่า latency/VRAM ติดลบคือใช้ลดลง ค่าความแม่นยำติดลบคือเสีย accuracy ใช้ผล Experiment 1 ที่เก็บไว้ ไม่รัน inference เดิมซ้ำ ตาราง technical ด้านล่างแสดง AP50/AP75/Recall/F1, pipeline, FPS, parameters และขนาด checkpoint เพิ่มเติม

## 6. ข้อจำกัด

โมเดลมี capacity และสูตร pretraining ต่างกัน ภาพวิดีโอต่อเนื่องมีความสัมพันธ์กัน จึงไม่อ้าง statistical significance ค่า IoU/Dice เป็นเฉพาะ TP ที่จับคู่สำเร็จ ต้องอ่านพร้อม recall ผล MOTS20 ไม่ใช่หลักฐาน final CCTV robustness และ crowd count ไม่ใช่ระดับ occlusion ที่ติดป้ายกำกับ Shared-GPU telemetry ลดความเสี่ยงการปนเปื้อนแต่ไม่รับประกันว่าไม่มีผลระบบชั่วขณะ

## 7. ทำอะไรต่อ

ทดลอง YOLO บนชุด CCTV ที่มี GT แยกเงื่อนไข blur, low-light และ camera angle โดยกำหนด protocol ก่อนเห็นผล หากต้องการพิสูจน์ความเหนือกว่าของ architecture ต้องมี capacity-controlled comparison เพิ่มต่างหาก

'''
    text = (EXP / 'REPORT.md').read_text()
    technical = text[text.index('## 1. Research question'):]
    cross_columns = [('family', 'Family'), ('largest', 'Largest model'), ('second_largest', 'Second-largest model'),
                     ('largest_map50_95', 'Largest mAP'), ('second_map50_95', 'Second mAP'), ('delta_map50_95', 'Δ mAP (0–1)'),
                     ('largest_inference_ms', 'Largest inference ms'), ('second_inference_ms', 'Second inference ms'), ('delta_inference_ms', 'Δ latency ms'),
                     ('largest_peak_allocated_mib', 'Largest VRAM MiB'), ('second_peak_allocated_mib', 'Second VRAM MiB'), ('delta_peak_allocated_mib', 'Δ VRAM MiB')]
    cross_text = '\n## Cross-tier: largest vs second-largest\n\n' + base.table(cross, cross_columns)
    cross_text += '\nAbsolute differences are second-largest minus largest. Percentage-point changes apply only to metrics on the 0–1 scale. Relative changes use the largest-model value as denominator. VRAM means peak allocated PyTorch memory, not whole-device usage.\n\n'
    cross_text += base.table(details, [('family', 'Family'), ('metric', 'Metric'), ('largest', 'Largest'), ('second_largest', 'Second-largest'),
                                     ('absolute_delta', 'Absolute Δ'), ('percentage_point_delta', 'Δ pp'), ('relative_percent_delta', 'Relative Δ %')])
    large_order = sorted(largest, key=lambda r: -r['map50_95'])
    small_order = sorted(current, key=lambda r: -r['map50_95'])
    cross_text += '\nAccuracy ranking, largest: ' + ' > '.join(r['model'] for r in large_order) + '.\n\nSecond-largest: ' + ' > '.join(r['model'] for r in small_order) + '. These are descriptive rankings, not significance tests.\n'
    for filename in ['cross_tier_map', 'cross_tier_latency', 'cross_tier_vram', 'delta_accuracy_vs_latency', 'delta_accuracy_vs_parameters']:
        cross_text += f'\n![{filename}](outputs/plots/{run}/{filename}.png)\n'
    cross_text += '\nExperiment 1 asks “How do the largest available models compare?” Experiment 2 asks “How do the second-largest available models compare?” Together they begin to show scaling behavior. Neither establishes capacity-controlled architecture superiority, controlled blur, low-light, camera-angle, explicit occlusion-severity robustness or final CCTV deployment suitability.\n'
    report = summary + technical + cross_text
    (EXP / 'REPORT.md').write_text(report)
    (EXP / 'reports' / run / 'SUMMARY.md').write_text(report.replace('](outputs/', '](../../outputs/'))
    write(EXP / 'manifests/cross_tier_reference.json', {'timestamp': now(), 'report_sha256': sha(previous / 'REPORT.md'),
          'comparison_summary_sha256': sha(previous / 'metrics/comparison_summary.csv'), 'reference_inference_rerun': False})
    insight = educational(current, cross, best, fast, pipeline, low, pareto, practical, scaling, run)
    (EXP / 'BENCHMARK_INSIGHTS_TH.md').write_text(insight)
    readme = (EXP / 'README.md').read_text().replace('**Status: validation in progress; no benchmark results yet.**', '**Status: PASS WITH WARNINGS — 4 models × 2,862 accuracy frames; 3 clean timing rounds/model.**')
    readme = readme.replace(' (generated after successful evaluation)', '')
    readme += f'\n## Results\n\nAccuracy: **{best["model"]}**; inference speed: **{fast["model"]}**; pipeline speed: **{pipeline["model"]}**; lowest peak allocated VRAM: **{low["model"]}**.\n\nRead the linked reports for measured cross-tier deltas and limitations.\n'
    (EXP / 'README.md').write_text(readme)
    terminal = summary + '\n' + base.table(current, [('model', 'Model'), ('map50_95', 'mAP'), ('ap50', 'AP50'), ('ap75', 'AP75'), ('precision', 'Precision'), ('recall', 'Recall'), ('f1', 'F1'), ('matched_iou_mean', 'TP IoU'), ('matched_dice_mean', 'TP Dice'), ('inference_ms', 'Inference ms'), ('pipeline_ms', 'Pipeline ms'), ('fps', 'FPS'), ('peak_allocated_mib', 'Peak VRAM MiB'), ('parameters', 'Params'), ('checkpoint_mb', 'MB')])
    terminal += f'\nWarnings: NNPACK and pycocotools deprecation; unequal capacity; correlated video frames; no significance or CCTV robustness claim.\nREPORT.md: {EXP / "REPORT.md"}\nBENCHMARK_INSIGHTS_TH.md: {EXP / "BENCHMARK_INSIGHTS_TH.md"}\n'
    (EXP / 'reports' / run / 'terminal_summary.txt').write_text(terminal)
    print(terminal)

def educational(current, cross, best, fast, pipeline, low, pareto, practical, scaling, run):
    a = next(r for r in base.rows(EXP / 'metrics/per_model.csv') if base.label(r['model']) == best['model'])
    ck = base.read(EXP / 'manifests/checkpoint_manifest.json')
    c = next(r for r in ck if base.label(r['filename']) == best['model'])
    entries = [
        ('Ground Truth (GT)', 'คำตอบอ้างอิงที่คนทำ annotation ว่าคนแต่ละคนอยู่ตรงไหน', 'ไม่ใช่คะแนนสูง/ต่ำ', 'ชุดนี้มี 26,894 Person instances ใน 2,862 ภาพ; class 2 คือคน และ class 10 คือ ignore', 'GT มีขอบเขตและนโยบาย annotation ของ MOTS20 ไม่ใช่คำตอบสำหรับทุกสภาพ CCTV'),
        ('TP', 'คนที่โมเดลทายแล้วจับคู่กับ GT ได้หนึ่งต่อหนึ่งที่ mask IoU ≥0.50', 'มากขึ้นดีเมื่อใช้ชุดข้อมูลและ threshold เดิม', f"{best['model']} มี TP={a['tp']}", 'คนเดียวไม่สามารถสร้าง TP ซ้ำหลายตัวได้'),
        ('FP', 'คำทำนายที่ไม่จับคู่ GT และไม่ถูก ignore', 'ต่ำดีกว่า', f"รุ่นเดียวกันมี FP={a['fp']}", 'ignore ต้องพิจารณาหลังจับคู่ valid GT ก่อน'),
        ('FN', 'GT คนที่ไม่มีคำทำนายจับคู่สำเร็จ', 'ต่ำดีกว่า', f"รุ่นเดียวกันมี FN={a['fn']}", 'ขอบเขต mask ที่ไม่ผ่าน IoU อาจทำให้พลาดการจับคู่ แม้มีกรอบอยู่ใกล้คน'),
        ('Precision', 'TP/(TP+FP): สิ่งที่บอกว่าเป็นคนถูกกี่ส่วน', 'สูงดีกว่า', f"{best['model']}={best['precision']:.6f}", 'precision สูงอย่างเดียวอาจยังพลาดคนจำนวนมาก ต้องอ่าน recall'),
        ('Recall', 'TP/(TP+FN): พบคนใน GT ได้กี่ส่วน', 'สูงดีกว่า', f"{best['model']}={best['recall']:.6f}", 'ใช้ confidence 0.25 เหมือนกันทุกโมเดล ไม่ใช่ทุก operating point'),
        ('F1', '2PR/(P+R): ค่าเฉลี่ยฮาร์มอนิกของ precision และ recall', 'สูงดีกว่า', f"{best['model']}={best['f1']:.6f}", 'ไม่ได้วัดรูปทรง mask หลายระดับ IoU แบบ mAP'),
        ('Mask IoU', 'พื้นที่ mask ที่ทับกันหารพื้นที่รวม', 'สูงดีกว่า', f"ค่าเฉลี่ย TP-only ของ {best['model']}={best['matched_iou_mean']:.6f}", 'ไม่รวมคนที่พลาด จึงไม่ใช่ dataset-wide detection success'),
        ('Dice', 'สองเท่าของพื้นที่ทับกันหารผลรวมพื้นที่สอง mask', 'สูงดีกว่า', f"ค่าเฉลี่ย TP-only={best['matched_dice_mean']:.6f}", 'คำนวณรายคู่ด้วย 2IoU/(1+IoU) แล้วเฉลี่ย ไม่ใช่แปลงค่าเฉลี่ย IoU'),
        ('AP50', 'สรุป precision–recall ตาม confidence โดยจับคู่ที่ mask IoU 0.50', 'สูงดีกว่า', f"{best['model']}={best['ap50']:.6f}", 'ไม่ใช่ precision ที่ confidence 0.50 และไม่ใช่ tracking metric'),
        ('AP75', 'AP ที่ mask IoU 0.75 ซึ่งต้องตรงรูปคนมากขึ้น', 'สูงดีกว่า', f"{best['model']}={best['ap75']:.6f}", 'ความต่างจาก AP50 บอกผลของเกณฑ์รูปทรงที่เข้มขึ้น ไม่แยกสาเหตุทั้งหมด'),
        ('mAP50-95', 'เฉลี่ย AP ที่ IoU 0.50 ถึง 0.95 ทีละ 0.05', 'สูงดีกว่า; เป็น metric หลัก', f"สูงสุด {best['model']}={best['map50_95']:.6f}", 'ชุดนี้มีเฉพาะ Person; pooled AP ไม่ใช่ค่าเฉลี่ย AP สี่ sequences และผลต่างเล็กไม่พิสูจน์ significance'),
        ('Latency', 'เวลาประมวลผลภาพหนึ่งภาพ หน่วย ms', 'ต่ำดีกว่า', f"Inference เร็วสุด {fast['model']}={fast['inference_ms']:.3f} ms; pipeline เร็วสุด {pipeline['model']}={pipeline['pipeline_ms']:.3f} ms", 'pipeline รวม preprocess, forward, postprocess; RLE แยกต่างหาก ไม่รวม disk I/O, GT, metrics และ visualization'),
        ('FPS', 'จำนวนภาพต่อวินาทีจาก 1000/mean pipeline ms', 'สูงดีกว่า', f"{pipeline['model']}={pipeline['fps']:.3f} FPS", 'ไม่ใช่ 1000/inference ms และยังไม่ใช่ throughput ระบบ CCTV end-to-end'),
        ('VRAM', 'หน่วยความจำ GPU ที่ PyTorch allocator ใช้', 'ต่ำดีกว่าเมื่อความแม่นยำเพียงพอ', f"ต่ำสุด {low['model']}={low['peak_allocated_mib']:.2f} MiB peak allocated", 'allocated ต่างจาก reserved และต่างจาก nvidia-smi ทั้งการ์ด; รายงาน peak หลัง warmup รวมโมเดล'),
        ('Parameters', 'จำนวนค่าพารามิเตอร์ที่โหลดจาก checkpoint', 'ไม่มีทิศทางดีเสมอ; น้อยลงช่วยด้านขนาดแต่ไม่รับประกันความเร็ว', f"{best['model']}={int(best['parameters']):,}; checkpoint={best['checkpoint_mb']:.3f} MB", 'loaded และ fused runtime อาจต่างกัน; L/c ไม่ได้มี capacity เท่ากัน'),
        ('GFLOPs', 'ค่าประมาณงานคำนวณ forward ที่ input 640', 'น้อยลงหมายถึงงานเชิงประมาณลดลง ไม่รับประกัน latency', f"{best['model']}={c['gflops_nms_unfused']:.3f} GFLOPs ตาม local profiler", 'เป็น estimate ของ NMS-path forward ไม่รวม pipeline ทั้งหมดหรือประสิทธิภาพ kernels'),
        ('maxDet', 'จำนวน predictions สูงสุดต่อภาพที่ evaluator พิจารณา', 'ต้องพอจน AP converged ไม่ใช่ยิ่งสูงยิ่งดี', 'ใช้ AP maxDet=200 หลังเทียบ 100/200/300/1000 บน 100 ภาพเดิม; model-level max_det=1000', 'หลักฐาน preflight เป็น sample ไม่ใช่ข้อพิสูจน์ convergence ทุกภาพ; สอง caps ทำหน้าที่ต่างกัน'),
        ('NMS IoU กับ evaluation IoU', 'NMS ลดกรอบทำนายซ้ำ; evaluation จับคู่ prediction mask กับ GT', 'เป็นเกณฑ์ที่ตรึงร่วม ไม่ใช่คะแนนยิ่งสูงยิ่งดี', 'NMS box IoU=0.70; fixed evaluation mask IoU=0.50; AP ใช้ 0.50–0.95', 'อย่าสับสน IoU สองขั้นตอนหรือ threshold confidence 0.25'),
        ('Pareto frontier', 'โมเดลที่ไม่มีอีกตัวทั้งแม่นกว่า/เท่ากันและเร็วกว่า/เท่ากัน โดยดีกว่าอย่างน้อยด้านหนึ่ง', 'อยู่บน frontier หมายถึงเป็นทางเลือก trade-off', ', '.join(pareto), 'ขึ้นกับสองแกนที่เลือก; frontier ของ VRAM อาจต่างออกไป ไม่ใช่คะแนนรวม'),
    ]
    text = '# อ่านผล Experiment 2 แบบเข้าใจง่าย\n\nรายงานนี้อธิบายผลวัดจริง ส่วน protocol และตารางครบอยู่ใน [REPORT.md](REPORT.md)\n\n'
    text += f'Accuracy สูงสุดคือ **{best["model"]}**; inference เร็วสุดคือ **{fast["model"]}**; pipeline เร็วสุดคือ **{pipeline["model"]}**; VRAM ต่ำสุดคือ **{low["model"]}**\n\n'
    text += 'ถ้าเน้น accuracy ให้เริ่มจากผู้ได้ mAP สูงสุด ถ้าเน้น speed ให้เลือกระหว่าง latency ของ forward กับ pipeline ตามงานจริง ถ้าเน้นสมดุลให้ดู Pareto พร้อมเพดาน VRAM และระดับ recall ที่งานยอมรับได้ ไม่มีคะแนนถ่วงน้ำหนักที่ตั้งขึ้นเอง\n\n' + practical + '\n'
    for title, definition, direction, example, caveat in entries:
        text += f'\n## {title}\n\n**วัดอะไร:** {definition}\n\n**สูงหรือต่ำจึงดี:** {direction}\n\n**อ่านผลนี้:** {example}\n\n**ข้อควรระวัง:** {caveat}\n'
    text += '\n## ลดขนาดแล้วเสีย accuracy เท่าไร เร็วขึ้นจริงหรือไม่ และ memory ลดเท่าไร\n\n' + scaling + '\n\n'
    text += base.table(cross, [('family', 'Family'), ('relative_percent_pipeline_ms', 'Pipeline Δ %'), ('relative_percent_fps', 'FPS Δ %'), ('relative_percent_parameters', 'Parameters Δ %'), ('relative_percent_checkpoint_mb', 'Checkpoint MB Δ %')])
    ranked = sorted(current, key=lambda r: r['map50_95'])
    nearest = min(zip(ranked, ranked[1:]), key=lambda p: p[1]['map50_95'] - p[0]['map50_95'])
    text += f'\n## ผลต่างไหนไม่ควรตีความเกินจริง\n\nคู่ที่ mAP ใกล้กันที่สุดใน tier นี้คือ {nearest[0]["model"]} กับ {nearest[1]["model"]}: ต่าง {100*(nearest[1]["map50_95"]-nearest[0]["map50_95"]):.4f} percentage points นี่เป็น descriptive difference ไม่มี statistical procedure ที่พิสูจน์ความเหนือกว่า ภาพวิดีโอต่อเนื่องไม่เป็นอิสระ และ latency ที่ต่างเล็กน้อยอาจได้รับอิทธิพลจากระบบ shared GPU แม้ผ่าน contamination gate\n'
    text += '\n## ผลนี้ยังบอกอะไรเกี่ยวกับ CCTV ไม่ได้\n\nExperiment 1 ตอบเรื่องรุ่นใหญ่ที่สุด Experiment 2 ตอบเรื่องรุ่นใหญ่เป็นอันดับสองที่มีให้ใช้ เมื่ออ่านร่วมกันเริ่มเห็น scaling แต่ยังไม่แยก architecture จาก capacity และ pretraining ไม่ได้พิสูจน์ controlled blur, low-light, camera-angle หรือ explicit occlusion-severity robustness และไม่ยืนยันความเหมาะสม deployment CCTV จริง ต้องมีชุดข้อมูลและการทดลองแยกเงื่อนไขต่อไป\n'
    return text

if __name__ == '__main__': main(sys.argv[1])
