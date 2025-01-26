from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
import sys
from PIL import Image
from pillow_heif import register_heif_opener
import piexif
import io
import os
import time
import datetime
import subprocess

# Register HEIF opener with Pillow
register_heif_opener()

def get_date_taken(path):
    try:
        image = Image.open(path)
        exif_data = image._getexif()
        if exif_data and 36867 in exif_data:
            return exif_data[36867]
    except Exception as e:
        print(f"Error reading date taken from {path}: {e}")
    return None

def get_heic_date_taken(path):
    try:
        heif_image = Image.open(path)
        exif_dict = piexif.load(heif_image.info['exif'])
        if "Exif" in exif_dict and 36867 in exif_dict["Exif"]:
            return exif_dict["Exif"][36867].decode("utf-8")
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
    except Exception as e:
        print(f"Error reading media created date from {path}: {e}")
    return None

def modify_file_date(image_path, date_taken):
    if date_taken:
        try:
            date_struct = time.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
            timestamp = time.mktime(date_struct)
            os.utime(image_path, (timestamp, timestamp))
            print(f"Updated {image_path} with date taken: {date_taken}")
        except Exception as e:
            print(f"Error modifying file date for {image_path}: {e}")
    else:
        print(f"Skipping {image_path} due to missing date taken.")

def process_directory(directory, ffprobe_path):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg')):
                image_path = os.path.join(root, filename)
                date_taken = get_date_taken(image_path)
                modify_file_date(image_path, date_taken)
            elif filename.lower().endswith('.heic'):
                heic_path = os.path.join(root, filename)
                date_taken = get_heic_date_taken(heic_path)
                modify_file_date(heic_path, date_taken)
            elif filename.lower().endswith('.mp4'):
                video_path = os.path.join(root, filename)
                date_created = get_video_date_created(video_path, ffprobe_path)
                modify_file_date(video_path, date_created)

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Directory Selector'
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        layout = QVBoxLayout()

        self.label = QLabel('Select a directory to process files:')
        layout.addWidget(self.label)

        self.button = QPushButton('Choose Directory', self)
        self.button.clicked.connect(self.showDialog)
        layout.addWidget(self.button)

        self.executeButton = QPushButton('Execute', self)
        self.executeButton.clicked.connect(self.executeScript)
        layout.addWidget(self.executeButton)

        self.setLayout(layout)
        self.show()

    def showDialog(self):
        self.directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if self.directory:
            self.label.setText(f'Selected Directory: {self.directory}')

    def executeScript(self):
        if hasattr(self, 'directory'):
            ffprobe_path = 'C:\\ffmpeg\\bin\\ffprobe.exe'  # Update this path to your FFmpeg installation
            process_directory(self.directory, ffprobe_path)
            self.label.setText('Execution completed.')
        else:
            self.label.setText('Please select a directory first.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
