from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
from flask import Flask, request, jsonify
import torch


app = Flask(__name__)


model_path = "/desay2PB/ct/dev/sg_bowen/Qwen2-VL-main/vlm_data/Qwen2-VL-7B"
# default: Load the model on the available device(s)
model = Qwen2VLForConditionalGeneration.from_pretrained(
    model_path, torch_dtype="auto", device_map="auto"
)
# default processer
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
    inputs = inputs.to("cuda")

    generated_ids = model.generate(**inputs, max_new_tokens=128)
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    return output_text


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json  # Expecting JSON payload
    user_message = data.get('message', '')  # Get the 'message' field from the JSON
    response_message = _chat(user_message)
    return jsonify({"response": response_message})


if __name__ == '__main__':
    app.run(debug=False, port=8888, host='0.0.0.0')

