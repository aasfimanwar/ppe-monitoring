import subprocess
subprocess.run(['pip', 'install', 'ultralytics', '-q'])

import os, zipfile, yaml, shutil
from ultralytics import YOLO
import torch

print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU!')

# ── Find the dataset ──────────────────────────────────────────────────────────
# Check which dataset is available
input_dir = '/kaggle/input'
print('Available datasets:')
for d in os.listdir(input_dir):
    print(' ', d)

# Find the zip file automatically
zip_path = None
for root, dirs, files in os.walk(input_dir):
    for f in files:
        if f.endswith('.zip') and 'ppe' in f.lower():
            zip_path = os.path.join(root, f)
            print(f'Found zip: {zip_path}')
            break

# If no zip, dataset may already be extracted
extract_path = '/kaggle/working/dataset'
if zip_path:
    print('Extracting dataset...')
    os.makedirs(extract_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_path)
    print('Extraction complete!')
else:
    # Copy from input directly
    print('No zip found - using input directory directly')
    extract_path = input_dir

# ── Find image folders ────────────────────────────────────────────────────────
train_path = valid_path = test_path = None
for root, dirs, files in os.walk(extract_path):
    if os.path.basename(root) == 'images':
        parent = os.path.basename(os.path.dirname(root))
        if parent == 'train': train_path = root
        elif parent in ['valid','val']: valid_path = root
        elif parent == 'test': test_path = root

print(f'Train : {train_path}')
print(f'Valid : {valid_path}')
print(f'Test  : {test_path}')

def count(p):
    if not p or not os.path.exists(p): return 0
    return len([f for f in os.listdir(p) if f.lower().endswith(('.jpg','.jpeg','.png'))])

print(f'Train images : {count(train_path):,}')
print(f'Valid images : {count(valid_path):,}')
print(f'Test images  : {count(test_path):,}')

# ── Create data.yaml ──────────────────────────────────────────────────────────
yaml_path = '/kaggle/working/data.yaml'
with open(yaml_path, 'w') as f:
    yaml.dump({
        'train': train_path,
        'val':   valid_path,
        'test':  test_path,
        'nc':    14,
        'names': ['Fall-Detected','Gloves','Goggles','Hardhat','Ladder','Mask',
                  'NO-Gloves','NO-Goggles','NO-Hardhat','NO-Mask','NO-Safety Vest',
                  'Person','Safety Cone','Safety Vest']
    }, f, default_flow_style=False)

print('data.yaml saved!')

# ── Train ─────────────────────────────────────────────────────────────────────
print('Starting training...')
model = YOLO('yolov8s.pt')

results = model.train(
    data        = yaml_path,
    epochs      = 50,
    imgsz       = 640,
    batch       = 32,
    device      = '0,1',
    project     = '/kaggle/working/runs',
    name        = 'ppe_final',
    patience    = 15,
    save        = True,
    save_period = 5,
    plots       = True,
    exist_ok    = True,
    workers     = 4,
)

# Emergency save — run this any time to save current best
import shutil, os, glob

print('Checkpoints available:')
for pt in sorted(glob.glob('/kaggle/working/runs/**/*.pt', recursive=True)):
    size = os.path.getsize(pt) / (1024*1024)
    print(f'  {pt} ({size:.1f} MB)')

# Copy best to output root for easy download
best = '/kaggle/working/runs/ppe_final/weights/best.pt'
if os.path.exists(best):
    shutil.copy(best, '/kaggle/working/ppe_best.pt')
    print('Saved ppe_best.pt to output!')
# ── Results ───────────────────────────────────────────────────────────────────
m = results.results_dict
print('=' * 50)
print('TRAINING COMPLETE!')
print(f"mAP50     : {round(m.get('metrics/mAP50(B)', 0) * 100, 1)} %")
print(f"Precision : {round(m.get('metrics/precision(B)', 0) * 100, 1)} %")
print(f"Recall    : {round(m.get('metrics/recall(B)', 0) * 100, 1)} %")
print('=' * 50)

# ── Save to output ────────────────────────────────────────────────────────────
best_src = '/kaggle/working/runs/ppe_final/weights/best.pt'
best_dst = '/kaggle/working/ppe_best.pt'
shutil.copy(best_src, best_dst)
print(f'Model saved to output: {best_dst}')
print('Go to Output tab on the right to download ppe_best.pt')