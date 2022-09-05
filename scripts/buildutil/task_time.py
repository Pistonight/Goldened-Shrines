from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths
import os

from buildutil.task_download import TaskDefDownload

class TaskDefTime(ITaskDefinition):
    def __init__(self, segment, segment_name, segment_context) -> None:
        super().__init__()
        self.segment = segment
        self.segment_name = segment_name
        self.segment_context = segment_context

    def get_description(self):
        return f"Time {self.segment_name} segment"
    def get_color(self):
        return "\033[1;32m"
    def get_dependencies(self):
        deps = [(TaskType.Download, self.segment)]
        if self.segment > 0:
            deps.append((TaskType.GenerateTime, self.segment-1))
        return deps

    def _name(self) -> str:
        return f"{self.segment_name}.time"
    def _hash_files(self) -> list[str]:
        return [
            paths.seg_time_toml(self.segment_name),
            paths.seg_order_txt(),
            paths.hash_txt(TaskDefDownload(self.segment_name)._name())
        ]

    def prepare(self):
        os.makedirs("build/time", exist_ok=True)
    def _exe_args(self):
        args = [
            "python3", "scripts/build_time.py",
            self.segment_name
        ]
        args.extend(self.segment_context)
        return args
