# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os
import sys
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env import INDEXING_DIR, STOCKS_DIRS


WORKERS = 8
indexed_dir = os.path.join(INDEXING_DIR, 'indexed')
thumbnails_dir = os.path.join(INDEXING_DIR, 'thumbnails')


if not os.path.isdir(indexed_dir):
    os.makedirs(indexed_dir)

if not os.path.isdir(thumbnails_dir):
    os.makedirs(thumbnails_dir)


def render_stock(stock_path):
    first_frame = 1
    last_frame = 10
    frame_rate = 24

    total_frames = last_frame - first_frame
    frames = 300 if total_frames > 300 else total_frames
    scale = 400

    seconds = float(frames) / float(frame_rate)

    basename = os.path.basename(stock_path).rsplit('_', 1)[0].rsplit('.', 1)[0]
    output_dir = '{}/{}_{}'.format(indexed_dir,
                                   os.path.basename(os.path.dirname(stock_path)), basename)

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    output = '{}/{}_%d.jpg'.format(output_dir, basename)

    ext = stock_path.split('.')[-1]

    if ext in ['mp4', 'mov']:
        cmd = 'ffmpeg -i "{}" -vf scale={}:-1 -q:v 1 -ss 0 -t {} "{}"'.format(
            stock_path, scale, seconds, output)

    elif any(fmt in stock_path for fmt in ['%02d', '%03d', '%04d', '%05d']):
        cmd = 'ffmpeg -start_number {} -i "{}" -vf scale={}:-1 -q:v 1 -vframes {} "{}"'.format(
            first_frame, stock_path, scale, frames, output)

    else:
        cmd = 'ffmpeg -i "{}" -vf scale={}:-1 -q:v 1 "{}/{}.jpg"'.format(
            stock_path, scale, output_dir, basename)

    try:
        subprocess.run(cmd, check=True, shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())
        print('\n' + cmd)


def extract_stocks():
    stocks = []
    scanned_dirs = []

    for folder in STOCKS_DIRS:
        for root, _, files in os.walk(folder):
            for f in files:
                ext = f.split('.')[-1]

                if ext in ['mov', 'mp4']:
                    stock_path = os.path.join(root, f)
                    if not stock_path in stocks:
                        stocks.append(stock_path)
                    continue

                if not ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'exr']:
                    continue

                sequence_dir = root
                if sequence_dir in scanned_dirs:
                    continue
                scanned_dirs.append(sequence_dir)

                sequences, textures = separate_images_and_sequences(
                    sequence_dir)

                stocks.extend(sequences)
                stocks.extend(textures)

    return stocks


def separate_images_and_sequences(folder):
    files = sorted(os.listdir(folder))
    sequence_pattern = re.compile(r"(.*?)(\d+)(\.\w+)$")

    unique_images = []
    sequences = {}

    for file in files:
        match = sequence_pattern.match(file)
        if match:
            base, frame, ext = match.groups()
            sequences[f"{base}{ext}"] = f"{folder}/{base}%0{len(frame)}d{ext}"
        else:
            unique_images.append(os.path.join(folder, file))

    return list(sequences.values()), unique_images


with ProcessPoolExecutor(max_workers=WORKERS) as executor:
    executor.map(render_stock, extract_stocks())
