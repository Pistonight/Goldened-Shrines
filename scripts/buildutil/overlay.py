"""Generate split images"""
# overlay.py <seg name> <seed> <step>
from buildutil import info
from buildutil.timecode import frm_to_strh
from PIL import Image, ImageDraw, ImageFont

BACKGROUND_PATH="docs/images/Background.png"
TIMER_FONT_PATH="docs/fonts/Calibri-Bold.ttf"
TEXT_FONT_PATH="docs/fonts/OpenSans-Regular.ttf"
TIME_FONT_PATH="docs/fonts/OpenSans-Bold.ttf"

COLOR_GOLD=(0xff,0xd7,0x00,0xff)
COLOR_GREY=(0x88,0x88,0x88,0xff)
COLOR_BLACK=(0x00,0x00,0x00,0xff)
COLOR_WHITE=(0xfd,0xfd,0xfd,0xff)

ICON_X = 12
SPLIT_NAME_X=80
SPLIT_TIME_X=272
SEG_TIME_X=182
TIMES_Y = 26
SEG_TIMER_X=466

def load_fonts():
    return {
        "timer_big": ImageFont.truetype(TIMER_FONT_PATH, 52),
        "timer_small": ImageFont.truetype(TIMER_FONT_PATH, 40),
        "runner": ImageFont.truetype(TEXT_FONT_PATH, 36),
        "split_name": ImageFont.truetype(TEXT_FONT_PATH, 20),
        "number": ImageFont.truetype(TIME_FONT_PATH, 24),
        "number_small": ImageFont.truetype(TIME_FONT_PATH, 20)
    }

def get_base_image(seg_name, seg_time_info, fonts):
    runner_font = fonts["runner"]
    number_font = fonts["number"]
    split_name_font = fonts["split_name"]
    number_small_font = fonts["number_small"]

    image = Image.open(BACKGROUND_PATH)
    draw = ImageDraw.Draw(image)

    runner = info.get_seg_info(seg_name)["runner"]
    runner_name = info.get_runners_info()[runner]["display_name"]
    segment_num = info.get_3char_seg_num(seg_time_info["shrine_number"])

    # (name, seg_time, split_time, icon)
    # (name, "", "-", icon) for current
    # after current will be after
    splits = []
    for split_data in seg_time_info["splits"]:
        if "segment_time" in split_data:
            splits.append((
                info.get_seg_spaced_name(split_data["name"]),
                frm_to_strh(split_data["segment_time"], show_ms=True),
                frm_to_strh(split_data["split_time"], show_ms=False),
                split_data["icon"]
            ))
        else:
            splits.append((
                info.get_seg_spaced_name(split_data["name"]),
                "",
                "-",
                split_data["icon"]
            ))

    runner_width = draw.textlength(runner_name, font=runner_font)
    x = int(300+((312-runner_width)/2))
    draw.text((x, 212), runner_name, fill=COLOR_GOLD,font=runner_font)

    draw.text((302,172), segment_num, fill=COLOR_BLACK,font=number_font)

    is_current = False
    is_after = False
    if seg_time_info["start_frame"] < 0:
        # special segment
        is_after = True
    for i, split in enumerate(splits):
        name, seg_time, split_time, icon = split
        if split_time=="-":
            if not is_current and not is_after:
                is_current=True
            else:
                is_current=False
                is_after=True
        
        if is_current:
            draw.rectangle(((2, 56*i),(281, 56*i+57)), fill=COLOR_GOLD)
            icon_name=f"docs/images/{icon}_Black_.png"
            seg_time_color=COLOR_BLACK
            main_color=COLOR_BLACK
        else:
            icon_name=f"docs/images/{icon}_Gold_.png"
            seg_time_color=COLOR_GOLD
            main_color=COLOR_WHITE
        if is_after:
            seg_time_color=COLOR_GREY
            main_color=COLOR_GREY
        icon_image = Image.open(icon_name)
        image.paste(icon_image, box=(ICON_X, 2+56*i), mask=icon_image)
        draw.text((SPLIT_NAME_X, 2+56*i), name, fill=main_color, font=split_name_font)

        x = SPLIT_TIME_X - draw.textlength(split_time, font=number_small_font)
        draw.text((x, 2+TIMES_Y+56*i), split_time, fill=main_color, font=number_small_font)

        x = SEG_TIME_X - draw.textlength(seg_time, font=number_small_font)
        draw.text((x, 2+TIMES_Y+56*i), seg_time, fill=seg_time_color, font=number_small_font)
    #image.show()
    return image

def draw_frame(base_image, start_frame, frame, fonts):
    image = base_image.copy()
    draw = ImageDraw.Draw(image)
    total_time = frm_to_strh(start_frame+frame, show_ms=True)
    seg_time = frm_to_strh(frame, show_ms=True)
    time_no_ms = total_time[:-3]
    time_ms = total_time[-3:]

    timer_font_big = fonts["timer_big"]
    timer_font_small = fonts["timer_small"]
    number_font = fonts["number"]

    if start_frame >= 0:
        if frame >= 0:
            color = COLOR_WHITE 
        else:
            color = COLOR_GOLD
    else:
        color = COLOR_GREY

    x=538-draw.textlength(time_no_ms, font=timer_font_big)
    draw.text((x,276), time_no_ms, fill=color,font=timer_font_big)
    draw.text((540,286), time_ms, fill=color,font=timer_font_small)
    if start_frame >=0 and frame >=0:
        x=SEG_TIMER_X-draw.textlength(seg_time, font=number_font)
        draw.text((x,172), seg_time, fill=COLOR_GOLD, font=number_font)
    return image


