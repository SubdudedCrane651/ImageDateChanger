from PIL import Image
from PIL.ExifTags import TAGS
import os
import time
import datetime
import subprocess

def get_date_taken(path):
    try:
        return Image.open(path)._getexif()[36867]
    except Exception as e:
        print(f"Error reading date taken from {path}: {e}")
        return None

def get_video_date_created(path, ffprobe_path):
    try:
        result = subprocess.run([ffprobe_path, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'format_tags=creation_time', '-of', 'default=noprint_wrappers=1:nokey=1', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        date_created = result.stdout.decode().strip()
        formats = ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
        for fmt in formats:
            try:
                date_struct = datetime.datetime.strptime(date_created, fmt)
                return date_struct.strftime('%Y:%m:%d %H:%M:%S')
            except ValueError:
                continue
        print(f"Date format not recognized for {path}: {date_created}")
        return None
    except Exception as e:
        print(f"Error reading media created date from {path}: {e}")
        return None

def modify_file_date(image_path, date_taken):
    if date_taken:
        date_struct = time.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
        timestamp = time.mktime(date_struct)
        os.utime(image_path, (timestamp, timestamp))
        print(f"Updated {image_path} with media created date: {date_taken}")
    else:
        print(f"Skipping {image_path} due to missing media created date.")

def process_directory(directory, ffprobe_path):
    for root, dirs, files in os.walk(directory):
        for filename in files:
           try:
            if filename.lower().endswith(('.jpg', '.jpeg')):
                image_path = os.path.join(root, filename)
                date_taken = get_date_taken(image_path)
                modify_file_date(image_path, date_taken)
            elif filename.lower().endswith('.mp4'):
                video_path = os.path.join(root, filename)
                date_created = get_video_date_created(video_path, ffprobe_path)
                modify_file_date(video_path, date_created)
           except:
               print("skipped")
directory = 'L:\Multimedia\Pictures'
ffprobe_path = 'C:\\ffmpeg\\bin\\ffprobe.exe'  # Update this path to your FFmpeg installation

process_directory(directory, ffprobe_path)
