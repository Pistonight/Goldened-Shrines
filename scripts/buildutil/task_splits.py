from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths
import os

GENERATE_SPLIT_STEP = 8
class TaskDefGenerateSplits(ITaskDefinition):
    def __init__(self, segment, segment_name, seed) -> None:
        super().__init__()
        self.segment = segment
        self.segment_name = segment_name
        self.seed = seed

    def get_description(self):
        return f"Generate Splits for {self.segment_name} (Group {self.seed+1}/{GENERATE_SPLIT_STEP})"
    def get_color(self):
        return "\033[1;33m"
    def get_dependencies(self):
        return [(TaskType.GenerateTime, self.segment)]

    def _name(self) -> str:
        return f"{self.segment_name}.split{self.seed}"
    def _hash_files(self) -> list[str]:
        return [
            paths.seg_time_toml(self.segment_name),
            paths.seg_split_frame(self.segment_name, self.seed),
        ]

    def prepare(self):
        os.makedirs(paths.seg_splits_dir(self.segment_name), exist_ok=True)
    def _exe_args(self):
        return [
            "python3", "scripts/build_overlay.py",
            self.segment_name,
            str(self.seed),
            str(GENERATE_SPLIT_STEP)
        ]
