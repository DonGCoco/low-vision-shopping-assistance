import os.path
import sys
import numpy as np
import cv2
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
                             QTextEdit, QSizePolicy)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QImage, QPixmap
import requests
import base64
import pyaudio
import wave


class WebcamWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.initUI()
        self.cap = None
        self.single_image = None
        self.image_path = None
        self.extract_contours = False
        # self.query_prompt = "hello"
        self.llm_url = 'http://localhost:5000/query'
        self.tts_url = 'http://localhost:8000/jp_tts'
        self.llm_base_query_text = "これは私が買いたい商品が並んでいるスーパーマーケットの写真です。画像の商品について詳しく説明してください。名前、種類、サイズ、値段を教えて下さい。"
        self.cache_audio_path = "cache/received.wav"
        self.input_audio_path = "cache/input.wav"
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []

    def initUI(self):
        self.setWindowTitle('object detection system')

        # Create labels to show the images
        self.original_image = QLabel(self)

        # Set fixed size for the labels
        self.original_image.setFixedSize(480, 480)

        # Display placeholder images initially
        self.display_placeholder_image(self.original_image)

        # Create a QTextEdit for logging
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        # Create buttons
        self.load_image_button = QPushButton('Load Image', self)
        self.load_image_button.clicked.connect(self.select_image)

        self.query_button = QPushButton('Query', self)
        self.query_button.clicked.connect(self.query)
        self.query_button.setEnabled(False)

        self.clear_button = QPushButton("Clear", self)
        self.clear_button.clicked.connect(self.clear)
        self.clear_button.setEnabled(False)

        self.play_audio_button = QPushButton("Play Audio", self)
        self.play_audio_button.clicked.connect(self.play_audio)
        self.play_audio_button.setEnabled(True)

        self.start_record_button = QPushButton("Start Record", self)
        self.start_record_button.setEnabled(False)
        self.start_record_button.clicked.connect(self.start_recording)

        self.end_record_button = QPushButton("End Record", self)
        self.end_record_button.setEnabled(False)
        self.end_record_button.clicked.connect(self.stop_recording)

        self.ask_button = QPushButton("Ask", self)
        self.ask_button.clicked.connect(self.ask)
        self.ask_button.setEnabled(False)

        # Set up the button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_image_button)
        button_layout.addWidget(self.query_button)

        button_layout2 = QHBoxLayout()
        button_layout2.addWidget(self.clear_button)
        button_layout2.addWidget(self.play_audio_button)

        button_layout3 = QHBoxLayout()
        button_layout3.addWidget(self.start_record_button)
        button_layout3.addWidget(self.end_record_button)
        button_layout3.addWidget(self.ask_button)

        # Set up the image layout
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.original_image)

        # log
        log_layout = QVBoxLayout()
        log_layout.addWidget(self.log_text)

        # Combine button layout and image layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addLayout(button_layout2)
        main_layout.addLayout(button_layout3)
        main_layout.addLayout(image_layout)
        main_layout.addLayout(log_layout)

        self.setLayout(main_layout)
        self.resize(100, 100)
        self.show()

    def start_recording(self):
        try:
            self.display_image(self.original_image, self.single_image)
            self.is_recording = True
            self.frames = []
            self.stream = self.audio.open(format=pyaudio.paInt16,
                                          channels=1,
                                          rate=44100,
                                          input=True,
                                          frames_per_buffer=1024)
            self.log_text.setText(f"Recording...")
            self.start_record_button.setDisabled(True)
            self.end_record_button.setEnabled(True)
        except Exception as e:
            print(e)

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.start_record_button.setEnabled(True)
        self.end_record_button.setDisabled(True)
        # 保存为 WAV 文件
        filename = self.input_audio_path
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)  # todo
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.log_text.setText(f"Recording finished")
        self.ask_button.setEnabled(True)

    def select_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.jpg *.png *.bmp)")
        try:
            if image_path:
                self.single_image = cv2.imread(image_path)
                self.single_image = cv2.resize(self.single_image, (480, 480))
                self.image_path = image_path
                self.display_image(self.original_image, self.single_image)
                self.query_button.setEnabled(True)
                self.clear_button.setEnabled(True)
        except Exception as e:
            print(e)

    def clear(self):
        self.image_path = None
        self.single_image = None
        self.query_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.display_placeholder_image(self.original_image)

    def play_audio(self):
        audio_url = QUrl.fromLocalFile(self.cache_audio_path)
        self.player.setMedia(QMediaContent(audio_url))
        self.player.play()

    def query(self):
        try:
            with open(self.image_path, 'rb') as image_file, open(self.input_audio_path, 'rb') as audio_file:
                files = {
                    'image': image_file,
                }
                data = {
                    'text': self.llm_base_query_text
                }
                response = requests.post(self.llm_url, data=data, files=files)
            output_message = response.json()['response']
            self.log_text.setText(output_message)
            response = requests.get(self.tts_url, params={"text": output_message})  # todo
            if response.status_code == 200:
                with open(self.cache_audio_path, "wb") as f:
                    f.write(response.content)
                print("WAV file received and saved as received.wav")
            else:
                print(f"Error: {response.status_code}, {response.json()}")
            if os.path.exists(self.cache_audio_path):
                self.play_audio_button.setEnabled(True)
                self.start_record_button.setEnabled(True)
        except Exception as e:
            print(e)

    def ask(self):
        try:
            with open(self.image_path, 'rb') as image_file, open(self.input_audio_path, 'rb') as audio_file:
                files = {
                    'image': image_file,
                    'audio': audio_file
                }
                response = requests.post(self.llm_url, files=files)
            output_message = response.json()['response']
            self.log_text.setText(output_message)
            response = requests.get(self.tts_url, params={"text": output_message})  # todo
            if response.status_code == 200:
                with open(self.cache_audio_path, "wb") as f:
                    f.write(response.content)
                print("WAV file received and saved as received.wav")
            else:
                print(f"Error: {response.status_code}, {response.json()}")
            if os.path.exists(self.cache_audio_path):
                self.play_audio_button.setEnabled(True)
                self.start_record_button.setEnabled(True)
        except Exception as e:
            print(e)

    def display_image(self, label, img):
        qformat = QImage.Format_Indexed8 if len(img.shape) == 2 else QImage.Format_RGB888
        out_image = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        out_image = out_image.rgbSwapped()
        label.setPixmap(QPixmap.fromImage(out_image))
        label.setAlignment(Qt.AlignCenter)

    def display_placeholder_image(self, label):
        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
        placeholder.fill(255)  # Fill the placeholder with white color
        qformat = QImage.Format_RGB888
        out_image = QImage(placeholder, placeholder.shape[1], placeholder.shape[0], placeholder.strides[0], qformat)
        out_image = out_image.rgbSwapped()
        label.setPixmap(QPixmap.fromImage(out_image))
        label.setAlignment(Qt.AlignCenter)

    def closeEvent(self, event):
        if self.cap is not None:
            self.cap.release()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WebcamWidget()
    sys.exit(app.exec_())
