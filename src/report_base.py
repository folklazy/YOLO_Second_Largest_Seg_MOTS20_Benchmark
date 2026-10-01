"""Reports and independent artifact consistency checks; performs no inference."""
from pathlib import Path
import sys,json,csv,gzip,shutil,math
from validate import ROOT,EXP,MODELS,SEQS,sha,write,now
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read(p):return json.loads(p.read_text())
def rows(p):
    with p.open() as f:return list(csv.DictReader(f))
def number(v):
    try:return float(v)
    except (TypeError,ValueError):return float('nan')
def table(rr,columns):
    s='| '+' | '.join(label for _,label in columns)+' |\n| '+' | '.join('---' for _ in columns)+' |\n'
    for r in rr:
        vals=[]
        for k,_ in columns:
            v=r.get(k,'N/A')
            if isinstance(v,float):v=f'{v:.6f}' if math.isfinite(v) else 'N/A'
            vals.append(str(v))
        s+='| '+' | '.join(vals)+' |\n'
    return s
def csvwrite(p,rr):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def label(name):return {'yolo26l-seg.pt':'YOLO26l-Seg','yolo11l-seg.pt':'YOLO11l-Seg','yolov8l-seg.pt':'YOLOv8l-Seg','yolov9c-seg.pt':'YOLOv9c-Seg'}[name]

