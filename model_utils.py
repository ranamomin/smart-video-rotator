import cv2
import torch
import torchvision.transforms as T
from torchvision.models.detection import keypointrcnn_resnet50_fpn
import numpy as np
from PIL import Image

# Load a pretrained keypoint detection model
model = keypointrcnn_resnet50_fpn(pretrained=True)
model.eval()

# Keypoint indices for COCO dataset
KEYPOINTS = {
    'nose': 0, 'left_eye': 1, 'right_eye': 2, 'left_ear': 3, 'right_ear': 4,
    'left_shoulder': 5, 'right_shoulder': 6, 'left_elbow': 7, 'right_elbow': 8,
    'left_wrist': 9, 'right_wrist': 10, 'left_hip': 11, 'right_hip': 12,
    'left_knee': 13, 'right_knee': 14, 'left_ankle': 15, 'right_ankle': 16
}

def analyze_person_in_video(video_path, sample_frame_count=20, confidence_threshold=0.8):
    """
    Analyzes the person's orientation and head position within the video frame.
    Returns a tuple (body_axis, head_position).
    body_axis: "vertical" or "horizontal"
    head_position: "top", "bottom", "left", or "right"
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return None, None

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_indices = np.linspace(0, frame_count - 1, sample_frame_count).astype(int)

    vertical_votes = 0
    horizontal_votes = 0
    head_y_above_hip_votes = 0
    head_x_left_of_hip_votes = 0
    
    print(f"Analyzing {sample_frame_count} frames for person's body axis and head position...")

    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        transform_tensor = T.Compose([T.ToTensor()])
        img_tensor = transform_tensor(pil_image)
        
        with torch.no_grad():
            prediction = model([img_tensor])[0]

        for keypoints, score in zip(prediction['keypoints'], prediction['scores']):
            if score > confidence_threshold:
                # Calculate the person's body axis
                avg_shoulder_x = (keypoints[KEYPOINTS['left_shoulder'], 0].item() + keypoints[KEYPOINTS['right_shoulder'], 0].item()) / 2
                avg_shoulder_y = (keypoints[KEYPOINTS['left_shoulder'], 1].item() + keypoints[KEYPOINTS['right_shoulder'], 1].item()) / 2
                avg_hip_x = (keypoints[KEYPOINTS['left_hip'], 0].item() + keypoints[KEYPOINTS['right_hip'], 0].item()) / 2
                avg_hip_y = (keypoints[KEYPOINTS['left_hip'], 1].item() + keypoints[KEYPOINTS['right_hip'], 1].item()) / 2
                
                body_vertical_span = abs(avg_shoulder_y - avg_hip_y)
                body_horizontal_span = abs(avg_shoulder_x - avg_hip_x)
                
                if body_vertical_span > body_horizontal_span:
                    vertical_votes += 1
                else:
                    horizontal_votes += 1
                
                # Check head position relative to the hip
                head_x = (keypoints[KEYPOINTS['left_eye'], 0].item() + keypoints[KEYPOINTS['right_eye'], 0].item()) / 2
                head_y = (keypoints[KEYPOINTS['left_eye'], 1].item() + keypoints[KEYPOINTS['right_eye'], 1].item()) / 2
                
                if body_vertical_span > body_horizontal_span: # If body is vertical
                    if head_y < avg_hip_y:
                        head_y_above_hip_votes += 1
                else: # If body is horizontal
                    if head_x < avg_hip_x:
                        head_x_left_of_hip_votes += 1
    
    cap.release()

    body_axis = "vertical" if vertical_votes > horizontal_votes else "horizontal"
    
    if body_axis == "vertical":
        head_position = "top" if head_y_above_hip_votes > (vertical_votes / 2) else "bottom"
    else:
        head_position = "left" if head_x_left_of_hip_votes > (horizontal_votes / 2) else "right"

    return body_axis, head_position