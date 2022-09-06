"""Timecode manipulation"""
import sys

FRAME_PER_SECOND = 30
SECOND_PER_MINUTE = 60
MINUTE_PER_HOUR = 60

def frm_to_sec(frames):
    return frames / FRAME_PER_SECOND

def sec_to_strh(secs):

    minute_seconds = secs % SECOND_PER_MINUTE
    minutes = (secs - minute_seconds) / SECOND_PER_MINUTE
    hour_minutes = minutes % MINUTE_PER_HOUR
    hours = (minutes - hour_minutes) / MINUTE_PER_HOUR

    second_string = f"{int(minute_seconds)}"
    if minute_seconds < 10:
        second_string = "0" + second_string

    minute_string = f"{int(hour_minutes)}"
    if hour_minutes < 10 and hours > 0:
        minute_string = "0" + minute_string

    hour_string = f"{int(hours)}:" if hours > 0 else ""

    return f"{hour_string}{minute_string}:{second_string}"

def frm_to_strh(frames, show_ms=True):
    negative = frames < 0
    if negative:
        frames = -frames
    millisecond_frames = frames % FRAME_PER_SECOND
    seconds = (frames - millisecond_frames) / FRAME_PER_SECOND

    hms_string = sec_to_strh(seconds)
    if not show_ms:
        return hms_string

    rest_millisecond = millisecond_frames % (FRAME_PER_SECOND/10)
    hundred_millisecond = (millisecond_frames - rest_millisecond) / (FRAME_PER_SECOND/10)

    if rest_millisecond == 0:
        rest_string = "00"
    elif rest_millisecond == 1:
        rest_string = "33"
    else:
        rest_string = "67"

    ms_string = f".{int(hundred_millisecond)}{rest_string}"

    minus = "\u2013" if negative else ""

    return f"{minus}{hms_string}{ms_string}"

if __name__ == "__main__":
    frames = int(sys.argv[1])
    show_ms = len(sys.argv) > 2 and sys.argv[2] == "--ms"
    print(frm_to_strh(frames, show_ms))
