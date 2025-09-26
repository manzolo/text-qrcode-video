# Text to QR Code Video Encoder/Decoder

A Python-based tool to encode text into a video of QR codes and decode it back to text. This project allows users to convert text into a compact MP4 video where each frame is a QR code, optimized for size and reliability, and to extract the original text from the video.

## Features
- **Encode**: Converts text into a video of QR codes using H.265 compression, with configurable chunk size, QR resolution, and frame rate.
- **Decode**: Extracts text from QR code videos with robust preprocessing for reliable QR detection.
- **Web Interface**: A Flask-based UI for easy encoding and decoding via drag-and-drop or text input.
- **Optimized**: Achieves ~1-1.5MB video size for 37KB text with high decoding accuracy.

## Requirements
- Python 3.12+
- Docker (for containerized deployment)
- FFmpeg (for video compression)
- Dependencies: Flask, OpenCV, qrcode, pyzbar, Pillow, numpy (see `requirements.txt`)

## Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/manzolo/text-qrcode-video.git
   cd text-qrcode-video
   ```

2. **Build and Run with Docker**:
   ```bash
   docker compose build
   docker compose up -d
   ```

3. **Access the Web Interface**:
   Open `http://localhost:5000` in a browser to encode or decode text/videos.

## Usage
- **Encode**: Upload a text file or paste text in the "Encode" tab to generate a QR code video.
- **Decode**: Upload a QR code video in the "Decode" tab to extract the original text.
- **Configuration**: Adjust `chunk_size`, `qr_size`, and `fps` in `app/encoder.py` for size vs. reliability trade-offs.

## Example
- Input: 37,000-character text (~37KB)
- Output: ~1.5MB MP4 video with 47 QR code frames (256x256, 5 fps, CRF 25)
- Decoding: Recovers full text with >95% reliability, even with partial chunk loss.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for bug fixes, optimizations, or new features.

## License
MIT License