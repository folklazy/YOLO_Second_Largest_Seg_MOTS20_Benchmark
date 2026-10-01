"""Preserve Experiment 1 report/check implementation with explicit tier substitutions."""
from pathlib import Path
EXP = Path(__file__).resolve().parents[1]
PREV = EXP.parent / 'YOLO_Large_Seg_MOTS20_Benchmark'

def main():
    source = (PREV / 'src/report.py').read_text()
    substitutions = {
        'yolo26x': 'yolo26l', 'yolo11x': 'yolo11l', 'yolov8x': 'yolov8l', 'yolov9e': 'yolov9c',
        'YOLO26x': 'YOLO26l', 'YOLO11x': 'YOLO11l', 'YOLOv8x': 'YOLOv8l', 'YOLOv9e': 'YOLOv9c',
        "tim=EXP/'timing'/run;": "tim=EXP/'timing'/run/'clean_repetition';",
        'YOLO_Large_Seg_MOTS20_Benchmark/': 'YOLO_Second_Largest_Seg_MOTS20_Benchmark/',
        'Largest available': 'Second-largest available',
        'largest officially available': 'second-largest available official',
        'Largest variants': 'Second-largest variants',
        'largest-variant, pretrained': 'second-largest-variant, pretrained',
        'เป็นรุ่น segmentation ใหญ่ที่สุด': 'เป็นรุ่น segmentation ใหญ่เป็นอันดับสองที่มีให้ใช้',
    }
    for before, after in substitutions.items(): source = source.replace(before, after)
    destination = EXP / 'src/report_base.py'
    assert not destination.exists()
    destination.write_text(source)
    print('Report consistency checks and plots copied from Experiment 1; tier names and clean timing paths updated.')

if __name__ == '__main__': main()
