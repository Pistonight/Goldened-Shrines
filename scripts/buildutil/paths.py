def seg_download_mp4(segment):
    return f"build/download/{segment}.mp4"

def seg_overlay_mp4(segment):
    return f"build/encode/{segment}.mp4"

def seg_normalized_mp4(segment):
    return f"build/normalize/{segment}.mp4"

def seg_time_toml(segment):
    return f"build/time/{segment}.time.toml"

def seg_splits_dir(segment):
    return f"build/splits/{segment}"

def seg_toml(segment):
    return f"segments/{segment}.toml"

def seg_order_txt():
    return "segments/_order.txt"

def runners_toml():
    return "runners.toml"

def profiles_toml():
    return "profiles.toml"

def seg_split_frame(segment, index):
    return "%s/%05d.png" % (seg_splits_dir(segment), index)

def seg_split_series(segment):
    return f"{seg_splits_dir(segment)}/%05d.png"

def hash_txt(name):
    return f"build/hash/{name}.hash.txt"

def log_base(name):
    return f"build/logs/{name}"

def timetable_html():
    return "docs/latest.html"

def index_html():
    return "docs/index.html"
