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
class TaskDefTestMerge(ITaskDefinition):
    def __init__(self, segment, segment_name, total_segment, before_name, after_name):
        super().__init__()
        self.segment = segment
        self.total_segment = total_segment
        self.segment_name = segment_name
        self.before_name = before_name
        self.after_name = after_name

    def get_description(self):
        return f"Test merged segment {self.segment_name}"
    def get_color(self):
        return "\033[1;36m"
    def get_dependencies(self):
        if self.segment == 0:
            return [
                (TaskType.EncodeTrailer, 0),
                (TaskType.EncodeIntro, 0),
                (TaskType.Normalize, self.segment),
                (TaskType.Normalize, self.segment+1)
            ]
        if self.segment == self.total_segment - 1:
            return [
                (TaskType.EncodeCredits, 0),
                (TaskType.EncodeOutro, 0),
                (TaskType.NormalizeExtra, 0),
                (TaskType.Normalize, self.segment),
                (TaskType.Normalize, self.segment-1)
            ]
        return [
            (TaskType.Normalize, self.segment-1),
            (TaskType.Normalize, self.segment),
            (TaskType.Normalize, self.segment+1)
        ]
    def _name(self) -> str:
        return f"{self.segment_name}.test"
    def update_hash(self, _do_update) -> bool:
        return False

    def prepare(self):
        os.makedirs("build/merge", exist_ok=True)
        files = []
        if self.segment == 0:
            files.append(paths.seg_overlay_mp4("_trailer"))
            files.append(paths.seg_overlay_mp4("_intro"))
        else:
            files.append(paths.seg_normalized_mp4(self.before_name))
        files.append(paths.seg_normalized_mp4(self.segment_name))
        if self.segment == self.total_segment - 1:
            files.append(paths.seg_normalized_mp4("_outro_transition"))
            files.append(paths.seg_overlay_mp4("_outro"))
            files.append(paths.seg_overlay_mp4("_credits"))
        else:
            files.append(paths.seg_normalized_mp4(self.after_name))
        with open("build/merge/testlist.txt", "w+", encoding="utf-8") as out_file:
            for file in files:
                out_file.write(f"file ../../{file}\n")

    def _exe_args(self):

        return [
                "ffmpeg",
                "-y",
                # "-hwaccel", "nvdec",
                # "-hwaccel_output_format", "cuda",
                "-f", "concat",
                "-safe", "0",
                "-i", "build/merge/testlist.txt",
                # "-framerate", "30",
                # "-filter_complex",
                # "scale_cuda=1920:1080,hwdownload,format=nv12 [base]",
                "-c", "copy",
                # "-map", "[base]",
                # "-map", "0:a",
                # "-c:v", "h264_nvenc",
                # "-b:v", "6M",
                # "-c:a", "copy",
                # "-fps_mode", "passthrough",
                "build/merge/test.mp4"
            ]


