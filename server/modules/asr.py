

def speech_to_text(asr_model, audio_file):
    # 识别音频文件
    result = asr_model.transcribe(audio_file)
    # print("识别到的文本:", result["text"])
    return result["text"]
