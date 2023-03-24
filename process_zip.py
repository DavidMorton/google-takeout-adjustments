from zipfile import ZipFile
from PIL import ImageFile, Image
import os
from io import BytesIO
import shutil
import json
from datetime import datetime
from win32_setctime import setctime

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
            proposed_exif_tag = time_taken.strftime('%Y:%m:%d %H:%M:%S')
            exif[306] = proposed_exif_tag
            im.save(file)
    except:
        pass
    setctime(file, timestamp)
    os.utime(file, (timestamp, timestamp))

def process_folder(folder):
    json_files = [f for f in os.listdir(folder) if f.lower().endswith('.json')]
    for json_file in json_files:
        full_path = os.path.join(folder, json_file)
        with open(full_path, 'r') as f:
            json_obj = json.load(f)
        target_file = os.path.join(folder, json_obj['title'])
        
        timestamp = int(json_obj['photoTakenTime']['timestamp'])
        if not os.path.exists(target_file):
            root_name = json_obj['title']
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
        if start_time.timestamp() < os.path.getctime(os.path.join(folder, f)):
            os.remove(os.path.join(folder, f))

def rename_for_clarity(folder, year):
    all_files = [f for f in os.listdir(folder)]
    for f in all_files:
        os.rename(os.path.join(folder, f), os.path.join(folder, f'{year}_{f}'))

year = 2020
takeout_name = "20230324T132441Z"
output_path = "C:\\Users\\dvdmo\\Downloads\\Takeout_Images_2015\\"
source_dir = "C:\\Users\\dvdmo\\Downloads\\"

start_time = datetime.now()
print(start_time.timestamp())
#start_time = datetime.fromtimestamp(1679592063.331041)
process_zip_files(source_dir, takeout_name, output_path)
process_folder(output_path)
delete_extras(output_path, start_time)
#rename_for_clarity(output_path, year)



#def set_exif(file):

#get_exif("C:\\Users\\dvdmo\\OneDrive\\Pictures\\00100lrPORTRAIT_00100_BURST20200905200243563_COVER.jpg")
#get_exif("C:\\Users\\dvdmo\\OneDrive\\Pictures\\Finished Artwork\\20210312 - Galactacus.jpg")

