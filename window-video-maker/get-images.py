import cv2
import os
import sys
from datetime import timedelta
import argparse

def extract_frames(video_path, output_folder, interval_seconds=10):
    """
    Extract frames from a video file at specified intervals.
    
    Args:
        video_path (str): Path to the input video file
        output_folder (str): Path to the output folder for frames
        interval_seconds (int): Interval between frame captures in seconds
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Open the video file
    video = cv2.VideoCapture(video_path)
    if(video.isOpened() == False):
        print(f"Error: Could not open video file {video_path}")
        return
    # Get video properties
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    if(fps == 0):
        print(f"Error: Could not read video file FPS.")
        return
    
    if(total_frames == 0):
        print(f"Error: Could not read video file frame count.")
        return
    
    print(f'Total Frames={total_frames}')
    duration = total_frames / fps
    
    # Calculate frame interval
    frame_interval = int(fps * interval_seconds)
    
    frame_count = 0
    saved_count = 0
    
    while True:
        success, frame = video.read()
        
        if not success:
            break
            
        # Save frame at specified intervals
        if frame_count % frame_interval == 0:
            sys.stdout.write('+')
            timestamp = timedelta(seconds=int(frame_count/fps))
            filename = os.path.join(output_folder, f'frame_{saved_count}.jpg')
            frame=cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            cv2.imwrite(filename, frame)
            saved_count += 1
        sys.stdout.write('.')            
        frame_count += 1
    
    # Clean up
    video.release()
    print(f"Extraction complete! Saved {saved_count} frames to {output_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract frames from video at specified intervals')
    parser.add_argument('video_path', help='Path to the input video file')
    parser.add_argument('output_folder', help='Path to the output folder for frames')
    parser.add_argument('--interval', type=int, default=20, help='Interval between frames in seconds (default: 10)')
    #  py ./get-images.py video_path=video/default-window.mp4 output_folder=output
    # py ./get-images.py 'video\default-window.mp4' 'output'
    args = parser.parse_args()
    print(f' video path={args.video_path}')
    print(f'output folder= {args.output_folder}')
    extract_frames(args.video_path, args.output_folder, args.interval)