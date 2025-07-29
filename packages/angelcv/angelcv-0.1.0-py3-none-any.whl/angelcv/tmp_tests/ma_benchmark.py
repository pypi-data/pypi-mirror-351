from collections import defaultdict
import os
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from torch.utils.data import Dataset
import torchvision
from tqdm.auto import tqdm

from angelcv import ObjectDetectionModel

# Parameters
MODEL = "YOLOv10m-dc1-ic640-es"  # "base" or "YOLOv10m-dc1-ic640-es"
SAVE_ERRORS = True  # SAVE_THRESHOLDS only one value!
IMAGE_IN_4 = False
IOU_THRESHOLD = 0.3
# SCORE_THRESHOLDS = [0.8]
CONFIDENCE_THRESHOLDS = [0.0, 0.5, 0.7, 0.9]
DATASET_FOLDER = Path("~/Code/AngelProtection/app/detectorv/datasets/MockAttackDataset").expanduser()

GT_LABELS = ["Handgun", "Short_rifle"]

if MODEL == "YOLOv10m-dc1-ic640-es":
    MODEL_FILENAME = Path(
        "~/Code/computer-vision/AngelCV-tmp/checkpoints/2025-05-21_16-18-37_guns/model-066-052394-17.27.ckpt"
    ).expanduser()
    DETECTION_LABELS = ["gun", "rifle"]
elif MODEL == "base":
    # from inference import Detector

    MODEL_FILENAME = "odw_last_5L_640_with_no_mask_0.2_yolo_version_2.0.pt"
    DETECTION_LABELS = ["gun"]
    # Original result probably iou=0.5
    # TP: 330
    # FP: 67
    # FN: 2518
    # SCORE_THRESHOLD=0.0
    # TP 338
    # FP 59
    # FN 2510
    # SCORE_THRESHOLD=0.5
    # TP 306
    # FP 42
    # FN 2542
    # SCORE_THRESHOLD=0.7
    # TP 245
    # FP 18
    # FN 2603
    # SCORE_THRESHOLD=0.9
    # TP 94
    # FP 2
    # FN 2754
elif MODEL == "YOLOv8m-d2-es":
    # from inference_yolo8 import Detector

    # NOTE: YOLOv8m pretrained on COCO (dataset v2) unsure if correct "ISSUE" with dataset.yaml
    # 600 epoch (with early stopping patience 50) best
    MODEL_FILENAME = "yolov8m_d2_es.pt"
    DETECTION_LABELS = ["gun"]
    # NO SCORE_THRESHOLD
    # TP 684
    # FP 300
    # FN 2164
    # SCORE_THRESHOLD=0.5
    # TP 489
    # FP 100
    # FN 2359
    # SCORE_THRESHOLD=0.6
    # TP 381
    # FP 55
    # FN 2467
    # SCORE_THRESHOLD=0.7
    # TP 167
    # FP 16
    # FN 2681
    # SCORE_THRESHOLD=0.725
    # TP 110
    # FP 9
    # FN 2738
    # SCORE_THRESHOLD=0.75
    # TP 54
    # FP 5
    # FN 2794
    # SCORE_THRESHOLD=0.8
    # TP 21
    # FP 4
    # FN 2827
    # SCORE_THRESHOLD=0.9
    # TP 1
    # FP 0
    # FN 2847


def save_image_with_boxes(
    image: np.ndarray,
    d_boxes: dict[list],
    d_labels: dict[list],
    d_confidences: dict[list],
    gt_boxes: list[list[float]],
    save_path: Optional[Path] = None,
):
    # Open the image and create a draw object
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # Draw detection boxes and labels
    for box, label, confidence in zip(d_boxes, d_labels, d_confidences):
        x1, y1, x2, y2 = box
        draw.rectangle(((x1, y1), (x2, y2)), outline="red", width=2)
        draw.text((x1, y1), f"{label} {confidence:.2f}", fill="white", font=font)

    # Draw ground truth boxes
    for box in gt_boxes:
        x1, y1, x2, y2 = box
        draw.rectangle(((x1, y1), (x2, y2)), outline="green", width=2)

    # Save or show the image
    if save_path:
        image.save(save_path)
    else:
        image.show()


def parse_annotation(annotation_path):
    tree = ET.parse(annotation_path)
    root = tree.getroot()
    bboxes = []
    labels = []
    for obj in root.iter("object"):
        label = obj.find("name").text
        if label in GT_LABELS:
            bbox = obj.find("bndbox")
            labels.append(label)
            bboxes.append(
                {
                    "xmin": float(bbox.find("xmin").text),
                    "ymin": float(bbox.find("ymin").text),
                    "xmax": float(bbox.find("xmax").text),
                    "ymax": float(bbox.find("ymax").text),
                }
            )
    return bboxes, labels


