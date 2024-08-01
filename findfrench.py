import os
import subprocess
import shutil

# Define the directory to search
directory = "/mnt/AllVideo/Playlists/AllVideo/Series"
directory_F = "/mnt/AllVideo/Playlists/AllVideo/Series-F"

# Define the video file extensions to check
video_extensions = ('.mp4', '.mkv')

def check_french_audio(file_path):
    try:
        # Use ffprobe to get the audio streams information
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=index:stream_tags=language", "-select_streams", "a", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Check if the output contains 'language=fre'
        if 'language=fre' in result.stdout:
            return True
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return False

# Walk through the directory
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.lower().endswith(video_extensions):
            file_path = os.path.join(root, file)
            # Check if it's a symlink
            if os.path.islink(file_path):
                # Resolve the symlink to the actual file path
                real_path = os.readlink(file_path)
                if check_french_audio(real_path):
                    # Create destination directory if not exists
                    source_folder_name = os.path.basename(root)
                    destination_dir = os.path.join(directory_F, source_folder_name)
                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir)
                    
                    # Move the symlink
                    destination_path = os.path.join(destination_dir, file)
                    print(f"Moving {file_path} to {destination_path}")
                    shutil.move(file_path, destination_path)