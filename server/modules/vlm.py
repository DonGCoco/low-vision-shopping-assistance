

def create_vlm_message(text):
    llm_message = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": "server_cache/input_image.jpg"},
                {"type": "text",
                 "text": text},
            ],
        }
    ]
    return llm_message
