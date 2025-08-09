import subprocess
import cv2

def rotate_video(input_path, output_path, direction="clockwise"):
    """
    Rotates the video 90 degrees using ffmpeg.
    direction can be "clockwise", "counterclockwise", or "180".
    """
    if direction == "clockwise":
        transpose_code = "1"
    elif direction == "counterclockwise":
        transpose_code = "2"
    elif direction == "180":
        # A 180-degree rotation is two 90-degree clockwise rotations
        transpose_code = "1,transpose=1"
    else:
        raise ValueError("Invalid rotation direction. Use 'clockwise', 'counterclockwise', or '180'.")

    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", f"transpose={transpose_code}",
        "-c:a", "copy",
        "-y", # Overwrite output file if it exists
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Video successfully rotated and saved to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during video rotation: {e}")

def get_video_resolution(video_path):
    cap = cv2.VideoCapture(video_path)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    cap.release()
    return int(width), int(height)