import ffmpeg
import m3u8
import os

def add_entry_to_m3u8(playlist_path, video_path):
    # Extract the name (title) from the video file's metadata
    try:
        metadata = ffmpeg.probe(video_path)
        format_info = metadata.get('format', {})
        name = format_info.get('tags', {}).get('title', None)
        
        if not name:
            # Extract the filename without path and extension
            base_name = os.path.basename(video_path)
            name, _ = os.path.splitext(base_name)
            # Replace dots with spaces
            name = name.replace('.', ' ')
    except ffmpeg.Error as e:
        print(f"Error extracting metadata: {e}")
        # Extract the filename without path and extension
        base_name = os.path.basename(video_path)
        name, _ = os.path.splitext(base_name)
        # Replace dots with spaces
        name = name.replace('.', ' ')

    # Load the existing M3U8 playlist
    playlist = m3u8.load(playlist_path)

    # Create a new entry
    new_entry = m3u8.Segment(uri=video_path, title=name, duration=-1)

    # Append the new entry to the playlist
    playlist.segments.append(new_entry)

    # Save the updated playlist back to the file
    with open(playlist_path, 'w') as f:
        f.write(playlist.dumps())

# Example usage
playlist_path = '/mnt/AllVideo/Playlists/Series.m3u8'
video_path = '/mnt/AllVideo/NewVideo/The.boys.S04E03.1080p.HEVC.x265-MeGusta/The.boys.S04E03.1080p.HEVC.x265-MeGusta.mkv'
add_entry_to_m3u8(playlist_path, video_path)