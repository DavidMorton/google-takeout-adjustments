from PIL import Image
import os
from datetime import datetime
# f = "//Users//davidmorton//Downloads//Takeout//Google Photos//Photos from 2001//2016-12-24 20.21.12.jpg"
# i = Image.open(f)
# e = i.getexif()
# print(e.get(306))
# text = '.'.join(os.path.basename(f).split('.')[:-1])
# print(text)
# filename = datetime.strptime(text, '%Y-%m-%d %H.%M.%S')
# print(filename)
# e[306] = int(filename.timestamp())
# i.save(f, exif=e)
# os.utime(f, (filename.timestamp(), filename.timestamp()))
# #print(os.utime(f))
# #print(e.get(306))

def set_exif(folder):
    for file in os.listdir(folder):
        full_path = os.path.join(folder, file)
        ctime_timestamp = os.stat(full_path).st_birthtime
        ctime_datetime:datetime = datetime.fromtimestamp(ctime_timestamp)
        try:
            i = Image.open(full_path)
            exif = i.getexif()
            stamped_date = exif.get(306)
            if stamped_date is None:
                new_stamped_date = datetime.strftime(ctime_datetime, '%Y-%m-%d %H.%M.%S')
                exif[306] = new_stamped_date
                i.save(full_path, exif=exif)
                os.utime(full_path, (ctime_timestamp, ctime_timestamp))
                print('updated ' + file)
        except:
            pass
        
set_exif("/Users/davidmorton/Downloads/Takeout_Images_2013")