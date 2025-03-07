<p align="center">
<img src="https://github.com/user-attachments/assets/620dfa36-aab8-44d8-be5d-37d5e8e427ca" width="75%" height="auto">
</p>


This is the anonymous repository corresponding to the ICCV 2025 submission: "Surg-3M: A Dataset and Foundation Model for Perception in Surgical Settings". **This repository is intended for ICCV 2025 reviewers only.**


## 🔥🔥🔥 Surg-3M Dataset
You can download Surg-3M dataset and SurgFM foundation model by [this link](https://mega.nz/folder/GVkgDQKZ). 
**The password to decrypt it is included in the first section of the supplementary material submitted for review.**

The video annotation file can be downloaded here: [labels.json](https://github.com/anonymous-8989/sub8989/blob/main/labels.json)

### 🎥 Demo


<div align="center">
  <img src="https://github.com/user-attachments/assets/79f25335-6d8c-4b9b-afe1-59cfd5c84a39" width="70%" > </img>
</div>



### 🛠️ Dependencies and Installation
Install the following dependencies in your local setup:

   ```bash
   $ git clone git@github.com:anonymous-8989/sub8989.git
   $ cd sub8989 && pip install -r requirements.txt
   ```


### 🔗 Load Dataset

Using the following code to load the Surg-3M dataset LMDB and its annotation file:
```python
from surgfm.utils_timeSequenceAndKnn.py import Dataset
import lmdb
import json

# Load annotation
with open('labels.json', 'r') as file:
   annotation = json.load(file)
for video in annotation:
   video_id = video['youtubeId']
   procedure_type = video['procedureName']
   surgery_type = 'robotic' if video['robotic'] else 'non-robotic'


# Load Surg-3M dataset
# Open the LMDB environment in read-only mode
env = lmdb.open('lmdb_path', readonly=True, lock=False, readahead=False)
with env.begin() as txn:
   cursor = txn.cursor()
   for key, value in tqdm(cursor, total = txn.stat()['entries']):
        # Decode the image name from bytes to string
        img_name = key.decode('utf-8')
        img_array = np.frombuffer(value, dtype=np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

```

## 🎉🎉🎉 Surg-FM Foundation Model

You can download the SurgFM checkpoint within the provided link with the password.

### 🛠️ SurgFM Training

Follow the provided scripts to launch your own SurgFM training.

```bash
$ python3 -m torch.distributed.run --nproc_per_node=8 --nnodes=1 surgfm/surgfm.py --arch convnext_large --data_path 'Surg-3M dataset lmdb path' --output_dir 'your path to store the trained foundation model' --batch_size_per_gpu 40 --num_workers 10
```

### 🚀 SurgFM inference
The code below shows how to run our Surg-FM foundation model to get a feature vector for any given surgical video frame:

   ```python
   import torch
   from PIL import Image
   from src.model_loader import build_SurgFM

   # Load the pre-trained SurgFM model
   surgfm = build_SurgFM(pretrained_weights = 'your path to the SurgFM')
   surgfm.eval()

   # Load the image and convert it to a PyTorch tensor
   img_path = 'path/to/your/image.jpg'
   img = Image.open(img_path)
   img = img.resize((224, 224))
   img_tensor = torch.tensor(np.array(img)).unsqueeze(0).to('cuda')

   # Extract features from the image using the ResNet50 model
   outputs = surgfm(img_tensor)
   ```




## 🏃‍♂️🏃‍♂️🏃‍♂️ Recreate Surg-3M dataset From Scratch

Alternatively, you can recreate our Surg-3M dataset from scratch


### 🧱 Data Curation Pipeline

You can use our code of the data curation pipeline and provided annotation file (["*labels.json*"](https://github.com/anonymous-8989/sub8989/blob/main/labels.json)) to recreate the whole Surg-3M dataset.

1. Get your Youtube cookie:

   You need to provide a "cookies.txt" file if you want to download videos that require Youtube login. 

   Use the [cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp) extension to export your Youtube cookies as "cookies.txt".


2. Download the annotation file (["*labels.json*"](https://github.com/anonymous-8989/sub8989/blob/main/labels.json)) and use the video downloader to download the original selected Youtube videos.

   ```bash
   $ python3 src/video_downloader.py --video-path '../labels.json' --output 'your path to store the downloaded videos' --cookies 'your YouTube cookie file'
   ```

3. Curate the downloaded original videos as Surg-3M video dataset. In detail, use the video_processor to classify each frame as either 'surgical' or 'non-surgical', then remove the beginning and end segments of non-surgical content from the videos, and mask the non-surgical regions in 'surgical' frames and the entire 'non-surgical' frames.

   ```bash
   $ python3 src/video_processor.py --input 'your original downloaded video storage path' --input-json '../labels.json' --output 'your path to store the curated videos and their corresponding frame annotation files' --classify-models 'frame classification model' --segment-models 'non-surgical object detection models'
   ```

4. Process the Surg-3M video dataset as Surg-3M image dataset (For foundation model pre-training).

   ```bash
   $ python3 src/create_lmdb.py --video-folder 'your directory containing the curated videos and their corresponding frame annotation files' --output-json 'your path for the json file to verify the videos and labels alignment' --lmdb-path 'your lmdb storage path'
   ```
