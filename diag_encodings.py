import os, pickle
import config

folders = []
if os.path.isdir(config.DATASET_DIR):
    folders = [f for f in os.listdir(config.DATASET_DIR) if os.path.isdir(os.path.join(config.DATASET_DIR,f))]
print('dataset folders:', len(folders))
for f in folders[:20]:
    print(' -', f)
try:
    with open(config.ENCODINGS_FILE,'rb') as f:
        enc, names = pickle.load(f)
    print('encodings:', len(enc), 'entries; unique students in names:', len(set(names)))
    # show first few student names
    print('students sample:', list(dict.fromkeys(names))[:20])
except Exception as e:
    print('encodings error:', e)
