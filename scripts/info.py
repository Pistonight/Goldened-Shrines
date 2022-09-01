import toml
import re
import os
def get_seg_spaced_name(segment):
    #https://www.geeksforgeeks.org/python-split-camelcase-string-to-individual-strings/
    return " ".join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', segment))

def get_3char_seg_num(num):
    num = int(num)
    if num < 10:
        return f"00{num}"
    if num < 100:
        return f"0{num}"
    return str(num)

def get_seg_source_mp4(segment):
    return f"build/download/{segment}.mp4"

def get_seg_overlay_mp4(segment):
    return f"build/encode/{segment}.mp4"

def get_seg_time_toml(segment):
    return f"build/time/{segment}.time.toml"

def get_seg_info(segment, field=None):
    with open(f"segments/{segment}.toml", "r", encoding="utf-8") as file:
        info = toml.load(file)
    if field is None:
        return info
    return info[field]

def get_seg_time_info(segment, field=None):
    with open(get_seg_time_toml(segment), "r", encoding="utf-8") as file:
        info = toml.load(file)
    if field is None:
        return info
    return info[field]

def set_seg_time_info(segment, info):
    with open(get_seg_time_toml(segment), "w+", encoding="utf-8") as file:
        toml.dump(info, file)

def get_seg_split_overlay_dir(segment):
    return f"build/splits/{segment}"

def format_seg_split_frame(segment, index):
    return "%s/%05d.png" % (get_seg_split_overlay_dir(segment), index)

def set_seg_split_overlay_frame(segment, image, index):
    image.save(format_seg_split_frame(segment, index))

def get_seg_split_overlay_series(segment):
    return f"{get_seg_split_overlay_dir(segment)}/%05d.png"

def get_seg_name_file():
    return "segments/_order.txt"

def load_seg_names():
    seg_names = []
    with open(get_seg_name_file(), "r", encoding="utf-8") as seg_file:
        for seg_file_line in seg_file:
            seg_name = seg_file_line.rstrip()
            if len(seg_name) > 0:
                seg_names.append(seg_name)
            
    return seg_names

