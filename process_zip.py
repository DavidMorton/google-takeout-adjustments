from zipfile import ZipFile
from PIL import ImageFile, Image
import os
from io import BytesIO
import shutil
import json
from datetime import datetime
import re
#from win32_setctime import setctime

def process_zip_file(zip_path, output_dir):
    zip = ZipFile(zip_path)
    excluded_extensions = []
    excluded_extensions = ['.mp', '.html']
    suitable_files = [z.filename for z in zip.filelist if not any([z.filename.lower().endswith(x) for x in excluded_extensions])]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for z in suitable_files:
        b = zip.open(z, mode='r').read()

        basename = os.path.basename(z)
        with open(os.path.join(output_dir, basename), 'wb') as f:
            f.write(b)
        print(z)

def process_zip_files(source_dir, takeout_name, output_dir):

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    zip_files = sorted([f for f in os.listdir(source_dir) if takeout_name.lower() in f.lower() and f.lower().endswith('.zip')])
    for f in zip_files:
        zip = ZipFile(os.path.join(source_dir, f))
        #excluded_extensions = []
        excluded_extensions = ['.mp', '.html']
        suitable_files = [z.filename for z in zip.filelist if not any([z.filename.lower().endswith(x) for x in excluded_extensions])]
        for z in suitable_files:
            b = zip.open(z, mode='r').read()

            basename = os.path.basename(z)
            with open(os.path.join(output_dir, basename), 'wb') as f:
                f.write(b)

def ensure_timestamp(file, time_taken:datetime):
    timestamp = time_taken.timestamp()
    try:
        im = Image.open(file)
        exif = im.getexif()
        creation_time = exif.get(306)
        if creation_time is None:
            name_without_extension = '.'.join(os.path.basename(file).split('.')[:-1])
            try:
                time_taken = datetime.strptime(name_without_extension, '%Y-%m-%d %H.%M.%S')
                timestamp = time_taken.timestamp()
            except:
                pass
            proposed_exif_tag = time_taken.strftime('%Y-%m-%d %H.%M.%S')
            exif[306] = proposed_exif_tag
            im.save(file, exif=exif)
    except Exception as e:
        pass
    #setctime(file, timestamp)
    os.utime(file, (timestamp, timestamp))

def get_json_file_count(folder):
    return len([f for f in os.listdir(folder) if f.lower().endswith('.json')])

def get_all_file_count(folder):
    return len([f for f in os.listdir(folder)])

def process_folder(folder):
    json_files = [f for f in os.listdir(folder) if f.lower().endswith('.json')]
    for json_file in json_files:
        full_path = os.path.join(folder, json_file)
        with open(full_path, 'r') as f:
            json_obj = json.load(f)
        target_file = os.path.join(folder, json_obj['title']).replace("'", '_')
        # Need to handle the case of files that are doubled...
        m = re.match('.*(\(\d*\)).json$', json_file)
        if m is not None:
            added_buffer = m.group(1)
            target_file = f'{".".join(target_file.split(".")[:-1])}{added_buffer}.{target_file.split(".")[-1]}'
        timestamp = int(json_obj['photoTakenTime']['timestamp'])
        if not os.path.exists(target_file):
            root_name = target_file
            extension = root_name.split('.')[-1]
            root_file_name = '.'.join(root_name.split('.')[:-1])
            while not os.path.exists(os.path.join(folder, f'{root_file_name}.{extension}')):
                root_file_name = root_file_name[:-1]

            counter = 1
            root_cache = root_file_name
            new_file_name = f'{root_cache}({counter})'
            while os.path.exists(os.path.join(folder, f'{new_file_name}.{extension}')):
                root_file_name = new_file_name
                counter = counter + 1
                new_file_name = f'{root_cache}({counter})'

            target_file = os.path.join(folder, f'{root_file_name}.{extension}')

        ensure_timestamp(target_file, datetime.fromtimestamp(timestamp))
        os.remove(os.path.join(folder, json_file))


def delete_extras(folder, start_time:datetime):
    all_files = [f for f in os.listdir(folder)]
    for f in all_files:
        if start_time.timestamp() < os.path.getmtime(os.path.join(folder, f)):
            os.remove(os.path.join(folder, f))

def rename_for_clarity(folder, year):
    all_files = [f for f in os.listdir(folder)]
    for f in all_files:
        os.rename(os.path.join(folder, f), os.path.join(folder, f'{year}_{f}'))

takeout_name = "20230402T20aoeuaoeu4454Z"
output_path = "/Users/davidmorton/Downloads/Takeout_Images_2021/"
source_dir = "/Users/davidmorton/Downloads"

start_time = datetime.now()

process_zip_files(source_dir, takeout_name, output_path)
json_file_count = get_json_file_count(output_path)
process_folder(output_path)
delete_extras(output_path, start_time)
all_file_count = get_all_file_count(output_path)

print(f'JSON Files: {json_file_count}, All Files: {all_file_count}')
if (json_file_count == all_file_count):
    print("Everything is okay!")

