import os
import shutil
from pathlib import Path

def cleanup_temp_files(temp_dir):
    """Cleans up temporary files"""
    temp_path = Path(temp_dir)
    if temp_path.exists():
        for file in temp_path.glob('*'):
            if file.is_file():
                file.unlink()

def get_file_size_mb(filepath):
    """Returns the file size in MB"""
    return os.path.getsize(filepath) / (1024 * 1024)

def compress_video_h265(input_path, output_path):
    """Further compresses the video using H.265"""
    import subprocess
    cmd = [
        'ffmpeg', '-i', str(input_path),
        '-c:v', 'libx265', '-crf', '25',  # Increased to 25 for more compression
        '-preset', 'slow',  # Changed to 'slow' for better compression
        '-tag:v', 'hvc1',
        '-an',
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}")
        return False
    return os.path.exists(output_path)