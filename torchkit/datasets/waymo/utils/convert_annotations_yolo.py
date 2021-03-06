# ==================================================================== #
# File name: convert_annotations_yolo.py
# Author: Long H. Pham
# Date created: 08/02/2021
# The `torchkit.datasets.waymo.utils.convert_annotations_yolo` implements
# the utility functions to convert raw annotation files to yolo format.
# ==================================================================== #
import glob
import multiprocessing
import os

import numpy as np
from joblib import delayed
from joblib import Parallel
from tqdm import tqdm

from torchkit.core.data.image_info import ImageInfo
from torchkit.core.fileio import create_dirs
from torchkit.core.image import bbox_cxcywh_cxcywh_norm
from torchkit.utils import datasets_dir

# splits = ["train", "val"]
splits = ["train"]

for split in splits:
	annotation_pattern = os.path.join(datasets_dir, "waymo", "detection2d", split, "*", "annotations", "*.txt")
	annotation_paths   = glob.glob(annotation_pattern)
	
	new_annotation_dirs = [
		os.path.join(datasets_dir, "waymo", "detection2d", split, "front",       "annotations_yolo"),
		os.path.join(datasets_dir, "waymo", "detection2d", split, "front_left",  "annotations_yolo"),
		os.path.join(datasets_dir, "waymo", "detection2d", split, "front_right", "annotations_yolo"),
		os.path.join(datasets_dir, "waymo", "detection2d", split, "side_left",   "annotations_yolo"),
		os.path.join(datasets_dir, "waymo", "detection2d", split, "side_right",  "annotations_yolo")
	]
	create_dirs(paths=new_annotation_dirs, recreate=True)
	
	
	def process(path):
		# name                = Path(path).name
		image_path          = path.replace("annotations", "images")
		image_path          = image_path.replace(".txt", ".jpeg")
		image_info          = ImageInfo.from_image_file(image_path=image_path)
		shape0              = image_info.shape0
		new_annotation_path = path.replace("annotations", "annotations_yolo")
			
		# for d in new_annotation_dirs:
		# 	open(os.path.join(d, name), "w")
				
		with open(path, "r") as fi:
			labels = np.array([line.split() for line in fi.read().splitlines()], dtype=np.float32)
			
		with open(new_annotation_path, "w") as fo:
			for l in labels:
				bbox = bbox_cxcywh_cxcywh_norm(l[2:6], shape0[0], shape0[1])
				ss   = f"{int(l[1])} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n"
				fo.writelines(ss)
	
	
	num_jobs = multiprocessing.cpu_count()
	Parallel(n_jobs=num_jobs)(
		delayed(process)(path) for path in tqdm(annotation_paths, desc=f"{split}")
	)
