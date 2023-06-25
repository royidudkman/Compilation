import os
import random
import string
import math
from flask import Flask, render_template, request, jsonify, send_file
from moviepy.editor import VideoFileClip, concatenate_videoclips

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('videos[]')

    if not files:
        return jsonify(message='No files selected'), 400

    for file in files:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return jsonify(message='Upload complete')


@app.route('/mix')
def mix_videos():
    files = [os.path.join(app.config['UPLOAD_FOLDER'], file) for file in os.listdir(app.config['UPLOAD_FOLDER']) if file.endswith('.mp4')]

    if not files:
        return jsonify(message='No videos found'), 400

    video_parts = []
    durations = []

    for file in files:
        video = VideoFileClip(file)
        duration = video.duration
        durations.append(duration)

        part_duration = 5
        num_parts = math.ceil(duration / part_duration)
        parts = [video.subclip(i, i + part_duration) for i in range(0, int(duration) - part_duration + 1, part_duration)]
        video_parts.append(parts)

    max_duration = max(durations)
    mixed_clips = []

    for i in range(num_parts):
        for j, parts in enumerate(video_parts):
            if i < len(parts):
                part = parts[i]
                start_time = i * part_duration
                end_time = min(start_time + part_duration, durations[j])
                print(f"Processing video {j}, part {i}: start={start_time}, end={end_time}")
                mixed_clips.append(part.subclip(0, end_time - start_time))

    final_video = concatenate_videoclips(mixed_clips)
    final_video = final_video.set_fps(30)  # Set the frame rate
    final_video = final_video.resize(height=720)  # Set the height of the video
    mixed_filename = ''.join(random.choices(string.ascii_lowercase, k=10)) + '.mp4'
    mixed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], mixed_filename)
    final_video.write_videofile(mixed_filepath, codec="libx264")

    return send_file(mixed_filepath, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
