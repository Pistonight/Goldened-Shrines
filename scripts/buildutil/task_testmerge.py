from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths
import os

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
                (TaskType.NormalizeTrailer, 0),
                (TaskType.NormalizeIntro, 0),
                (TaskType.Normalize, self.segment),
                (TaskType.Normalize, self.segment+1)
            ]
        if self.segment == self.total_segment - 1:
            return [
                (TaskType.NormalizeCredits, 0),
                (TaskType.NormalizeOutro, 0),
                (TaskType.NormalizeTransition, 0),
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
            files.append(paths.seg_normalized_mp4("_trailer"))
            files.append(paths.seg_normalized_mp4("_intro"))
        else:
            files.append(paths.seg_normalized_mp4(self.before_name))
        files.append(paths.seg_normalized_mp4(self.segment_name))
        if self.segment == self.total_segment - 1:
            files.append(paths.seg_normalized_mp4("_outro_transition"))
            files.append(paths.seg_normalized_mp4("_outro"))
            files.append(paths.seg_normalized_mp4("_credits"))
        else:
            files.append(paths.seg_normalized_mp4(self.after_name))
        with open("build/merge/testlist.txt", "w+", encoding="utf-8") as out_file:
            for file in files:
                out_file.write(f"file ../../{file}\n")

    def _exe_args(self):

        return [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", "build/merge/testlist.txt",
            "-c", "copy",
            "build/merge/test.mp4"
        ]


