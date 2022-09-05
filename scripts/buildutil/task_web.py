from buildutil.task import ITaskDefinition, TaskType
from buildutil import paths

class TaskDefGenerateWebPage(ITaskDefinition):
    def __init__(self, last_seg_name) -> None:
        super().__init__()
        self.last_segment_name = last_seg_name

    def get_description(self):
        return f"Writing index.html"
    def get_dependencies(self):
        return [(TaskType.GenerateTimeTable, 0)]
    def _name(self) -> str:
        return "webpage"
    def _hash_files(self) -> list[str]:
        return [
            paths.index_html(),
            paths.timetable_html()
        ]

    def _exe_args(self):
        return [
            "python3", "scripts/build_web.py", self.last_segment_name
        ]
