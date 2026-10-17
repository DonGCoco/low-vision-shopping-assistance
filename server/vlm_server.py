from flask import Flask, request, jsonify
import torch
from modules import deblur, asr, vlm
import whisper


pseudo = True

app = Flask(__name__)
# deblur init
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
deblur_model_path = "model_zoo/deblurGAN.pth"
deblur.generator = deblur.init_model(deblur_model_path, device)
# asr init
asr_model = whisper.load_model("tiny")
# vlm init
if pseudo is False:
    from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
    from qwen_vl_utils import process_vision_info
    model_path = "model_zoo/Qwen2-VL-7B"
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_path, torch_dtype="auto", device_map=device
    )
    processor = AutoProcessor.from_pretrained(model_path)

    def _chat(messages):
        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(device)

        generated_ids = model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text

else:
    def _chat(message):
        output_text = "この写真は、スーパーマーケットで販売されているトマトの様子を示しています。以下に詳細を説明します。\n名前: トマト\n種類: トマト（バラ）\nサイズ: 画像からは具体的なサイズがわかりませんが、一般的なトマトの大きさと思われます。\n値段: 1個あたり177円（税込価格は191.46円）\nトマトは、赤く熟した果実で、サラダや料理によく使われます。写真には、多くのトマトが箱に詰められて陳列されています。"
        return output_text


@app.route('/query', methods=['POST'])
def query():
    image_file = request.files['image']
    # input_image = Image.open(image_file)
    deblur_image = deblur.image_deblur(image_file, device)
    deblur_image.save("server_cache/input_image.jpg")
    if 'audio' in request.files:
        audio_file = request.files['audio']
        audio_file.save("server_cache/input_audio.wav")
        text_content = asr.speech_to_text(asr_model, "server_cache/input_audio.wav")
    else:
        text_content = request.form['text']
    print('audio' in request.files, text_content)
    message = vlm.create_vlm_message(text_content)
    print(message)
    response_message = _chat(message)
    return jsonify({"response": response_message})


if __name__ == '__main__':
    app.run(debug=True)
