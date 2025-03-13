import os
import torch
import numpy as np
from flask import Flask, request, jsonify, send_file
from PIL import Image
import io

import detectron2
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2.utils.visualizer import ColorMode

# Initialize Flask App
app = Flask(__name__)

# Define Model Path
MODEL_PATH = "model_final.pth"

# Detectron2 Configuration
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.6
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
cfg.MODEL.WEIGHTS = MODEL_PATH

# Set device (CPU if no GPU available)
cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize Model
predictor = DefaultPredictor(cfg)

# Metadata
metadata = MetadataCatalog.get("car_dataset_val")
metadata.thing_classes = ["damage"]

# Segmentation Merging Function
def merge_segment(pred_segm):
    merge_dict = {}
    for i in range(len(pred_segm)):
        merge_dict[i] = []
        for j in range(i + 1, len(pred_segm)):
            if torch.sum(pred_segm[i] * pred_segm[j]) > 0:
                merge_dict[i].append(j)

    to_delete = []
    for key in merge_dict:
        for element in merge_dict[key]:
            to_delete.append(element)

    for element in to_delete:
        merge_dict.pop(element, None)

    empty_delete = [key for key in merge_dict if merge_dict[key] == []]
    for element in empty_delete:
        merge_dict.pop(element, None)

    for key in merge_dict:
        for element in merge_dict[key]:
            pred_segm[key] += pred_segm[element]

    except_elem = list(set(to_delete))
    new_indexes = list(range(len(pred_segm)))
    for elem in except_elem:
        new_indexes.remove(elem)

    return pred_segm[new_indexes]

# Prediction Function
def inference(image):
    img = np.array(image)
    outputs = predictor(img)
    out_dict = outputs["instances"].to("cpu").get_fields()

    new_inst = detectron2.structures.Instances((1024, 1024))
    new_inst.set("pred_masks", merge_segment(out_dict["pred_masks"]))

    visualizer = Visualizer(img[:, :, ::-1], metadata=metadata, scale=0.5, instance_mode=ColorMode.SEGMENTATION)
    out = visualizer.draw_instance_predictions(new_inst)

    return Image.fromarray(out.get_image()[:, :, ::-1])

# Flask API Endpoint for Prediction
@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    image = Image.open(file.stream).convert("RGB")
    
    segmented_image = inference(image)

    # Convert image to bytes for response
    img_io = io.BytesIO()
    segmented_image.save(img_io, format="PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