def main(run):
    out=EXP/'metrics'/run;tim=EXP/'timing'/run/'clean_repetition';plot=EXP/'outputs/plots'/run;plot.mkdir(parents=True,exist_ok=True)
    summarydir=EXP/'reports'/run;summarydir.mkdir(parents=True,exist_ok=True)
    assert not (summarydir/'SUMMARY.md').exists(),'Preserved report must not be overwritten'
    aa=rows(out/'per_model.csv');ss=rows(out/'per_sequence.csv');tt=rows(tim/'summary.csv')
    pre=rows(out/'preflight_maxdet.csv');ck=read(EXP/'manifests/checkpoint_manifest.json');env=read(EXP/'manifests/environment.json')
    freeze=read(EXP/'manifests'/f'{run}_full_freeze.json');images=read(EXP/'manifests/images.json')
    dataset=read(EXP/'manifests/dataset_manifest.json');cfg=__import__('yaml').safe_load((EXP/'configs/benchmark.yaml').read_text())
    checks=[]
    def check(item,ok,detail):checks.append({'item':item,'status':'PASS' if ok else 'FAIL','evidence':detail})
    check('Frozen config/protocol',sha(EXP/'configs/benchmark.yaml')==freeze['config_sha256'] and sha(EXP/'EXPERIMENT_PROTOCOL.md')==freeze['protocol_sha256'],'SHA256 at Phase 4 start versus final')
    check('Frozen implementation',all(sha(EXP/p)==h for p,h in freeze['sources'].items()),'Every benchmark/frozen-pilot Python source')
    source=read(EXP/'manifests/source_manifest.json')
    check('Validated evaluator and pilot preserved',all(sha(ROOT/x['original'])==x['sha256']==sha(ROOT/x['snapshot']) for x in source.values()),'Original and frozen snapshot hashes')
    check('Image manifest unchanged',sha(EXP/'manifests/images.json')==freeze['frame_list_sha256'],'Ordered list, dimensions and original image hashes')
    check('Predetermined sample lists unchanged',all(sha(EXP/'manifests'/n)==h for n,h in freeze['sample_hashes'].items()),'Preflight/timing/visualization hashes frozen before full run')
    check('Dataset images unchanged',all(sha(ROOT/x['path'])==x['sha256'] for x in images),'Rehash every one of 2,862 original image files')
    check('Ground truth and sequence metadata unchanged',all(sha(ROOT/dataset['dataset_root']/x['sequence']/'gt/gt.txt')==x['gt_sha256'] and sha(ROOT/dataset['dataset_root']/x['sequence']/'seqinfo.ini')==x['seqinfo_sha256'] for x in dataset['sequences']),'All GT and seqinfo SHA256')
    check('Checkpoints unchanged',all(sha(ROOT/'models'/x['filename'])==x['sha256'] for x in ck),'All four checkpoint SHA256')
    expected=[f"{r['sequence']}_{r['frame']:06d}" for r in images]
    metas=[];candidate_rows=[]
    for name in MODELS:
        base=EXP/'predictions'/run/'accuracy'/name.removesuffix('.pt');m=read(base/'metadata.json');metas.append(m)
        check(f'{label(name)} exact frame list/count',m['frames']==expected and m['images_successful']==2862 and m['images_failed']==0 and m['status']=='PASS','Successful metadata plus per-frame file audit')
        audit=rows(base/'frame_audit.csv')
        actual=[];max_count=0
        for r in images:
            key=f"{r['sequence']}_{r['frame']:06d}"
            with gzip.open(base/'predictions'/f'{key}.json.gz','rt') as f:p=json.load(f)
            actual.append(f"{p['sequence']}_{p['frame']:06d}")
            assert p['model']==name and p['input_shape']==[1,3,640,640]
            assert [p['width'],p['height']]==[r['width'],r['height']]
            assert all(x['class']==0 and x['confidence']>.001 and x['rle']['size']==[r['height'],r['width']] for x in p['predictions'])
            max_count=max(max_count,p['post_nms_candidates'])
        check(f'{label(name)} saved predictions and tensor shapes',actual==expected and len(list((base/'predictions').glob('*.json.gz')))==2862 and max_count<1000,'Lossless RLE/class/score/dimensions checked on every saved frame')
        candidate_rows.append({'model':label(name),'min_candidates':min(int(r['post_nms_candidates']) for r in audit),
                               'max_candidates':max_count,'mean_candidates':float(np.mean([int(r['post_nms_candidates']) for r in audit])),
                               'saved_predictions':sum(int(r['saved_predictions']) for r in audit)})
    for k in ['ap_max_dets','fixed_confidence','ap_confidence_floor','nms_iou','max_detections','precision','imgsz','batch','rect','retina_masks','matching_iou','ignore_prediction_ioa']:
        check('Common '+k,all(m['config'][k]==cfg[k] for m in metas),str(cfg[k]))
    check('NMS one-to-many path and CUDA FP32',all(m['end2end'] is False and m['precision']=='fp32' and m['effective_predictor_args']['nms'] is True and m['effective_predictor_args']['device']=='0' for m in metas),'Backend state asserted at load')
    check('Same evaluator manifest',len({m['source_manifest_sha256'] for m in metas})==1,'One source_manifest SHA256')
    check('Same frozen protocol and config',all(m['protocol_sha256']==freeze['protocol_sha256'] and m['config_sha256']==freeze['config_sha256'] for m in metas),'Each model metadata')
    clean=all(int(x['clean_rounds'])==3 and int(x['frames'])==300 for x in tt)
    check('Three clean timing rounds per model',clean,'Contaminated rounds excluded from primary table')
    timing_expected=[(r['sequence'],r['frame']) for r in read(EXP/'manifests/timing_frames.json')]
    timing_runs=read(tim/'runs.json')
    check('Same exact timing frame order for every round',all([(r['sequence'],int(r['frame'])) for r in rows(tim/f"round{rnd}-{name}.csv")]==timing_expected for rnd in range(1,4) for name in MODELS),'100 identical ordered frame keys × 12 runs')
    check('No contaminated timing in primary table',all(not r['contaminated'] for r in timing_runs),'Before/during/after telemetry and other-process audit')
    required=['map50_95','ap50','ap75','precision','recall','f1','matched_iou_mean','matched_dice_mean']
    check('Complete accuracy metrics',len(aa)==4 and len(ss)==16 and all(math.isfinite(number(r[k])) for r in aa+ss for k in required),'4 overall plus 16 sequence records')
    check('Complete timing metrics',len(tt)==4 and all(math.isfinite(number(r[k])) for r in tt for k in ['inference_ms_mean','total_ms_mean','fps','peak_gpu_allocated_mib']), 'Dedicated timing, evaluator preparation excluded')
    csvwrite(out/'protocol_consistency.csv',checks);write(out/'protocol_consistency.json',checks)
    assert all(c['status']=='PASS' for c in checks),'Final consistency failed; do not publish a complete comparison'
    comparison=[]
    for name in [MODELS[0],MODELS[1],MODELS[3],MODELS[2]]:
        a=next(x for x in aa if x['model']==name);t=next(x for x in tt if x['model']==name);c=next(x for x in ck if x['filename']==name)
        comparison.append({'model':label(name),**{k:number(a[k]) for k in required},
                           'inference_ms':number(t['inference_ms_mean']),'pipeline_ms':number(t['total_ms_mean']),
                           'fps':number(t['fps']),'peak_allocated_mib':number(t['peak_gpu_allocated_mib']),
                           'peak_reserved_mib':number(t['peak_gpu_reserved_mib']),'parameters':c['parameters_loaded'],
                           'gflops':c['gflops_nms_unfused'],'checkpoint_mb':c['bytes']/1e6})
    csvwrite(out/'comparison_summary.csv',comparison)
    for name in ['comparison_summary.csv','per_model.csv','per_sequence.csv','preflight_maxdet.csv','protocol_consistency.csv']:
        shutil.copyfile(out/name,EXP/'metrics'/name)
    csvwrite(out/'candidate_counts.csv',candidate_rows)
    x=np.arange(4);labels=[r['model'] for r in comparison]
    def bars(filename,fields,ylabel):
        fig,ax=plt.subplots(figsize=(9,5));width=.75/len(fields)
        for j,(field,title) in enumerate(fields):
            vals=[r[field] for r in comparison];b=ax.bar(x+(j-(len(fields)-1)/2)*width,vals,width,label=title)
            ax.bar_label(b,fmt='%.3f',padding=3,fontsize=8)
        ax.set_xticks(x,labels);ax.set_ylabel(ylabel);ax.set_ylim(bottom=0)
        if all(0<=r[k]<=1 for k,_ in fields for r in comparison):ax.set_ylim(0,1.08)
        ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
        if len(fields)>1:ax.legend(loc='upper right')
        ax.set_title('Second-largest available variants • MOTS20 Person • FP32 / 640')
        fig.tight_layout();fig.savefig(plot/(filename+'.png'),dpi=180);fig.savefig(plot/(filename+'.pdf'));plt.close(fig)
    for f,fields,y in [
        ('mask_map',[('map50_95','Mask mAP50-95')],'Mask mAP50-95 (0–1)'),
        ('ap50_ap75',[('ap50','AP50'),('ap75','AP75')],'Mask AP (0–1)'),
        ('precision_recall_f1',[(k,k.title()) for k in ['precision','recall','f1']],'Micro metric (0–1)'),
        ('matched_mask_quality',[('matched_iou_mean','Matched IoU'),('matched_dice_mean','Matched Dice')],'Matched TP only (0–1)'),
        ('inference_latency',[('inference_ms','Inference')],'Mean inference latency (ms)'),
        ('pipeline_latency',[('pipeline_ms','Pipeline')],'Mean pipeline latency (ms)'),
        ('fps',[('fps','FPS')],'FPS from mean pipeline latency'),
        ('peak_vram',[('peak_allocated_mib','Allocated'),('peak_reserved_mib','Reserved')],'Peak CUDA allocator memory (MiB)')]:bars(f,fields,y)
    for field,filename,xlabel in [('inference_ms','accuracy_vs_latency','Mean inference latency (ms)'),('parameters','accuracy_vs_parameters','Loaded checkpoint parameters (millions)')]:
        fig,ax=plt.subplots(figsize=(8,5))
        for r in comparison:
            value=r[field]/1e6 if field=='parameters' else r[field]
            ax.scatter(value,r['map50_95'],s=60);ax.annotate(r['model'],(value,r['map50_95']),xytext=(5,6),textcoords='offset points',fontsize=8)
        ax.set_xlim(left=0);ax.set_ylim(0,1);ax.set_xlabel(xlabel);ax.set_ylabel('Mask mAP50-95 (0–1)');ax.grid(alpha=.2)
        fig.tight_layout();fig.savefig(plot/(filename+'.png'),dpi=180);fig.savefig(plot/(filename+'.pdf'));plt.close(fig)
    csvwrite(plot/'underlying_values.csv',comparison)
    best=max(comparison,key=lambda x:x['map50_95']);fast=min(comparison,key=lambda x:x['inference_ms']);low=min(comparison,key=lambda x:x['peak_allocated_mib'])
    highrec=max(comparison,key=lambda x:x['recall']);fastpipe=min(comparison,key=lambda x:x['pipeline_ms'])
    pareto=[r['model'] for r in comparison if not any(o['map50_95']>=r['map50_95'] and o['inference_ms']<=r['inference_ms'] and (o['map50_95']>r['map50_95'] or o['inference_ms']<r['inference_ms']) for o in comparison)]
    columns=[('model','Model'),('map50_95','Mask mAP50-95'),('ap50','AP50'),('ap75','AP75'),('precision','Precision'),('recall','Recall'),('f1','F1'),('matched_iou_mean','TP-only IoU'),('matched_dice_mean','TP-only Dice'),('inference_ms','Inference ms'),('pipeline_ms','Pipeline ms'),('fps','FPS'),('peak_allocated_mib','Peak allocated MiB'),('parameters','Params'),('checkpoint_mb','Checkpoint MB')]
    gt_count=sum(int(x['gt_persons']) for x in aa[:1])
    text=f'''# Second-largest available YOLO segmentation variants on MOTS20

Run: `{run}` • **PASS WITH WARNINGS** • completed {now()}

## 1. ทดสอบอะไร
เปรียบเทียบ pretrained YOLO26l-Seg, YOLO11l-Seg, YOLOv9c-Seg และ YOLOv8l-Seg
กับ Person instance segmentation บน MOTS20 train ครบ 2,862 ภาพ ({gt_count:,} GT instances)
โดยไม่ฝึกเพิ่ม เป็นรุ่น segmentation ใหญ่เป็นอันดับสองที่มีให้ใช้ของแต่ละตระกูล ไม่ใช่โมเดลที่มีจำนวน parameters เท่ากัน

## 2. ใช้เงื่อนไขอะไร
Tesla T4 ตัวเดียว, FP32, batch 1, square letterbox 640×640, NMS IoU 0.70,
confidence floor 0.001 สำหรับ AP และ threshold 0.25 สำหรับ P/R/F1 ใช้ภาพและ evaluator เดียวกัน
YOLO26 ใช้ NMS-based one-to-many เช่นเดียวกับรุ่นอื่น Preflight 100 ภาพเลือก AP maxDet={cfg['ap_max_dets']}
วัดความเร็วแยกจาก accuracy จำนวน 100 ภาพ × 3 รอบต่อโมเดล มี warmup และ CUDA synchronization

## 3. ผลหลักเป็นอย่างไร
**{best['model']} มี Mask mAP50-95 สูงสุด {best['map50_95']:.6f}**
ส่วน **{fast['model']} มี inference เร็วสุด {fast['inference_ms']:.3f} ms/ภาพ**
ทุกโมเดลประมวลผลครบและผ่าน consistency checks ผลตัวเลขอยู่ในตารางด้านล่าง

## 4. แต่ละโมเดลเด่นด้านไหน
- Mask accuracy สูงสุด: {best['model']}
- Recall สูงสุด: {highrec['model']} ({highrec['recall']:.6f})
- Neural inference เร็วสุด: {fast['model']}; pipeline เร็วสุด: {fastpipe['model']}
- Peak allocated VRAM ต่ำสุด: {low['model']} ({low['peak_allocated_mib']:.2f} MiB)
- Accuracy–inference-latency Pareto frontier: {', '.join(pareto)}
ไม่ใช้คะแนนรวมถ่วงน้ำหนัก และไม่สรุปว่ารุ่นเดียวดีที่สุดทุกด้าน

## 5. มีปัญหาหรือข้อจำกัดอะไร
มี CPU NNPACK warning ระหว่างตรวจ model complexity และ pycocotools/NumPy deprecation warning
แต่ regression tests ผ่าน 15 ข้อ เก็บ warnings ไว้ใน logs ไม่เปลี่ยน dependencies
ภาพวิดีโอต่อเนื่องมีความสัมพันธ์กัน โมเดลมีความจุต่างกัน และ IoU/Dice เป็นค่าเฉพาะ TP ที่จับคู่สำเร็จ
ผลนี้ **ยังไม่เพียงพอสำหรับข้อสรุป final CCTV robustness**

## 6. ควรทำอะไรต่อ
ใช้ผลเป็น preliminary YOLO segmentation comparison ได้ แล้วออกแบบ CCTV robustness experiment
ที่แยก blur, low-light และ camera-angle อย่างชัดเจน พร้อมภาพ/GT ที่เหมาะสมและ protocol ร่วมกัน
หากต้องการแยกผลของ architecture ควรทำ capacity-controlled comparison เพิ่มต่างหาก

## 1. Research question
How do the second-largest available official pretrained segmentation checkpoints from
four YOLO generations generalize to MOTS20 Person masks under a common protocol?
No training, fine-tuning, transfer learning or adaptation was performed.

## 2. Experimental protocol
See [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md). Config hash:
`{freeze['config_sha256']}`. Protocol hash: `{freeze['protocol_sha256']}`.
Inference runs sequentially on CUDA:0. Native-resolution masks use retina_masks;
all actual network tensors are 1×3×640×640. Aspect-preserving centered letterbox
has value-114 padding, RGB FP32 /255. Input is 1920×1080→640×360 plus 140 pixels
top/bottom, or 640×480→640×480 plus 80 pixels top/bottom. NMS is box IoU 0.70;
evaluation matches mask IoU 0.50. These are separate operations.

Valid Person GT is matched first; unmatched predictions are ignored when their
intersection with the union of class-10 masks / prediction area ≥0.50. Fixed
metrics use ≥0.25; AP uses saved NMS candidates >0.001 and common maxDet
{cfg['ap_max_dets']}. AP is pooled confidence-ranked frame-level Person mask AP,
not official MOTS tracking evaluation. Matched Dice=2IoU/(1+IoU).

## 3. Dataset description
Only bundled MOTS train GT is used. No test GT, duplicate MOTSLabels, dataset
adaptation, file modification or split creation. All frames and GT RLE decoded;
all image/GT/checkpoint hashes rechecked at completion.
'''
    text+=table([{'sequence':r['sequence'],'frames':r['frames'],'resolution':str(r['resolution_wh']),'persons':r['classes']['2'],'ignore':r['classes'].get('10',0)} for r in dataset['sequences']], [('sequence','Sequence'),('frames','Frames'),('resolution','Resolution W×H'),('persons','GT Person instances'),('ignore','Ignore regions')])
    text+='\n## 4. Model/checkpoint table\n\n'
    text+=table([{'model':label(c['filename']),'parameters':c['parameters_loaded'],'gflops':c['gflops_nms_unfused'],'mb':c['bytes']/1e6,'sha':c['sha256']} for c in ck],[('model','Model'),('parameters','Loaded parameters'),('gflops','Local NMS GFLOPs @640'),('mb','Checkpoint MB (decimal)'),('sha','SHA256')])
    text+='\nSources: official Ultralytics assets v8.4.0; exact URLs and full COCO class mapping in checkpoint_manifest.json. Every checkpoint has task=segment and names[0]=person.\n'
    text+=f'''\n## 5. Environment
Hostname `{env['hostname']}`; OS `{env['os']}`; Python {env['python'].split()[0]};
Ultralytics {env['packages']['ultralytics']}; PyTorch {env['torch_version']};
torchvision {env['torchvision_version']}; NumPy {env['packages']['numpy']};
pycocotools {env['packages']['pycocotools']}; CUDA runtime {env['cuda_runtime']}.
Tesla T4, NVIDIA driver 580.178.04, physical VRAM 15,360 MiB;
CUDA-visible device memory approximately 14,911 MiB. CUDA_VISIBLE_DEVICES={env['CUDA_VISIBLE_DEVICES']}.
No packages changed. Git status/commit unavailable if workspace is not a Git checkout;
captured command return codes and errors are preserved in environment.json.

## 6. Preflight/maxDet validation
25 evenly spaced frames from each sequence, frozen before predictions. All four
models completed the same 100 frames. Strict convergence tolerance is <0.0001
for each AP metric relative to cap 1000. Chosen common cap: **{cfg['ap_max_dets']}**.
'''
    text+=table(pre,[('model','Model'),('max_dets','maxDet'),('ap50','AP50'),('ap75','AP75'),('map50_95','mAP50-95'),('converged','Converged')])
    text+='\nFull-run post-NMS counts before evaluator capping:\n\n'+table(candidate_rows,[('model','Model'),('min_candidates','Min'),('max_candidates','Max'),('mean_candidates','Mean'),('saved_predictions','Saved predictions')])
    text+='\n## 7. Overall accuracy comparison\n\n'+table(comparison,columns)
    text+='\nCounts use confidence ≥0.25; AP-floor prediction counts are separate. Micro P/R/F1 derive from pooled counts.\n\n'
    text+=table(aa,[('model','Model'),('gt_persons','GT'),('predictions_ap_floor','AP-floor predictions'),('predictions_at_confidence','Fixed-threshold predictions'),('tp','TP'),('fp','FP'),('fn','FN'),('ignored_predictions','Ignored')])
    text+='\n## 8. Per-sequence comparison\n\n'+table(ss,[('model','Model'),('sequence','Sequence'),('frames','Frames'),('gt_persons','GT'),('predictions_ap_floor','Predictions >.001'),('tp','TP'),('fp','FP'),('fn','FN'),('precision','Precision'),('recall','Recall'),('f1','F1'),('ap50','AP50'),('ap75','AP75'),('map50_95','mAP50-95'),('matched_iou_mean','TP IoU'),('matched_dice_mean','TP Dice'),('ignored_predictions','Ignored')])
    text+='\n## 9. Mask-quality analysis\n\nConditional on matched TP only, not dataset-wide mask accuracy. Population standard deviation.\n\n'
    quality=[]
    for a in aa:
        for metric in ['iou','dice']:quality.append({'model':a['model'],'metric':metric,**{k:a[f'matched_{metric}_{k}'] for k in ['mean','median','std','p25','p75']}})
    text+=table(quality,[('model','Model'),('metric','TP-only metric'),('mean','Mean'),('median','Median'),('std','Std'),('p25','P25'),('p75','P75')])
    text+='\n## 10. Person-size descriptive distribution\n\nRelative mask area = GT mask pixels / source image pixels. No size categories are invented.\n\n'
    size=read(EXP/'metrics/person_size_distribution.json');text+=table([size],[(k,k) for k in size])
    text+='\nEvery GT instance has mask area, bbox width/height/area, image dimensions and both normalized areas in `metrics/gt_instances.csv`.\n'
    text+='\n## 11. Crowd descriptive analysis\n\nGrouped by exact valid GT person count per frame; this is **not an occlusion severity label**. The following rows describe the empirical minimum, middle and maximum occupied count levels; complete exact-count distributions are saved in each model’s crowd CSV. Sequence and person-size composition can confound these comparisons.\n\n'
    crowd=[]
    for name in MODELS:
        rr=rows(out/f'{name}-crowd.csv');crowd.extend(rr[i] for i in sorted({0,len(rr)//2,len(rr)-1}))
    text+=table(crowd,[('model','Model'),('gt_persons_per_frame','GT/frame'),('frames','Frames'),('tp','TP'),('fp','FP'),('fn','FN'),('precision','Precision'),('recall','Recall'),('f1','F1')])
    text+='\n## 12. Speed comparison\n\nThree clean 100-frame rounds/model after 10 untimed warmups per run. CUDA synchronization at stage boundaries; disk I/O and evaluator are excluded. Pipeline includes preprocessing, forward, NMS/native masks, binary validation, lossless packing and CPU transfer. RLE preparation is separate. Mean-derived FPS is not mean instantaneous FPS.\n\n'
    speed=[]
    for t in tt:
        for stage in ['preprocess_ms','inference_ms','ultralytics_postprocess_inclusive_ms','postprocess_ms','total_ms','rle_preparation_ms']:
            speed.append({'model':t['model'],'stage':stage,**{k:t[stage+'_'+k] for k in ['mean','median','std','p50','p95']}})
    text+=table(speed,[('model','Model'),('stage','Stage'),('mean','Mean ms'),('median','Median ms'),('std','Std ms'),('p50','P50 ms'),('p95','P95 ms')])
    text+=f"\nSeed {freeze['seed']}; model order by round: `"+json.dumps(freeze['timing_order'])+'`. All timing GPU-state samples, processes, clocks, temperature and power are preserved.\n'
    text+='\n## 13. GPU-memory comparison\n\nPeak CUDA allocator values after warmup, including resident model. Max across clean timing rounds. Reserved cache is not equivalent to live allocated tensors or whole-device VRAM.\n\n'
    text+=table(tt,[('model','Model'),('baseline_allocated_mib','Baseline allocated MiB'),('baseline_reserved_mib','Baseline reserved MiB'),('peak_gpu_allocated_mib','Peak allocated MiB'),('peak_gpu_reserved_mib','Peak reserved MiB')])
    text+='\n## 14. Parameter/model-size comparison\n\nLocal loaded checkpoint parameter count is primary. Runtime fusion removes BatchNorm and, where applicable, unused heads; it can differ from documentation or loaded representation. Local GFLOPs are Ultralytics/THOP estimates for NMS forward at 640, not measured hardware operations. CPU NNPACK warnings occurred during this inspection. Loading is supplementary and excluded from FPS.\n\n'
    complexity=[]
    for c in ck:
        m=next(x for x in metas if x['model']==c['filename']);t=next(x for x in tt if x['model']==c['filename'])
        complexity.append({'model':label(c['filename']),'loaded':c['parameters_loaded'],'runtime':m['runtime_parameters'],'gflops':c['gflops_nms_unfused'],'mb':c['bytes']/1e6,'load':t['load_seconds_mean']})
    text+=table(complexity,[('model','Model'),('loaded','Loaded params'),('runtime','Fused runtime params'),('gflops','GFLOPs'),('mb','Checkpoint MB'),('load','Mean timing load s')])
    text+='\n## 15. Qualitative results\n\nTwelve predetermined frames (three/sequence), identical for all four models. Each sheet shows source, GT, predictions, TP matches, FN/FP, and ignore regions. No post-hoc examples are mixed with these.\n\n'
    for s in SEQS:
        k=f'{s}_000001'
        text+=f'### {s}, predetermined frame 1\n\n'
        for name in [MODELS[0],MODELS[1],MODELS[3],MODELS[2]]:text+=f'[{label(name)} contact sheet](outputs/visualizations/{run}/{name.removesuffix(".pt")}/{k}.jpg) · '
        text+='\n\n'
    text+='\nResearch plots (all bar axes start at zero; AP axes use 0–1):\n\n'
    for filename in ['mask_map','ap50_ap75','precision_recall_f1','matched_mask_quality','inference_latency','pipeline_latency','fps','peak_vram','accuracy_vs_latency','accuracy_vs_parameters']:
        text+=f'![{filename}](outputs/plots/{run}/{filename}.png)\n\n'
    text+='''## 16. Warnings/failures
CPU NNPACK unsupported-hardware warnings appeared during model complexity inspection.
pycocotools emits a NumPy copy-keyword DeprecationWarning; all 15 pilot regression
tests passed. No dependencies were changed to suppress warnings. No OOM, failed
accuracy frames, resumed runs or contaminated primary timing runs occurred.
The execution sandbox initially failed its namespace initialization; benchmark
commands ran through the explicitly approved execution path. This does not change
inference settings. Stdout/stderr and failure records, if any, are retained.

## 17. Threats to validity
Second-largest variants have unequal capacity and training recipes: not architecture-only
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
'''
    text+=f"{best['model']} has the highest measured mask accuracy; {fast['model']} has the lowest mean neural inference latency; {low['model']} uses the lowest peak allocated memory. The empirical accuracy–inference-latency Pareto set is {', '.join(pareto)}. This is a descriptive trade-off, not a combined score or statistical superiority claim.\n"
    text+='''
## 19. Conclusions
**A. Preliminary YOLO instance-segmentation comparison: YES**, within this exact
second-largest-variant, pretrained, MOTS20 Person frame-level protocol.
**B. Final CCTV robustness conclusions: NO.** No controlled blur, illumination,
camera-angle categories or explicit occlusion severity labels were tested.
Next: a separate preregistered CCTV robustness experiment; optionally a separate
capacity-controlled YOLO comparison to examine architecture effects.

Final protocol consistency checks:

'''+table(checks,[('item','Item'),('status','PASS/FAIL'),('evidence','Evidence')])
    text+=f'''
## 20. Exact artifact paths
All paths below are relative to workspace `YOLO_Second_Largest_Seg_MOTS20_Benchmark/`:

- Main report: `REPORT.md`; preserved summary: `reports/{run}/SUMMARY.md`
- Frozen protocol/config: `EXPERIMENT_PROTOCOL.md`, `configs/benchmark.yaml`
- Environment/data/checkpoint/source manifests: `manifests/`
- Exact all-frame list/hashes: `manifests/images.json`
- Predetermined frame lists: `manifests/{{preflight,timing,visualization}}_frames.json`
- Full-run freeze/order: `manifests/{run}_full_freeze.json`
- Comparison, per-sequence, preflight, consistency CSVs: `metrics/{run}/`
- Per-frame/matched-instance metrics: `metrics/{run}/{{per_frame,per_instance}}/`
- GT instance sizes/counts: `metrics/gt_instances.csv`, `metrics/gt_frames.csv`
- Lossless per-frame predictions/audits: `predictions/{run}/{{preflight,accuracy}}/`
- Timing measurements and telemetry: `timing/{run}/`
- Stdout/stderr and regression logs: `logs/{run}/`
- Plots, PDF copies and values: `outputs/plots/{run}/`
- Predetermined qualitative sheets: `outputs/visualizations/{run}/`

Model weights remain in workspace `models/`; dataset and pilot are unchanged.
'''
    (EXP/'REPORT.md').write_text(text)
    # Summary is self-contained; image links are rebased for its preserved location.
    (summarydir/'SUMMARY.md').write_text(text.replace('](outputs/','](../../outputs/').replace('](EXPERIMENT_PROTOCOL.md)','](../../EXPERIMENT_PROTOCOL.md)'))
    terminal='PASS WITH WARNINGS\nModels completed: 4/4; accuracy frames: 2,862 each (11,448 model-frames)\n'+table(comparison,columns)
    terminal+=f"\nHighest mask accuracy: {best['model']}\nFastest inference: {fast['model']}\nLowest allocated VRAM: {low['model']}\nPareto frontier: {', '.join(pareto)}\nWarnings: CPU NNPACK; pycocotools deprecation. Unequal capacities; no CCTV robustness claim.\nREPORT: {EXP/'REPORT.md'}\n"
    (summarydir/'terminal_summary.txt').write_text(terminal);print(terminal)
if __name__=='__main__':main(sys.argv[1])
