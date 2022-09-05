import toml
import re
import functools
from buildutil import paths
def get_seg_spaced_name(segment:str):
    segment_name = segment.split(".", 1)[0]
    #https://www.geeksforgeeks.org/python-split-camelcase-string-to-individual-strings/
    return " ".join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', segment_name))

def get_3char_seg_num(num):
    num = int(num)
    if num < 10:
        return f"00{num}"
    if num < 100:
        return f"0{num}"
    return str(num)

@functools.cache
def get_seg_info(segment):
    with open(paths.seg_toml(segment), "r", encoding="utf-8") as file:
        return toml.load(file)

@functools.cache
def get_seg_time_info(segment):
    with open(paths.seg_time_toml(segment), "r", encoding="utf-8") as file:
        return toml.load(file)


def set_seg_time_info(segment, info):
    with open(paths.seg_time_toml(segment), "w+", encoding="utf-8") as file:
        toml.dump(info, file)

def set_seg_split_overlay_frame(segment, image, index):
    image.save(paths.seg_split_frame(segment, index))

@functools.cache
def get_seg_names():
    seg_names = []
    with open(paths.seg_order_txt(), "r", encoding="utf-8") as seg_file:
        for seg_file_line in seg_file:
            seg_name = seg_file_line.rstrip()
            if len(seg_name) > 0:
                seg_names.append(seg_name)
            
    return seg_names

@functools.cache
def get_runners_info():
    with open(paths.runners_toml(), "r", encoding="utf-8") as file:
        return toml.load(file)

@functools.cache
def get_profiles():
    with open(paths.profiles_toml(), "r", encoding="utf-8") as file:
        return toml.load(file)

def load_runner_html_map():
    runners = {}
    runner_toml = get_runners_info()
    for runner_name, runner in runner_toml.items():
        html = "<span>"
        display_name = runner["display_name"]
        if "src" in runner:
            link_src = runner["src"]
            html+=f"<a href=\"{link_src}\">{display_name}</a>"
        else:
            html+=display_name
        for social in ("twitch", "twitter", "youtube", "bilibili"):
            if social in runner:
                link_social = runner[social]
                html+=f" <a href=\"{link_social}\"><img width=\"16px\" height=\"16px\" src=\"https://www.speedrun.com/images/socialmedia/{social}.png\"/></a>"
        html+="</span>"
        runners[runner_name] = html
        
    return runners

