import os
from model_utils import analyze_person_in_video
from rotate_utils import rotate_video, get_video_resolution

INPUT_FOLDER = "input_videos"
OUTPUT_FOLDER = "corrected"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

for filename in os.listdir(INPUT_FOLDER):
    if not filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        continue

    video_path = os.path.join(INPUT_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    
    print(f"\nProcessing: {filename}")

    # Analyze the person's orientation and head position
    body_axis, head_position = analyze_person_in_video(video_path)
    if body_axis is None:
        continue # Skip if no person was detected

    print(f"Detected: Body axis is {body_axis}, head is at the {head_position}")
    
    # Logic to determine the rotation needed to make the video portrait upright
    if body_axis == "vertical" and head_position == "top":
        print("Video is already portrait upright. No rotation needed.")
    elif body_axis == "vertical" and head_position == "bottom":
        print("Video is portrait upside-down. Rotating 180 degrees.")
        rotate_video(video_path, output_path, direction="180")
    elif body_axis == "horizontal" and head_position == "right":
        print("Video is in landscape, but the person is on the side. Rotating 90 degrees counter-clockwise.")
        rotate_video(video_path, output_path, direction="counterclockwise")
    elif body_axis == "horizontal" and head_position == "left":
        print("Video is in landscape, but the person is on the side. Rotating 90 degrees clockwise.")
        rotate_video(video_path, output_path, direction="clockwise")
    else:
        print("Could not determine correct rotation for this video. Skipping.")