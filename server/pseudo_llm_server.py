# coding=utf-8
from flask import Flask, request, jsonify
import numpy as np
import cv2
import base64
import io
from PIL import Image


app = Flask(__name__)


def _chat(messages):
    output_text = "この写真は、スーパーマーケットで販売されているトマトの様子を示しています。以下に詳細を説明します。\n名前: トマト\n種類: トマト（バラ）\nサイズ: 画像からは具体的なサイズがわかりませんが、一般的なトマトの大きさと思われます。\n値段: 1個あたり177円（税込価格は191.46円）\nトマトは、赤く熟した果実で、サラダや料理によく使われます。写真には、多くのトマトが箱に詰められて陳列されています。"
    return output_text


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    img_bytes_str = data.get('image', '')
    img_bytes = base64.b64decode(img_bytes_str)
    image = Image.open(io.BytesIO(img_bytes))
    image.save("cache/input.jpg")
    user_message = data.get('message', '')  # Get the 'message' field from the JSON
    print(user_message)
    response_message = _chat(user_message)
    print(response_message)
    return jsonify({"response": response_message})


if __name__ == '__main__':
    app.run(debug=False, port=8888, host='0.0.0.0')

