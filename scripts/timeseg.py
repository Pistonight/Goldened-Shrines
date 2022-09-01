"""Compute times.gen.toml for segments"""
import wrapper
import info

def compute_time(seg_name, context):
    seg_time = wrapper.execute_get_frame_count(seg_name)
    
    before = None
    for context_name in context:
        if context_name == seg_name:
            break
        before = context_name
    
    if before is None:
        start_frame = 0
        shrine_number = 1
        before_obj = None
    else:
        before_obj = info.get_seg_time_info(before, None)
        start_frame = before_obj["start_frame"] + before_obj["segment_time"]
        if seg_name.find("Tower") != -1 or seg_name.find("Warp") != -1 or seg_name.find("Plateau") != -1:
            shrine_number = before_obj["shrine_number"]
        else:
            shrine_number = min(before_obj["shrine_number"]+1, 120)

    if before_obj is None:
        splits = []
        for context_name in context:
            splits.append({
                "name": context_name,
                "icon": info.get_seg_info(context_name, "icon")
            })
    else:
        splits = []
        for i, before_split in enumerate(before_obj["splits"]):
            if before_split["name"] == context[0]:
                start_copy_index = i
                break
        for before_split in before_obj["splits"][start_copy_index:]:
            if before_split["name"] == before:
                splits.append({
                    "name": before,
                    "icon": before_split["icon"],
                    "segment_time": before_obj["segment_time"],
                    "split_time": start_frame
                })
            else:
                splits.append(before_split)
        if len(splits) < 6:
            splits.append({
                "name": context[-1],
                "icon": info.get_seg_info(context[-1], "icon")
            })
    
    output_obj = {
        "start_frame": start_frame,
        "segment_time": seg_time,
        "shrine_number": shrine_number,
        "splits": splits
    }

    info.set_seg_time_info(seg_name, output_obj)
