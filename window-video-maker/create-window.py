import random
import cv2
import os
from natsort import natsorted
import datetime
import argparse

def create_video_from_images(image_folder, video_folder,output_video, fps=0.1, randomise=False):
    default_length=15   
    loop_count=1
    images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg")or img.endswith(".jpeg")]
    if not images:
        print("No images found in the folder.")
        return
    
    videos=[vid for vid in os.listdir(video_folder) if vid.endswith(".mp4")]
    if videos:
        print(f"{len(videos)} Videos found in the folder.")

    assets=images+videos

    print(f"Found {len(assets)} assets in the folders.")

    if randomise:
        random.shuffle(assets)
        print("Randomised the order of assets")
    else:
        assets = natsorted(assets)
        print("assets will be displayed in the order they are named")

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, fps, (1920, 1080))

    for _ in range(loop_count):#loop twice
        for asset in assets:
            if asset.endswith(".mp4"):
                print(f"Adding video {asset} to the video")
                video_path = os.path.join(video_folder, asset)
                print(f"Reading video from {video_path}")
                cap = cv2.VideoCapture(video_path)
                print(f"Reading video from {video_path}")
                video_fps = cap.get(cv2.CAP_PROP_FPS)
                print(f"Video fps={video_fps}")
                frame_count=0
                number_of_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                print(f"Number of frames in the video={number_of_frames}")
                
                # 30fps video, 10fps output, skip every 3rd frame
                frames_to_skip = int(video_fps/fps)
                print(f"Frames to skip={frames_to_skip}")
                frames_written=0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    if not (frame.shape[0] == 1080 and frame.shape[1] == 1920):
                        ResizeTo = (1080, 1920)
                        frame = cv2.resize(frame, ResizeTo)
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    frame = cv2.resize(frame, (1920, 1080))
                    frame_count+=1
                    if frame_count > frames_to_skip:
                        print(f"Writing frame {frames_written} of {number_of_frames} from this video")
                        #for _ in range(fps):
                        video.write(frame)
                        video.write(frame)
                        frame_count=0
                        frames_written+=1
                cap.release()
                print(f"{frames_written} frames_written from this video")
            else:
                image = asset
                print(f"Adding image {image} to the video")
                img_path = os.path.join(image_folder, image)
                frame = cv2.imread(img_path)
                # if the image is already 1920x1080, skip resizing and rotating
                if not (frame.shape[0] == 1080 and frame.shape[1] == 1920):
                    ResizeTo = (1080, 1920)
                    frame = cv2.resize(frame, ResizeTo)
                    #rotate 90 degree
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                for _ in range(fps*default_length):  # Display each image for frames
                    video.write(frame)

    video.release()
    print(f"Video saved as {output_video}")

def generate_datestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def rotate_video(input_video):
        output_video = input_video.replace(".mp4", "_rotated.mp4")
        os.system(f'ffmpeg -i {input_video} -vf "transpose=2" {output_video}')
        print(f"Rotated video saved as {output_video}")

if __name__ == "__main__":
    
    image_folder = "images"
    video_folder = "videos"
    output_folder = "output"
    randomise = False
    fps=10
    parser = argparse.ArgumentParser(
                    prog='Create Window Video Application',
                    description='Create a video from images in a folder',
                    epilog='')
    
    parser.add_argument('-i', '--images', help='Path to the folder containing images', required=False)
    parser.add_argument('-o', '--output', help='Path to the output folder', required=False)
    parser.add_argument('-r', '--randomise', help='Randomise the order of images', action='store_true', required=False)
    parser.add_argument('-f', '--fps', help='Frames per second', required=False)
    args = parser.parse_args()

    if args.images:
        image_folder = args.images
    if args.output:
        output_folder = args.output
    if args.fps:
        fps = float(args.fps)
    if args.randomise:
        randomise = True


    datestamp = generate_datestamp()
    output_video = os.path.join(output_folder, f"window_gen_{datestamp}.mp4")
    # Original aspect ratio: 9:16, will output as -90 rotated 16:9
    create_video_from_images(image_folder, video_folder, output_video, fps, randomise)
