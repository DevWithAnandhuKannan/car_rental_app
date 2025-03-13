import base64
import os
import torch
import numpy as np
import cv2
import detectron2
from flask import Flask, request, jsonify
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import Instances
import gradio as gr
from PIL import Image

# Ensure dependencies are installed
try:
    import detectron2
except ImportError:
    os.system('pip install git+https://github.com/facebookresearch/detectron2.git')

# Flask app
app = Flask(__name__)

@app.route('predict', methods=['POST'])
def predict():
    try:
        # Check if an image file is included in the request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        # Read the image file from the request
        image_file = request.files['image']
        image = Image.open(image_file).convert('RGB')

        # Perform inference (replace with your actual model call)
        prediction = inference(image)

        # For this example, we’ll encode the image back to base64 as a response
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Prepare the response
        response = {
            "prediction": prediction,
            "image": img_str  # Example: returning the processed image
        }
        return jsonify(response), 200

    except Exception as e:
        # Handle any errors during processing
        return jsonify({"error": str(e)}), 500


# Load Detectron2 Model
model_path = 'model_final.pth'

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.6
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
cfg.MODEL.WEIGHTS = model_path

if not torch.cuda.is_available():
    cfg.MODEL.DEVICE = 'cpu'

predictor = DefaultPredictor(cfg)

# Ensure metadata is properly assigned
my_metadata = MetadataCatalog.get("car_dataset_val")
my_metadata.thing_classes = ["damage"]

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

    empty_delete = [key for key in merge_dict if not merge_dict[key]]
    for element in empty_delete:
        merge_dict.pop(element, None)

    for key in merge_dict:
        for element in merge_dict[key]:
            pred_segm[key] += pred_segm[element]

    # Remove merged elements
    except_elem = list(set(to_delete))
    new_indexes = [i for i in range(len(pred_segm)) if i not in except_elem]

    return [pred_segm[i] for i in new_indexes]

def inference(image):
    img = np.array(image)
    outputs = predictor(img)
    out_dict = outputs["instances"].to("cpu").get_fields()

    new_inst = Instances((1024, 1024))
    new_inst.set('pred_masks', merge_segment(out_dict['pred_masks']))

    v = Visualizer(img[:, :, ::-1], metadata=my_metadata, scale=0.5, instance_mode=ColorMode.SEGMENTATION)
    out = v.draw_instance_predictions(new_inst)

    return out.get_image()[:, :, ::-1]

# Define Gradio interface
gr_interface = gr.Interface(fn=inference, inputs="image", outputs="image")

# Run Flask and Gradio together
if __name__ == '__main__':
    import threading
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)).start()
    gr_interface.launch()
