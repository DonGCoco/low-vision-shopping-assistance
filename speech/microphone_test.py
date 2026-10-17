import pyaudio
import wave

# 设置录音参数
FORMAT = pyaudio.paInt16  # 音频格式
CHANNELS = 1  # 单声道
RATE = 44100  # 采样率
CHUNK = 1024  # 每次读取的音频块大小
RECORD_SECONDS = 5  # 录制时长（秒）
OUTPUT_FILENAME = "output.wav"  # 输出文件名

# 初始化 PyAudio
p = pyaudio.PyAudio()

# 打开麦克风输入流
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("开始录音...")

frames = []

# 录音并将音频数据存入 frames 列表
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

# 结束录音
print("录音结束。")

# 停止并关闭流
stream.stop_stream()
stream.close()
p.terminate()

# 保存录音为 WAV 文件
with wave.open(OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print(f"录音已保存为 {OUTPUT_FILENAME}")
