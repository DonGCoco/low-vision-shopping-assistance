# Setup and development notes

## Environment

Use a Python environment compatible with PyTorch, torchvision, transformers, Flask, PyQt5, PyAudio and Whisper. `requirements-reference.txt` lists the main dependencies; package versions and CUDA support should be selected for the target machine. FFmpeg and PortAudio may require system installation.

## Model and service configuration

- DeblurGAN checkpoint: `server/model_zoo/deblurGAN.pth`.
- Qwen2-VL-7B files: `server/model_zoo/Qwen2-VL-7B/`.
- Whisper: the server loads the `tiny` model.
- TTS service: the client expects `GET http://localhost:8000/jp_tts?text=...` returning WAV bytes. Deploy the thesis-described GPT-SoVITS service separately or provide a compatible endpoint.
- Client query service: `http://localhost:5000/query`.

Obtain third-party models and datasets under their applicable terms.

## Startup

From the repository root:

```bash
mkdir -p server/server_cache client/cache
```

Run `python vlm_server.py` from `server/`, start the compatible TTS service, then run `python main.py` from `client/`.

## Runtime modes

`server/vlm_server.py` has `pseudo = True` for a fixed-response demonstration. It still initializes DeblurGAN and Whisper. For actual Qwen inference, set `pseudo = False` and configure the local model directory. Normalize the decoded model response from a list to a string before passing it to the TTS endpoint.

## Development considerations

The desktop client has recording controls; integrate the microphone read loop from `speech/microphone_test.py` into the client before using live voice input. The initial query also opens `client/cache/input.wav`; remove this unnecessary open or provide a valid file. Requests contain the image and current question; conversation history requires explicit session state.

Paths are relative to each process working directory. The Flask debug server is for local development. Legacy DeblurGAN training code may need adaptation to the installed PyTorch version. Review the generator adversarial-loss gradient handling before new training runs. Configure your own training, validation and test splits; the supplied example configuration uses no validation split.

## Validation

Packaging checks cover Python syntax and JSON validity. Runtime validation depends on the configured models, audio hardware and services.
