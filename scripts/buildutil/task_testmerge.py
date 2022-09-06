from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths, time, timecode
import os

class TaskDefTestMerge(ITaskDefinition):
    def __init__(self, segment, segment_name, total_segment, before_name, after_name):
        super().__init__()
        self.segment = segment
        self.total_segment = total_segment
        self.segment_name = segment_name
        self.before_name = before_name
        self.after_name = after_name

    def is_gpu(self):
        return True
    def get_description(self):
        return f"Render test segment {self.segment_name}"
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

    def _exe_args(self):
        has_beginning = "0"
        has_ending = "0"
        segments = []
        if self.segment == 0:
            has_beginning = "1"
        else:
            segments.append(self.before_name)
        segments.append(self.segment_name)
        if self.segment == self.total_segment - 1:
            has_ending = "1"
        else:
            segments.append(self.after_name)

        args = [
            "python3", "scripts/build_merge.py",
            has_beginning, has_ending,
            "build/merge/test.mp4",
            "build/merge/middle.mp4",
            "build/merge/testlist.txt"
        ]
        args.extend(segments)
        return args
