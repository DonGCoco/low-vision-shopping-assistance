from gtts import gTTS

# 日语的“你好”
text = "こんにちは"  # 这是“你好”的日语表达

# 生成音频
tts = gTTS(text, lang='ja')  # 设置语言为日语

# 保存为音频文件
tts.save("hello_japanese.mp3")

print("音频已保存为 hello_japanese.mp3")
