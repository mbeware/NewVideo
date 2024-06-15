from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileMovedEvent,FileCreatedEvent
import os
import ffmpeg
import m3u8

from flask import Flask, render_template_string, request, jsonify


app = Flask(__name__)
folder_to_monitor = "/mnt/AllVideo/NewVideo"
playlist_path = '/mnt/AllVideo/Playlists/Series.m3u8'

def add_entry_to_m3u8(playlist_path, video_path):
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


class VideoFileHandler(FileSystemEventHandler):
    def __init__(self, folder):
        self.folder = folder
        self.newf = []
        self.block = False

    def on_created(self, event):
        if not self.block:
            self.block=True        
            if event.is_directory:
                return
            if event.src_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                if not (event.src_path in self.newf): 
                    self.newf.append(event.src_path)
                    add_entry_to_m3u8(playlist_path,event.src_path)
                    print(f"New video file detected: {event.src_path}")
                else:
                    print(f"Duplicate video file detected and not added: {event.src_path}")
        self.block=False




@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>New video to watch</title>
        <style>
            .hidden { display: none; }
            .toggle { cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>web interface no implemented yet</h1>
    </body>
    </html>
    """)
 

if __name__ == "__main__":
    event_handler = VideoFileHandler(folder_to_monitor)
    observer = Observer()
    observer.schedule(event_handler, folder_to_monitor, recursive=True,event_filter=[FileCreatedEvent])

    observer.start()

    try:
        app.run(port=5000, debug=True)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
