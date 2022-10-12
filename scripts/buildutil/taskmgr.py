from buildutil.task import TaskType, Task
from buildutil.taskfactory import TaskFactory
from buildutil.proc import ProcessHolder

LINE_LENGTH = 80

class TaskManager:
    def __init__(self, gpu_limit):
        self.process_holder = ProcessHolder()
        self.process_holder.start(None, None)
        self.segment_names = None
        self.task_matrix = dict()
        self.task_queue = []
        self.gpu_limit = gpu_limit
        self.gpu_usage = 0
        self.total = 0
        self.completed = 0
        self.skipped = 0
        self.failed = 0
        self.last_up_line = 1

        self.factory = None

    def initialize(self, segment_names):
        self.segment_names = segment_names
        for type in TaskType:
            self.task_matrix[type] = [None] * len(segment_names)

        self.factory = TaskFactory(segment_names)

    def add_task(self, type, segment):
        """Add the task and all its dependencies, return True if the task is added or False if the task is already up-to-date"""
        # is the task already added?
        if self.task_matrix[type][segment] is not None:
            return not self.task_matrix[type][segment].is_completed()
        # Create the task object and put it in the queue temporarily
        task = self.factory.create(type, segment)
        self.task_matrix[type][segment] = task
        up_to_date = True
        # Get its dependencies
        dependencies = task.get_dependencies()
        for (dep_type, dep_segment) in dependencies:
            # Try scheduling dependency
            dep_scheduled = self.add_task(dep_type, dep_segment)
            # If one of the dependencies is not up to date, then this task is not
            if dep_scheduled:
                up_to_date = False

        self.print_status("Adding tasks", [])
        
        # Finally test if self is up to date
        if up_to_date:
            up_to_date = task.is_self_up_to_date()
        
        if up_to_date:
            self.skipped+=1
            task.mark_complete(True)
            return False
        
        return True

    def schedule_tasks(self):
        """Queue up added tasks in an optimized order"""
        self.print_status("Scheduling tasks", [])
        # Tasks are popped from the back, so we insert last tasks first
        for task_type in (
            TaskType.MergeVideo, 
            TaskType.GenerateWebPage, 
            TaskType.GenerateTimeTable,
            TaskType.NormalizeTrailer,
            TaskType.NormalizeIntro,
            TaskType.NormalizeTransition,
            TaskType.NormalizeOutro,
            TaskType.NormalizeCredits,
            TaskType.EncodeCredits,
            TaskType.DownloadCredits,
            TaskType.EncodeTrailer,
            TaskType.DownloadTrailer,
            TaskType.EncodeTransition,
            TaskType.EncodeOutro,
            TaskType.GenerateOutro,
            TaskType.DownloadTransition,
            TaskType.DownloadOutro,
            TaskType.EncodeIntro,
            TaskType.GenerateIntro,
            TaskType.DownloadIntro,
        ):
            for task in self.task_matrix[task_type]:
                if task is not None:
                    self.add_to_queue(task)
                    break
        
        # For segment specific tasks, we want to hit EncodeOverlay as fast as possible
        for segment in range(len(self.segment_names)-1, -1, -1):
            for task_type in (
                TaskType.TestMerge,
                TaskType.Normalize,
                TaskType.EncodeOverlay,
                TaskType.GenerateSplit_0,
                TaskType.GenerateSplit_1,
                TaskType.GenerateSplit_2,
                TaskType.GenerateSplit_3,
                TaskType.GenerateSplit_4,
                TaskType.GenerateSplit_5,
                TaskType.GenerateSplit_6,
                TaskType.GenerateSplit_7,
                TaskType.GenerateTime,
                TaskType.Download,
            ):
                self.add_to_queue(self.task_matrix[task_type][segment])            

    def add_to_queue(self, task: Task):
        if task is None:
            return
        self.total+=1
        self.print_status("Scheduling tasks", [])
        if task.is_completed():
            self.completed+=1
            return
        self.task_queue.append(task)
        
    def executable_task(self) -> Task | None:
        """Get one task that can be executed right now, or None if nothing is found"""
        polled = []
        return_task = None
        while self.task_queue:
            task = self.task_queue.pop()
            # Purge completed tasks in queue
            if task.is_completed():
                continue
            # Determine if task can be executed
            if task.is_gpu() and self.gpu_usage >= self.gpu_limit:
                polled.append(task)
                break

            can_execute = True
            dependencies = task.get_dependencies()
            for (dep_type, dep_segment) in dependencies:
                dep_task = self.task_matrix[dep_type][dep_segment]
                if not dep_task.is_completed():
                    can_execute = False
                    # Not ready yet, add the task back later
                    polled.append(task)
                    break
                if dep_task.is_failed():
                    can_execute = False
                    # Fail this task
                    task.mark_complete(False)
                    self.failed+=1
                    # Don't add failed task back
                    break
            if can_execute:
                return_task = task
                break
        self.task_queue.extend(polled)
        if return_task is not None and return_task.is_gpu():
            self.gpu_usage+=1
        return return_task

    def on_finish_task(self, task: Task):
        if task.is_gpu():
            self.gpu_usage-=1
        self.completed+=1
        if task.is_failed():
            self.failed+=1
        task.update_hash()

    def is_queue_empty(self):
        return not self.task_queue
    
    def print_status(self, step_description, process_holders: list[ProcessHolder]):
        print(f"\033[{self.last_up_line}A")
        line = 2
        if self.total == 0:
            percentage = ""
        else:
            percentage_number = ((self.completed-self.skipped)/(self.total-self.skipped))*100
            percentage = f"{percentage_number:.2f}% "
        progress = f"{percentage}{step_description}: {self.completed}/{self.total} Completed ({self.skipped} Cache Hit). {self.failed} Failed.   "
        
        elapsed = self.process_holder.elapsed_time()
        progress = self.format_status_line(progress,"")
        print(f"[{elapsed}] {progress}")

        for process_holder in process_holders:
            if process_holder.is_active():
                elapsed = process_holder.elapsed_time()
                task = process_holder.get_task()
                description = self.format_status_line(task.get_description(), task.get_color())
                print(f"   [{elapsed}] {description}")
                line+=1
        extra = 1
        if line < self.last_up_line:
            for _ in range(self.last_up_line - line):
                print(self.format_status_line("",""))
                extra += 1
        print(f"\033[{extra}A")
        self.last_up_line = line

    def print_report(self):
        print()
        fails = []
        for task_type in self.task_matrix:
            for task in self.task_matrix[task_type]:
                if task is not None and task.is_failed():
                    fails.append(self.format_status_line(task.get_description(), task.get_color()))
        if not fails:
            print("BUILD SUCCEEDED")
        else:
            for f in fails:
                print(f"Task Failed: {f}")
            print()
            print("BUILD FAILED") 

    def format_status_line(self, line, color_code):
        length = len(line)
        if length > LINE_LENGTH:
            line = line[:LINE_LENGTH-4] + " ..."
        else:
            line = line + " " * (LINE_LENGTH - length)
        return color_code + line + "\033[0m"
