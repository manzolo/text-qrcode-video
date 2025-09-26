import sys
import os
sys.path.append('/app')

from app.encoder import TextToVideoEncoder
from app.decoder import VideoToTextDecoder
import tempfile

def test_encode_decode():
    """Test completo di encoding e decoding"""
    
    # Testo di test
    test_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
    """ * 10  # Ripeti per avere più chunk
    
    # Setup
    encoder = TextToVideoEncoder(temp_dir="/tmp")
    decoder = VideoToTextDecoder(temp_dir="/tmp")
    
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        video_path = tmp.name
    
    try:
        # Encode
        success = encoder.encode(test_text, video_path)
        assert success, "Encoding failed"
        assert os.path.exists(video_path), "Video file not created"
        
        # Decode
        decoded_text = decoder.decode(video_path)
        assert decoded_text is not None, "Decoding failed"
        
        # Verifica
        assert decoded_text == test_text, "Text mismatch after decode"
        
        print(f"✅ Test passed!")
        print(f"Original length: {len(test_text)}")
        print(f"Decoded length: {len(decoded_text)}")
        print(f"Chunks used: {encoder.last_chunk_count}")
        print(f"Video size: {os.path.getsize(video_path) / 1024:.1f} KB")
        
    finally:
        if os.path.exists(video_path):
            os.unlink(video_path)

if __name__ == "__main__":
    test_encode_decode()