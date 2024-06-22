import m3u8

def add_entry_to_m3u8(playlist_path, video_path, video_name):
    # Load the existing M3U8 playlist
    playlist = m3u8.load(playlist_path)

    # Create a new entry
    new_entry = m3u8.Segment(uri=video_path, title=video_name, duration=-1)
    print(f"New entry to add: {new_entry}")
    # Append the new entry to the playlist
    playlist.segments.append(new_entry)

    # Save the updated playlist back to the file
    with open(playlist_path, 'w') as f:
        f.write(playlist.dumps())


import argparse
parser=argparse.ArgumentParser(description="sample argument parser")
parser.add_argument("PlaylistFullName", help="Path and filename of the playlist", default="/tmp/playlist.m3u8")
parser.add_argument("VideoToAdd", help="Path and filename of the video to add")
parser.add_argument("VideoName", help="Video Path and Name")
parser.add_argument("VideoCategory", help="Category of the video")
args=parser.parse_args()

if args.VideoCategory == "RSS_autodownload":
    playlist_path = args.PlaylistFullName
    video_path = args.VideoToAdd
    video_name = args.VideoName 
    add_entry_to_m3u8(playlist_path, video_path, video_name)
else:
    print("Category not RSS_autodownload")
