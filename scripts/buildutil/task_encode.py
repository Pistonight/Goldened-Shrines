from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths
from buildutil import time
import os

from buildutil.task_download import TaskDefDownload
from buildutil.task_splits import GENERATE_SPLIT_STEP

# 5 modes
# convert - segment = None, just reencode
# intro - segment = None, segment_name = "_intro", encode and fade in
# regular - segment = i
# outro - segment = None, segment_name = "_outro"
# transition - segment = None, segment_name = "_outro_transition", fade out
class TaskDefEncodeOverlay(ITaskDefinition):
    def __init__(self, segment, segment_name):
        super().__init__()
        self.segment = segment
        self.segment_name = segment_name
    def is_gpu(self):
        return True
    def get_description(self):
        return f"Encode Overlay for {self.segment_name}"
    def get_color(self):
        return "\033[1;34m"
    def get_dependencies(self):
        if self.segment is None:
            if self.segment_name == "_intro":
                return [(TaskType.GenerateIntro, 0)]
            if self.segment_name.startswith("_outro"):
                return [(TaskType.GenerateOutro, 0)]
            return [
                (TaskType.DownloadTrailer, 0),
                (TaskType.DownloadCredits, 0),
                (TaskType.DownloadTransition, 0)
            ]
        return [
            (TaskType.GenerateSplit_0, self.segment),
            (TaskType.GenerateSplit_1, self.segment),
            (TaskType.GenerateSplit_2, self.segment),
            (TaskType.GenerateSplit_3, self.segment),
            (TaskType.GenerateSplit_4, self.segment),
            (TaskType.GenerateSplit_5, self.segment),
            (TaskType.GenerateSplit_6, self.segment),
            (TaskType.GenerateSplit_7, self.segment),
        ]
    def _name(self) -> str:
        return f"{self.segment_name}.encode"
    def _hash_files(self) -> list[str]:
        files = [
            paths.hash_txt(TaskDefDownload(self.segment_name)._name())
        ]
        if self.segment is not None:
            for i in range(GENERATE_SPLIT_STEP):
                files.append(paths.seg_split_frame(self.segment_name, i))
        elif self.segment_name == "_intro":
            files.append(paths.seg_split_frame("_intro", 0))
        else:
            files.append(paths.seg_split_frame("_outro", 0))
        files.append(paths.seg_overlay_mp4(self.segment_name))
        return files

    def prepare(self):
        os.makedirs("build/encode", exist_ok=True)

    def _exe_args(self):
        if self.segment_name.startswith("_outro"):
            input_overlay = paths.seg_split_frame("_outro", 0)
        elif self.segment_name in ("_trailer", "_credits"):
            input_overlay = None
        else:
            input_overlay = paths.seg_split_series(self.segment_name)
        return encode_args(
            paths.seg_download_mp4(self.segment_name),
            input_overlay,
            paths.seg_overlay_mp4(self.segment_name),
            self.segment_name
        )

def encode_args(input_mp4, input_png, output_mp4, segment_name):
    # Global
    args = [
        "ffmpeg",
        # Force overwrite existing
        "-y",
        # CUDA acceleration
        "-hwaccel", "nvdec",
        "-hwaccel_output_format", "cuda"
    ]
    # Input mp4
    args.extend([
        "-i", input_mp4
    ])
    # Basic filter
    filter_complex = "scale_cuda=1920:1080,hwdownload,format=nv12 [base]"
    out_v_stream = "[base]"
    out_a_stream = "0:a"
    
    # Fade out for outro transition (before overlaying)
    if segment_name == "_outro_transition":
        filter_complex+=f"; {out_v_stream}fade=t=out:d=2:st=2:c=white [fade]; [0:a]afade=t=out:st=2:d=2 [aout]"
        out_v_stream = "[fade]"
        out_a_stream = "[aout]"

    if segment_name == "_credits":
        filter_complex+=f"; {out_v_stream}fade=t=in:d=1.5:st=0:c=white [fade]"
        out_v_stream = "[fade]"

    # Overlay
    if input_png is not None:
        args.extend([
            # Frame rate of the overlay
            "-framerate",             "30",
            "-thread_queue_size",     "4096",
            "-i",                     input_png,
        ])
        filter_complex+=f"; {out_v_stream}[1:v]overlay=10:728 [out]"
        out_v_stream = "[out]"

    # Fade out for outro (after overlaying)
    if segment_name == "_outro":
        # Time the outro to get seconds to start fade out
        outro_frames = time.execute_seg_frame_count("_outro")
        # Fade out start 1s before end
        outro_fade_start = int(round(outro_frames/30))-2
        filter_complex+=f"; {out_v_stream}fade=t=out:d=1:st={outro_fade_start}:c=white [fade2]"
        out_v_stream = "[fade2]"

    # Fade in for intro
    elif segment_name == "_intro":
        filter_complex+=f"; {out_v_stream}fade=t=in:st=1:d=1 [fade]"
        out_v_stream = "[fade]"


    bit_rate = "6M" if not segment_name.startswith("_") else "20M"
    # Filter and output
    args.extend([
        "-filter_complex", filter_complex,
        "-framerate", "30",
        "-map", out_v_stream,
        "-map", out_a_stream,
        "-c:v", "h264_nvenc",
        "-b:v", bit_rate,
        "-c:a", "aac",
        "-fps_mode", "passthrough",
        output_mp4
    ])

    return args

    # ffmpeg -i transition.mp4 -vf "fade=t=out:d=2:st=2:c=white" -af "afade=t=out:st=2:d=2" out.mp4