class MockAttackDataset(Dataset):
    def __init__(self, image_dir, annotation_dir):
        self.image_dir = image_dir
        self.annotation_dir = annotation_dir
        self.filenames = [os.path.splitext(f)[0] for f in os.listdir(annotation_dir) if f.endswith(".xml")]

        self.transforms = torchvision.transforms.Compose(
            [
                # torchvision.transforms.Resize((1080, 1920)),
                # torchvision.transforms.ToTensor(),
            ]
        )

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        file_name = self.filenames[idx]
        image_path = os.path.join(self.image_dir, file_name + ".jpg")
        annotation_path = os.path.join(self.annotation_dir, file_name + ".xml")

        image = Image.open(image_path).convert("RGB")
        image.filename = image_path  # NOTE: lost with convert
        bboxes, labels = parse_annotation(annotation_path)

        # Convert everything to PyTorch tensors
        image = self.transforms(image)
        boxes = np.array([list(bbox.values()) for bbox in bboxes])

        # Your target is a dictionary holding the ground truth boxes
        target = {}
        target["boxes"] = boxes
        # "Handgun" and "Short_rifle" are passed
        target["labels"] = np.array(labels)

        return image, target


def split_image(image, bboxes):
    width, height = image.size
    # Slicing points to divide the image into 4 equal parts
    slice_points = [
        (0, 0, width // 2, height // 2),  # Top-Left
        (width // 2, 0, width, height // 2),  # Top-Right
        (0, height // 2, width // 2, height),  # Bottom-Left
        (width // 2, height // 2, width, height),  # Bottom-Right
    ]

    subtargets = [{"boxes": [], "labels": []} for _ in range(4)]
    subimages = []
    for slice_point in slice_points:
        subimage = image.crop(slice_point)
        subimage.filename = image.filename  # NOTE: lost with crop
        subimages.append(subimage)

    for bbox, label in zip(bboxes["boxes"], bboxes["labels"]):
        for i, slice_point in enumerate(slice_points):
            x1, y1, x2, y2 = bbox
            sx1, sy1, sx2, sy2 = slice_point

            # Check if the bbox intersects with this slice_point
            if not (x2 < sx1 or sx2 < x1 or y2 < sy1 or sy2 < y1):
                # Calculate the overlapping area
                nx1, ny1, nx2, ny2 = (
                    max(x1, sx1),
                    max(y1, sy1),
                    min(x2, sx2),
                    min(y2, sy2),
                )
                # Adjust coordinates relative to the sub-image
                nx1 -= sx1
                ny1 -= sy1
                nx2 -= sx1
                ny2 -= sy1
                # Add to corresponding sub-image's boxes
                subtargets[i]["boxes"].append([nx1, ny1, nx2, ny2])
                subtargets[i]["labels"].append(label)

    return subimages, subtargets


def compute_iou(box_a, box_b):
    # Determine the coordinates of the intersection rectangle
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    # Compute the area of intersection rectangle
    inter_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)

    # Compute the area of both the prediction and ground-truth rectangles
    box_a_area = (box_a[2] - box_a[0] + 1) * (box_a[3] - box_a[1] + 1)
    box_b_area = (box_b[2] - box_b[0] + 1) * (box_b[3] - box_b[1] + 1)

    # Compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the intersection area
    iou = inter_area / float(box_a_area + box_b_area - inter_area)

    return iou


def calculate_image_precision(gt_boxes, detected_boxes, iou_threshold=0.5):
    # If no detections are made, return zero precision and the number of FN is the number of GT boxes
    if len(detected_boxes) == 0:
        return 0, 0, len(gt_boxes)

    # Initialize counters
    true_positives = 0
    false_positives = 0

    # Create a list to know if a GT box was already used
    detected = [False] * len(gt_boxes)

    # Calculate IoUs and determine TP and FP
    for db in detected_boxes:
        ious = [compute_iou(db, gt) for gt in gt_boxes]
        max_iou = max(ious) if ious else 0
        max_idx = ious.index(max_iou) if max_iou > iou_threshold else -1
        if max_idx >= 0 and not detected[max_idx]:
            true_positives += 1
            detected[max_idx] = True
        else:
            false_positives += 1

    false_negatives = len(gt_boxes) - sum(detected)

    return true_positives, false_positives, false_negatives


def initialize_folders(folders: list[str]):
    for folder_name in folders:
        folder = Path(__file__).parent / folder_name
        # If exists remove all the elements in the folder
        if folder.exists() and SAVE_ERRORS:
            for f in folder.iterdir():
                f.unlink()
        else:
            folder.mkdir(exist_ok=True)


if __name__ == "__main__":
    folders = ["TP", "FN", "FP"]
    if SAVE_ERRORS:
        initialize_folders(folders)

    # Instantiate your dataset
    mock_attack_dataset = MockAttackDataset(image_dir=str(DATASET_FOLDER), annotation_dir=str(DATASET_FOLDER))

    model_path = Path(__file__).parent.parent / "weights" / MODEL_FILENAME

    model = ObjectDetectionModel(MODEL_FILENAME)

    print(f"Divide in 4: {IMAGE_IN_4}")

    # Modify the main loop to aggregate TPs, FPs, and FNs over all images
    true_positives_total = defaultdict(int)
    false_positives_total = defaultdict(int)
    false_negatives_total = defaultdict(int)

    # NOTE: for some reason when iterating over the dataset, it does one interation more than the length of the dataset
    # that's why we iterate over range(len(mock_attack_dataset))
    for dataset_i in tqdm(range(len(mock_attack_dataset))):
        # if dataset_i == 100:
        #     break

        test_image_full, test_target_full = mock_attack_dataset[dataset_i]

        if IMAGE_IN_4:
            # Split image in 4
            test_images, test_targets = split_image(test_image_full, test_target_full)
        else:
            test_images = [test_image_full]
            test_targets = [test_target_full]

        for test_image, test_target in zip(test_images, test_targets):
            image_np = np.array(test_image.convert("RGB"))
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            # NOTE: image_np is in bgr format, range [0, 255], shape [H, W, C]
            detections = model.predict(image_np, confidence_th=0.1)[0]

            gt_boxes_gun = test_target["boxes"]
            detected_boxes_gun = defaultdict(list)
            detected_labels = defaultdict(list)
            detected_confidences = defaultdict(list)
            if detections:
                # NOTE: adding detected "gun" to "detected_box_gun"
                for box, label, confidence in zip(
                    detections.boxes.xyxy, detections.boxes.labels, detections.boxes.confidences
                ):
                    label = "gun" if label == "person" else label
                    label = "rifle" if label == "bicycle" else label
                    for confidence_threshold in CONFIDENCE_THRESHOLDS:
                        if confidence < confidence_threshold:
                            continue

                        if label in DETECTION_LABELS:
                            detected_boxes_gun[confidence_threshold].append(box)
                            detected_labels[confidence_threshold].append(label)
                            detected_confidences[confidence_threshold].append(confidence)
                            """
                            show_image_with_boxes(
                                image=test_image,
                                d_boxes=[box],
                                d_labels=[label],
                                gt_boxes=gt_boxes_gun,
                            )
                            """

            for confidence_threshold in CONFIDENCE_THRESHOLDS:
                detected_boxes_gun[confidence_threshold] = np.array(detected_boxes_gun[confidence_threshold])

                # Calculate TPs, FPs, and FNs for the current image
                (
                    true_positives,
                    false_positives,
                    false_negatives,
                ) = calculate_image_precision(
                    gt_boxes=gt_boxes_gun,
                    detected_boxes=detected_boxes_gun[confidence_threshold],
                    iou_threshold=IOU_THRESHOLD,
                )

                # Save images
                save_path = None
                filename = Path(test_image.filename).stem
                if IMAGE_IN_4:
                    filename += f"_{dataset_i}"
                filename += ".jpg"

                if true_positives > 0:
                    if not os.path.exists("TP"):
                        os.makedirs("TP")
                    save_path = Path(__file__).parent / "TP" / filename
                elif false_positives > 0:
                    if not os.path.exists("FP"):
                        os.makedirs("FP")
                    save_path = Path(__file__).parent / "FP" / filename
                elif false_negatives > 0:
                    if not os.path.exists("FN"):
                        os.makedirs("FN")
                    save_path = Path(__file__).parent / "FN" / filename

                if save_path and SAVE_ERRORS:
                    save_image_with_boxes(
                        image=test_image,
                        d_boxes=detected_boxes_gun[confidence_threshold],
                        d_labels=detected_labels[confidence_threshold],
                        d_confidences=detected_confidences[confidence_threshold],
                        gt_boxes=gt_boxes_gun,
                        save_path=str(save_path),
                    )

                # print("TP", true_positives, "FP", false_positives, "FN", false_negatives)

                # Accumulate counts
                true_positives_total[confidence_threshold] += true_positives
                false_positives_total[confidence_threshold] += false_positives
                false_negatives_total[confidence_threshold] += false_negatives

    for confidence_threshold in CONFIDENCE_THRESHOLDS:
        # Now calculate precision and recall for the entire dataset
        precision = (
            true_positives_total[confidence_threshold]
            / (true_positives_total[confidence_threshold] + false_positives_total[confidence_threshold])
            if (true_positives_total[confidence_threshold] + false_positives_total[confidence_threshold]) > 0
            else 0
        )
        recall = (
            true_positives_total[confidence_threshold]
            / (true_positives_total[confidence_threshold] + false_negatives_total[confidence_threshold])
            if (true_positives_total[confidence_threshold] + false_negatives_total[confidence_threshold]) > 0
            else 0
        )

        # Assuming a sorted list of detections by confidence score, calculate the average precision
        average_precision = precision * recall  # This is a simplified version for illustrative purposes

        # Print metrics
        print(f"Score threshold: {confidence_threshold}")
        print("TP", true_positives_total[confidence_threshold])
        print("FP", false_positives_total[confidence_threshold])
        print("FN", false_negatives_total[confidence_threshold])

        """
        # Print out the AP for the class "gun"
        print(f"Average Precision for the class 'gun': {average_precision}")
        """
