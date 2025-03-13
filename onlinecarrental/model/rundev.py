import base64
import io
import os
import torch
import numpy as np
from flask import Flask, request, jsonify
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data import MetadataCatalog
from detectron2.structures import Instances
from PIL import Image

# Flask app
app = Flask(__name__)

# Load Detectron2 Model
model_path = 'model_final.pth'

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.6
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # Assuming 1 class for damage
cfg.MODEL.WEIGHTS = model_path

if not torch.cuda.is_available():
    cfg.MODEL.DEVICE = 'cpu'

predictor = DefaultPredictor(cfg)

# Metadata
my_metadata = MetadataCatalog.get("car_dataset_val")
my_metadata.thing_classes = ["damage"]

def merge_segment(pred_segm):
    merge_dict = {}
    for i in range(len(pred_segm)):
        merge_dict[i] = []
        for j in range(i + 1, len(pred_segm)):
            if torch.sum(pred_segm[i] * pred_segm[j]) > 0:
                merge_dict[i].append(j)

    to_delete = set()
    for key in merge_dict:
        to_delete.update(merge_dict[key])

    new_masks = [pred_segm[i] for i in range(len(pred_segm)) if i not in to_delete]
    return new_masks

def inference(image):
    img = np.array(image)
    outputs = predictor(img)
    out_dict = outputs["instances"].to("cpu").get_fields()

    if 'pred_masks' not in out_dict or len(out_dict['pred_masks']) == 0:
        return image  # Return original image if no damage detected

    new_inst = Instances(img.shape[:2])
    new_inst.set('pred_masks', merge_segment(out_dict['pred_masks']))

    v = Visualizer(img[:, :, ::-1], metadata=my_metadata, scale=0.5, instance_mode=ColorMode.SEGMENTATION)
    out = v.draw_instance_predictions(new_inst)
    return Image.fromarray(out.get_image()[:, :, ::-1])

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        image = Image.open(image_file).convert('RGB')
        processed_image = inference(image)

        buffered = io.BytesIO()
        processed_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return jsonify({"prediction": "success", "image": img_str}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # Debug=True for easier troubleshooting