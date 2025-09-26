import cv2
from pyzbar import pyzbar
import json
import hashlib
from pathlib import Path
import numpy as np

class VideoToTextDecoder:
    def __init__(self, temp_dir="/data/temp"):
        self.temp_dir = Path(temp_dir)
        
    def decode(self, video_path):
        """Decodes QR video into text"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                print(f"Error: Cannot open video file {video_path}")
                return None
            
            metadata = None
            chunks = {}
            expected_chunks = None
            
            # Initial scan for metadata (first 5 frames)
            for _ in range(5):
                ret, frame = cap.read()
                if not ret:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(gray)
                thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                
                decoded_objects = pyzbar.decode(thresh)
                for obj in decoded_objects:
                    try:
                        data = json.loads(obj.data.decode('utf-8'))
                        if 'total_length' in data and metadata is None:
                            metadata = data
                            expected_chunks = metadata.get('num_chunks')
                            break
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
                if metadata:
                    break
            
            # Rewind the video
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_count = 0
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Preprocessing
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(gray)
                thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                
                # QR Decoding
                decoded_objects = pyzbar.decode(thresh)
                
                for obj in decoded_objects:
                    try:
                        data = json.loads(obj.data.decode('utf-8'))
                        
                        # Metadata (redundant, but for robustness)
                        if 'total_length' in data:
                            if metadata is None:
                                metadata = data
                                expected_chunks = metadata.get('num_chunks')
                            
                        # Data chunk
                        elif 'index' in data:
                            idx = data['index']
                            if idx not in chunks:
                                chunks[idx] = data['data']
                                if expected_chunks is None:
                                    expected_chunks = data.get('total')
                            
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
                
                frame_count += 1
                
                # Break if we have all chunks
                if expected_chunks and len(chunks) >= expected_chunks:
                    break
            
            cap.release()
            
            # Check for missing chunks
            if expected_chunks and len(chunks) < expected_chunks:
                missing_chunks = [i for i in range(expected_chunks) if i not in chunks]
                print(f"Error: Missing chunks. Found {len(chunks)} of {expected_chunks}. Missing indices: {missing_chunks}")
                # Return partial text
                sorted_chunks = [chunks.get(i, '') for i in range(expected_chunks)]
                reconstructed_text = ''.join(sorted_chunks)
                print(f"Returning partial text (length: {len(reconstructed_text)})")
                return reconstructed_text if reconstructed_text else None
            
            # Reconstruct
            if not chunks:
                print("Error: No chunks found in video")
                return None
            
            sorted_chunks = [chunks[i] for i in sorted(chunks.keys())]
            reconstructed_text = ''.join(sorted_chunks)
            
            # Verification
            if metadata:
                if len(reconstructed_text) != metadata['total_length']:
                    print(f"Warning: Length mismatch! Expected {metadata['total_length']}, got {len(reconstructed_text)}")
                if 'hash' in metadata:
                    calculated_hash = hashlib.sha256(reconstructed_text.encode()).hexdigest()
                    if calculated_hash != metadata['hash']:
                        print(f"Warning: Hash mismatch! Expected {metadata['hash']}, got {calculated_hash}")
            
            return reconstructed_text
            
        except Exception as e:
            print(f"Decoding error: {e}")
            return None