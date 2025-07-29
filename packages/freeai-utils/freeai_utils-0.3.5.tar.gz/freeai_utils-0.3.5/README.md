# freeai-utils

A lightweight, pip‑installable Python toolkit that wraps popular AI and utility libraries into classes and functions (no external binaries or convoluted setup scripts required). All selected models fall in the **81–242 million parameter** range, which pioritizes real time responsiveness while still delivering solid accuracy. Instead of writing long pipelines or dealing with low level APIs, you get smart defaults out of the box, with the option to customize behavior at init time if needed. 

The first time you use a feature that needs a model (like image captioning or Whisper), it will automatically download the model from Hugging Face. After that, it usually works offline using the cached version.

**Note**: This library focuses on being simple to use, even if it means sacrificing a bit of accuracy. It's great for beginners or anyone who wants to explore AI features without dealing with complex code. Just call the functions, I'll handle the rest.

## Features

- **Audio**: record WAV/MP3 (fixed, toggle, silence-triggered)  
- **Speech-to-Text**: OpenAI Whisper transcription & language detection   
- **Web Search**: scrape & summarize Google results  
- **Image**: caption generation & OCR (EasyOCR)  
- **TTS**: text-to-speech via gTTS or pyttsx3
- **PDF-DOCX-Reader**: extract text and images from pdf and docx files
- **Document Filter**: extract and rank relevant content from documents using an extractive QA model (TinyRoBERTa by default)
- **Translator**: Provides automatic language detection, translating content into your specified target language. (both online and local)
* **Gemini API**: Interact with Google Cloud Gemini models via your API key

  * *Note: This works best with Google accounts that have no billing method added yet (completely free to use with limits).*

## Installation

```bash
pip install freeai-utils
```

> No need to install extra executables or clone large repositories — everything works out of the box with `pip`.

---

## 📖 Full API Reference

For a detailed list of all classes and methods, see [API.md](https://github.com/truongbaan/Utility-python-library/blob/main/API.md).

## Acknowledgements & References

See [THIRD_PARTY.md](https://github.com/truongbaan/Utility-python-library/blob/main/THIRD_PARTY.md) for a full list of third-party libraries and their licenses.

## Inspiration

This project was inspired by the GitHub repository:
[awesome-python](https://github.com/vinta/awesome-python)

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/truongbaan/Utility-python-library/blob/main/LICENSE) file for details.

## Note: 
This project is currently private; it will be made public in a future release.