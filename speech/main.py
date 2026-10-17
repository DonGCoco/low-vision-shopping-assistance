import whisper


# 加载 Whisper 模型
model = whisper.load_model("tiny")  # 可以选择"tiny", "base", "small", "medium", "large"


def speech_to_text(audio_file):
    # 识别音频文件
    result = model.transcribe(audio_file)
    print("识别到的文本:", result["text"])
    return result["text"]


# 使用示例
audio_path = "hello_japanese.mp3"  # 替换为实际文件路径
speech_to_text(audio_path)
