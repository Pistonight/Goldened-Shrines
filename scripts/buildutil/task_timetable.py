from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths

class TaskDefGenerateTimeTable(ITaskDefinition):
    def __init__(self, segment_names) -> None:
        super().__init__()
        self.total_segments = len(segment_names)
        self.segment_names = segment_names

    def get_description(self):
        return f"Generate Time Table"
    def get_dependencies(self):
        return [(TaskType.GenerateTime, self.total_segments-1)]

    def _name(self) -> str:
        return "timetable"
    def _hash_files(self) -> list[str]:
        files = [paths.timetable_html()]
        for segment_name in self.segment_names:
            files.append(paths.seg_time_toml(segment_name))
        return files

    def _exe_args(self):
        return [
            "python3", "scripts/build_timetable.py",
        ]
