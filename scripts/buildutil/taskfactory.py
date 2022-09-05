from buildutil.task import TaskType, Task
from buildutil.task_download import TaskDefDownload
from buildutil.task_time import TaskDefTime
from buildutil.task_splits import TaskDefGenerateSplits
from buildutil.task_splits_inout import TaskDefGenerateSplitsInout
from buildutil.task_encode import TaskDefEncodeOverlay
from buildutil.task_timetable import TaskDefGenerateTimeTable
from buildutil.task_web import TaskDefGenerateWebPage
from buildutil.task_normalize import TaskDefNormalize
from buildutil.task_testmerge import TaskDefTestMerge
from buildutil.task_merge import TaskDefMerge

class TaskFactory:
    def __init__(self, segment_names):
        self.segment_names = segment_names
    def create(self, type: TaskType, segment: int) -> Task:
        segment_name = self.segment_names[segment]
        if type == TaskType.Download:
            return Task(TaskDefDownload(segment_name))
        if type == TaskType.DownloadTrailer:
            return Task(TaskDefDownload("_trailer"))
        if type == TaskType.DownloadIntro:
            return Task(TaskDefDownload("_intro"))
        if type == TaskType.DownloadTransition:
            return Task(TaskDefDownload("_outro_transition"))
        if type == TaskType.DownloadOutro:
            return Task(TaskDefDownload("_outro"))
        if type == TaskType.DownloadCredits:
            return Task(TaskDefDownload("_credits"))
        if type == TaskType.GenerateTime:
            if segment < 3:
                start = 0
            elif segment == len(self.segment_names)-1:
                start = segment - 5
            elif segment == len(self.segment_names)-2:
                start = segment - 4
            else:
                start = segment - 3
            context = self.segment_names[start:start+6]
            return Task(TaskDefTime(segment, segment_name, context))
        if type == TaskType.GenerateSplit_0:
            return Task(TaskDefGenerateSplits(segment, segment_name, 0))
        if type == TaskType.GenerateSplit_1:
            return Task(TaskDefGenerateSplits(segment, segment_name, 1))
        if type == TaskType.GenerateSplit_2:
            return Task(TaskDefGenerateSplits(segment, segment_name, 2))
        if type == TaskType.GenerateSplit_3:
            return Task(TaskDefGenerateSplits(segment, segment_name, 3))
        if type == TaskType.GenerateSplit_4:
            return Task(TaskDefGenerateSplits(segment, segment_name, 4))
        if type == TaskType.GenerateSplit_5:
            return Task(TaskDefGenerateSplits(segment, segment_name, 5))
        if type == TaskType.GenerateSplit_6:
            return Task(TaskDefGenerateSplits(segment, segment_name, 6))
        if type == TaskType.GenerateSplit_7:
            return Task(TaskDefGenerateSplits(segment, segment_name, 7))
        if type == TaskType.GenerateIntro:
            return Task(TaskDefGenerateSplitsInout("_intro", self.segment_names[0], 0))
        if type == TaskType.GenerateOutro:
            return Task(TaskDefGenerateSplitsInout("_outro", self.segment_names[-1], len(self.segment_names)-1))        
        if type == TaskType.EncodeOverlay:
            return Task(TaskDefEncodeOverlay(segment, segment_name))
        if type == TaskType.EncodeTrailer:
            return Task(TaskDefEncodeOverlay(None, "_trailer"))
        if type == TaskType.EncodeIntro:
            return Task(TaskDefEncodeOverlay(None, "_intro"))
        if type == TaskType.EncodeTransition:
            return Task(TaskDefEncodeOverlay(None, "_outro_transition"))
        if type == TaskType.EncodeOutro:
            return Task(TaskDefEncodeOverlay(None, "_outro"))
        if type == TaskType.EncodeCredits:
            return Task(TaskDefEncodeOverlay(None, "_credits"))
        if type == TaskType.GenerateTimeTable:
            return Task(TaskDefGenerateTimeTable(self.segment_names))
        if type == TaskType.GenerateWebPage:
            return Task(TaskDefGenerateWebPage(self.segment_names[-1]))
        if type == TaskType.Normalize:
            return Task(TaskDefNormalize(segment, segment_name))
        if type == TaskType.NormalizeTrailer:
            return Task(TaskDefNormalize(None, "_trailer"))
        if type == TaskType.NormalizeIntro:
            return Task(TaskDefNormalize(None, "_intro"))
        if type == TaskType.NormalizeTransition:
            return Task(TaskDefNormalize(None, "_outro_transition"))
        if type == TaskType.NormalizeOutro:
            return Task(TaskDefNormalize(None, "_outro"))
        if type == TaskType.NormalizeCredits:
            return Task(TaskDefNormalize(None, "_credits"))
        if type == TaskType.TestMerge:
            return Task(TaskDefTestMerge(
                segment, 
                segment_name, 
                len(self.segment_names),
                self.segment_names[segment-1] if segment > 0 else None,
                self.segment_names[segment+1] if segment < len(self.segment_names)-1 else None))
        if type == TaskType.MergeVideo:
            return Task(TaskDefMerge(self.segment_names))
