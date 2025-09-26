from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from pathlib import Path
from .encoder import TextToVideoEncoder
from .decoder import VideoToTextDecoder

app = Flask(__name__, static_folder='/app/web/static', static_url_path='/static')
CORS(app)

# Configuration
DATA_DIR = Path("/data")
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
TEMP_DIR = DATA_DIR / "temp"

# Create directories if they don't exist
for dir_path in [INPUT_DIR, OUTPUT_DIR, TEMP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

encoder = TextToVideoEncoder(temp_dir=TEMP_DIR)
decoder = VideoToTextDecoder(temp_dir=TEMP_DIR)

@app.route('/')
def index():
    with open('/app/web/index.html', 'r') as f:
        return f.read()

@app.route('/encode', methods=['POST'])
def encode_text():
    """Endpoint for encoding text into QR video"""
    try:
        if 'file' in request.files:
            file = request.files['file']
            text = file.read().decode('utf-8')
        else:
            data = request.get_json()
            text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate output filename
        output_filename = f"encoded_{os.urandom(8).hex()}.mp4"
        output_path = OUTPUT_DIR / output_filename
        
        # Encode
        success = encoder.encode(text, str(output_path))
        
        if success:
            return jsonify({
                'success': True,
                'filename': output_filename,
                'size': os.path.getsize(output_path),
                'chunks': encoder.last_chunk_count
            })
        else:
            return jsonify({'error': 'Encoding failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decode', methods=['POST'])
def decode_video():
    """Endpoint for decoding QR video into text"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video = request.files['video']
        video_path = TEMP_DIR / f"temp_{os.urandom(8).hex()}.mp4"
        video.save(str(video_path))
        
        # Decode
        # NOTE: The original code includes logic to check a decoder log file for missing chunks,
        # but the provided decoder class doesn't explicitly write a separate log file
        # and instead prints to stdout/stderr. Assuming the goal is to check for
        # internal warnings, we'll keep the log check structure but note the likely
        # need for adjustment in a real production environment.
        text = decoder.decode(str(video_path))
        
        # Clean up temporary file
        video_path.unlink()
        
        if text:
            # Check logs for missing chunks (Log file checking logic kept as per original)
            log_file = '/tmp/decoder.log'
            warning = None
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    if 'Error: Missing chunks' in log_content:
                        warning = 'Decoding incomplete: some chunks are missing'
            return jsonify({
                'success': True,
                'text': text,
                'length': len(text),
                'warning': warning
            })
        else:
            return jsonify({'error': 'Decoding failed: No text extracted'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download of the encoded file"""
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return send_file(str(file_path), as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)