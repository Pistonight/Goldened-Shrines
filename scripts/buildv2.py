import info
from task import TaskType, Task, TaskManager
from proc import ProcessHolder
import os
import shutil
import sys

class BuildConfig:
    def __init__(self, subprocesses: int):
        self.subprocesses = subprocesses

def build_main(task_types: set[TaskType], input_segments: list[str], build_config: BuildConfig):
    # (none or start_time, none or process)
    task_manager = TaskManager(gpu_limit=3)
    processes: list[ProcessHolder] = []
    for _ in range(build_config.subprocesses):
        processes.append(ProcessHolder())
    task_manager.print_status("Loading segment info", processes)
    segment_names = info.load_seg_names()
    task_manager.print_status("Initializing tasks  ", processes)
    task_manager.initialize(segment_names)

    segments = []
    if not input_segments:
        for i in range(len(segment_names)):
            segments.append(i)
    else:
        for input_segment in input_segments:
            seg_id = segment_names.index(input_segment) # exception if not found
            segments.append(seg_id)
    task_manager.print_status("Checking what needs to be done    ", processes)

    for t in task_types:
        if t in (
            TaskType.GenerateMergeVideo, 
            TaskType.GenerateWebPage, 
            TaskType.GenerateTimeTable,
            TaskType.DownloadTrailer,
            TaskType.DownloadIntro,
            TaskType.DownloadOutro,
            TaskType.DownloadCredits,
            TaskType.GenerateIntro,
            TaskType.GenerateOutro,
            TaskType.EncodeIntro,
            TaskType.EncodeOutro
        ):
            task_manager.schedule_task(t, 0)
        else:
            for s in segments:
                task_manager.schedule_task(t, s)
    
    task_manager.print_status("Queueing tasks                             ", processes)
    task_manager.queue_scheduled_tasks()
    task_manager.print_status(None, processes)
    if task_manager.is_queue_empty():
        task_manager.print_report()
        return

    os.makedirs("build/logs", exist_ok=True)
    os.makedirs("build/hash", exist_ok=True)

    task_manager.print_status(None, processes)
    # Manage subprocesses
    while True:
        # try to start a process in all empty slots
        for process_holder in processes:
            if not process_holder.is_active():
                # find a task
                task = task_manager.executable_task()
                if task is not None:
                    task.prepare()
                    process = task.execute()
                    if process is not None:
                        # if proces is none, it means the task was done synchronously
                        process_holder.start(process, task)
                    else:
                        task.mark_complete(True)
                        task_manager.on_finish_task(task)
        # try joining processes
        active_count = 0
        did_print_this_loop = False
        for process_holder in processes:
            if process_holder.is_active():
                process = process_holder.get_process()
                active_count+=1
                process.join(1)
                if process.exitcode is not None:
                    succeeded = process.exitcode == 0
                    task = process_holder.get_task()
                    task.mark_complete(succeeded)
                    task_manager.on_finish_task(task)
                    process_holder.stop()

                else:
                    did_print_this_loop=True
                    task_manager.print_status(None, processes)
        if active_count == 0 and task_manager.is_queue_empty():
            break
        if not did_print_this_loop:
            task_manager.print_status(None, processes)

    # Report
    task_manager.print_report()

def add_tasks_from_name(task_name, tasks: set[TaskType]):
    if task_name == "download":
        tasks.add(TaskType.Download)
        tasks.add(TaskType.DownloadIntro)
        tasks.add(TaskType.DownloadOutro)
        tasks.add(TaskType.DownloadCredits)
        tasks.add(TaskType.DownloadTrailer)
        return True
    if task_name == "time":
        tasks.add(TaskType.GenerateTime)
        return True
    if task_name in ("generate", "split", "splits"):
        tasks.add(TaskType.GenerateSplit_0)
        tasks.add(TaskType.GenerateSplit_1)
        tasks.add(TaskType.GenerateSplit_2)
        tasks.add(TaskType.GenerateSplit_3)
        tasks.add(TaskType.GenerateSplit_4)
        tasks.add(TaskType.GenerateSplit_5)
        tasks.add(TaskType.GenerateSplit_6)
        tasks.add(TaskType.GenerateSplit_7)
        tasks.add(TaskType.GenerateSplit_8)
        tasks.add(TaskType.GenerateSplit_9)
        tasks.add(TaskType.GenerateSplit_a)
        tasks.add(TaskType.GenerateSplit_b)
        tasks.add(TaskType.GenerateSplit_c)
        tasks.add(TaskType.GenerateSplit_d)
        tasks.add(TaskType.GenerateSplit_e)
        tasks.add(TaskType.GenerateIntro),
        tasks.add(TaskType.GenerateOutro)
        return True
    if task_name in ("overlay", "encode"):
        tasks.add(TaskType.EncodeOverlay)
        tasks.add(TaskType.EncodeIntro)
        tasks.add(TaskType.EncodeOutro)
        return True
    if task_name == "intro":
        tasks.add(TaskType.DownloadIntro)
        tasks.add(TaskType.GenerateIntro)
        tasks.add(TaskType.EncodeIntro)
        return True
    if task_name == "outro":
        tasks.add(TaskType.DownloadOutro)
        tasks.add(TaskType.GenerateOutro)
        tasks.add(TaskType.EncodeOutro)
        return True
    if task_name in ("table", "timetable"):
        tasks.add(TaskType.GenerateTimeTable)
        return True
    if task_name in ("website", "webpage", "web"):
        tasks.add(TaskType.GenerateWebPage)
        return True
    if task_name in ("merge", "render"):
        tasks.add(TaskType.GenerateMergeVideo)
        return True
    return False

def clean_output():
    if os.path.exists("build"):
        shutil.rmtree("build")

if __name__ == "__main__":
    tasks: set[TaskType] = set()
    segments: list[str] = []
    clean = False
    for arg in sys.argv[1:]:
        if arg == "clean":
            clean = True
            continue
        if not add_tasks_from_name(arg, tasks):
            segments.append(arg)
    
    if clean:
        clean_output()
    
    config = BuildConfig(subprocesses=15)
    build_main(tasks, segments, config)
