import os
import datetime



# Define the base directory and the playlist directory
base_dir = '/mnt/AllVideo'
playlist_dir = os.path.join(base_dir, '000_Playlists/Playlists_all')
#playlist_dir = '/mnt/Data004/playlist/Playlists_all'
excluded_dirs = os.path.join(base_dir, '000_Playlists') 

# Ensure the playlist directory exists
os.makedirs(playlist_dir, exist_ok=True)

# Supported video file extensions
video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm']

# Date filter: Only include files modified after this date
date_filter = datetime.datetime(1990, 8, 4)


# Function to create symlinks for video files
def create_symlinks():
    for root, dirs, files in os.walk(base_dir):
        # Skip the playlist directory 
        if root.startswith(playlist_dir) or root.startswith(excluded_dirs):
            continue
        if root.find('.Trash') != -1:
            continue
        
        # List of video files after the date filter
        video_files = []
        for file in files:
            # Check if the file has a video extension
            if any(file.lower().endswith(ext) for ext in video_extensions):
                source_file = os.path.join(root, file)
                # Check the last modification time of the file
                mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(source_file))
                if mod_time > date_filter:
                    video_files.append(file)
        
        # If there are no video files after the date filter, skip this directory
        if not video_files:
            continue

        # Determine the relative path of the current folder from base_dir
        relative_path = os.path.relpath(root, base_dir)
        
        # Create the corresponding directory in the playlist directory
        playlist_subdir = os.path.join(playlist_dir, relative_path)
        os.makedirs(playlist_subdir, exist_ok=True)

        for file in video_files:
            source_file = os.path.join(root, file)
            link_name = os.path.join(playlist_subdir, file)
            
            # Remove existing symlink if it exists
            if os.path.islink(link_name):
                os.unlink(link_name)
            
            # Create the symlink
            os.symlink(source_file, link_name)
            print(f"Symlink created: {link_name} -> {source_file}")

# Run the function to create symlinks
create_symlinks()