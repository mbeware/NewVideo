from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
import json

app = Flask(__name__)
video_files = defaultdict(list)  # Group by year/month
new_files_by_day = defaultdict(list)  # Files added within the last week
one_week_ago = datetime.now() - timedelta(days=7)
state_file = ".watcher.state"
folder_to_monitor = "/mnt/BH-03/NewVideo"
state = {}

def load_state():
    global state
    try:
        with open(os.path.join(folder_to_monitor, state_file), 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}

def save_state():
    with open(os.path.join(folder_to_monitor, state_file), 'w') as f:
        json.dump(state, f)

def add_file(filepath):
    file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
    year_month = file_date.strftime("%Y-%m")
    video_files[year_month].append((file_date, filepath))

    if file_date > one_week_ago:
        day = file_date.strftime("%Y-%m-%d")
        new_files_by_day[day].append((file_date, filepath))

class VideoFileHandler(FileSystemEventHandler):
    def __init__(self, folder):
        self.folder = folder
        self.scan_existing_files()

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            add_file(event.src_path)
            print(f"New video file detected: {event.src_path}")

    def scan_existing_files(self):
        for root, _, files in os.walk(self.folder):
            for file in files:
                if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    add_file(os.path.join(root, file))

@app.route('/')
def index():
    sorted_new_files_by_day = {
        k: sorted(v, key=lambda x: x[0], reverse=True)
        for k, v in sorted(new_files_by_day.items(), reverse=True)
    }
    sorted_video_files = {
        k: sorted(v, key=lambda x: x[0], reverse=True)
        for k, v in sorted(video_files.items(), reverse=True)
    }
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Files</title>
        <style>
            .hidden { display: none; }
            .toggle { cursor: pointer; }
        </style>
        <script>
            function toggleVisibility(id) {
                var element = document.getElementById(id);
                if (element.classList.contains('hidden')) {
                    element.classList.remove('hidden');
                } else {
                    element.classList.add('hidden');
                }
            }

            function updateState(filepath, key, checked) {
                fetch('/update_state', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ filepath: filepath, key: key, checked: checked })
                }).then(response => {
                    if (!response.ok) {
                        alert('Failed to update state');
                    }
                });
            }
        </script>
    </head>
    <body>
        <h1>New Video Files (Last Week)</h1>
        {% for day, files in sorted_new_files_by_day.items() %}
        <h2>{{ day }}</h2>
        <ul>
            {% for date, video in files %}
            <li>
                <input type="checkbox" {% if state.get(video, {}).get('watched') %}checked{% endif %} onclick="updateState('{{ video }}', 'watched', this.checked)"> Watched
                <input type="checkbox" {% if state.get(video, {}).get('interesting') %}checked{% endif %} onclick="updateState('{{ video }}', 'interesting', this.checked)"> Interesting
                <a href="{{ video }}" download>{{ video }}</a> ({{ date.strftime("%Y-%m-%d %H:%M:%S") }})
            </li>
            {% endfor %}
        </ul>
        {% endfor %}
        <h1>All Video Files</h1>
        {% for year_month, files in sorted_video_files.items() %}
        <h2 class="toggle" onclick="toggleVisibility('{{ year_month }}')">{{ year_month }}</h2>
        <ul id="{{ year_month }}" class="hidden">
            {% for date, video in files %}
            <li>
                <input type="checkbox" {% if state.get(video, {}).get('watched') %}checked{% endif %} onclick="updateState('{{ video }}', 'watched', this.checked)"> Watched
                <input type="checkbox" {% if state.get(video, {}).get('interesting') %}checked{% endif %} onclick="updateState('{{ video }}', 'interesting', this.checked)"> Interesting
                <a href="{{ video }}" download>{{ video }}</a> ({{ date.strftime("%Y-%m-%d %H:%M:%S") }})
            </li>
            {% endfor %}
        </ul>
        {% endfor %}
    </body>
    </html>
    """, sorted_new_files_by_day=sorted_new_files_by_day, sorted_video_files=sorted_video_files, state=state)

@app.route('/update_state', methods=['POST'])
def update_state():
    data = request.json
    filepath = data['filepath']
    key = data['key']
    checked = data['checked']
    if filepath not in state:
        state[filepath] = {}
    state[filepath][key] = checked
    save_state()
    return '', 204

if __name__ == "__main__":
    load_state()
    
    event_handler = VideoFileHandler(folder_to_monitor)
    observer = Observer()
    observer.schedule(event_handler, folder_to_monitor, recursive=True)
    observer.start()

    try:
        app.run(port=5000, debug=True)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
