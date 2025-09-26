import qrcode
from PIL import Image
import cv2
import numpy as np
import os
from pathlib import Path
import math
import json
import hashlib
from .utils import compress_video_h265

class TextToVideoEncoder:
    def __init__(self, temp_dir="/data/temp", chunk_size=800, qr_size=256, fps=5):
        self.temp_dir = Path(temp_dir)
        self.chunk_size = chunk_size
        self.qr_size = qr_size
        self.fps = fps
        self.last_chunk_count = 0
        
    def encode(self, text, output_path):
        """Encodes text into a QR code video"""
        try:
            # Prepare metadata
            chunks = self._split_into_chunks(text)
            metadata = {
                'total_length': len(text),
                'chunk_size': self.chunk_size,
                'num_chunks': len(chunks),
                'hash': hashlib.sha256(text.encode()).hexdigest()
            }
            
            self.last_chunk_count = len(chunks)
            
            # Generate QR for each chunk
            qr_images = []
            
            # First frame: metadata
            try:
                meta_qr = self._create_qr(json.dumps(metadata))
                qr_images.append(meta_qr)
            except ValueError as e:
                print(f"Metadata encoding error: {e}")
                return False
            
            # Data frames
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    'index': i,
                    'total': len(chunks),
                    'data': chunk
                }
                try:
                    qr_img = self._create_qr(json.dumps(chunk_data))
                    qr_images.append(qr_img)
                except ValueError as e:
                    print(f"Chunk {i} encoding error: {e}")
                    return False
            
            # Create video
            return self._create_video(qr_images, output_path)
            
        except Exception as e:
            print(f"Encoding error: {e}")
            return False
    
    def _split_into_chunks(self, text):
        """Splits the text into chunks"""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i + self.chunk_size])
        return chunks
    
    def _create_qr(self, data):
        """Generates QR code from string"""
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((self.qr_size, self.qr_size), Image.Resampling.NEAREST)
        return np.array(img.convert('RGB'))
    
    def _create_video(self, images, output_path):
        """Creates video from a list of images"""
        if not images:
            return False
        
        height, width = images[0].shape[:2]
        temp_output = str(self.temp_dir / f"temp_{os.urandom(8).hex()}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_output, fourcc, self.fps, (width, height))
        
        for img in images:
            # Convert from RGB to BGR for OpenCV
            bgr_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # Repeat frame for longer duration
            for _ in range(2):  # Reduced to 2 frames per QR code
                out.write(bgr_img)
        
        out.release()
        
        # Compress the video with H.265
        success = compress_video_h265(temp_output, output_path)
        
        # Clean up the temporary file
        if os.path.exists(temp_output):
            os.unlink(temp_output)
        
        return success and os.path.exists(output_path)