from wanwu import FaceWanwu
import os
from PIL import Image

if os.path.exists("yolov7s-face.onnx"):
    face_det = FaceWanwu(onnx_f="yolov7s-face.onnx", input_height=640, input_width=640)
else:
    face_det = FaceWanwu(type="yolov7s-face", input_height=640, input_width=640)


def get_face_box_ww(image, save=True, normalize_output=False):
    if isinstance(image, str):
        image_in = Image.open(image).convert("RGB")
    else:
        image_in = image
    boxes, scores = face_det.get_face_boxes(image_in)
    if isinstance(image, str) and save:
        # visualize it
        print(len(boxes))
        labels = [i for i in range(1, len(boxes) + 1)]
        print(labels)
        img_out = face_det.vis_res(
            image_in,
            boxes,
            scores,
            labels=[0 for _ in range(len(boxes))],
            track_ids=labels,
            class_names=["face"],
        )
        img_out = img_out[..., ::-1]
        img_out_name = os.path.basename(image)[:-4] + "_out.jpg"
        Image.fromarray(img_out).save(os.path.join("temp", img_out_name))

    if normalize_output:
        boxes = boxes
    else:
        boxes = boxes.astype(int)
        boxes = boxes.tolist()
    return boxes


a = get_face_box_ww("raw/images/l41000sbn89[01_24_24][20240801-165209].png")
print(a)
