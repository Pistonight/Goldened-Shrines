"""Multi Build Wrapper"""
import time
import wrapper
import sys
from tc import sec_to_strh
import timeseg
import gensplit
import genhtml
import info
from multiprocessing import Process
MAX_SUBPROCESS = 15

# task code
# upper 1 byte = task, lower 2 byte = which segment
# workflow jobs:
TASK_CLEAN =  0x01# clean - remove previous output: overlay images, computed times, websites, output videos, remove downloaded segment
#        dependencies: none
TASK_DOWNLOAD = 0x02# download - download segment
#        dependencies: clean for that segment
TASK_TIME = 0x03# time - generate time info for the segment
#        dependencies: download for current and previous 3 segments
TASK_GENERATE= 0x04# generate - generate overlay files for one segment
#        dependencies: time for current segment
TASK_OVERLAY = 0x05# overlay - overlay the generated splits on top of video (GPU)
#        dependencies: generate for current segment
TASK_TABLE = 0x06# website - generate website, require all timing be finished
#        dependencies: time for all segments
TASK_WEBSITE = 0x07# website - generate website, require all timing be finished
#        dependencies: table
TASK_MERGE = 0x08# merge all the videos to produce the final video
#        dependencies: overlay for all segments

GPU_LIMIT = 3

def get_description(task, segment_name):
    if task == TASK_CLEAN:
        return f"Cleaning output for: {segment_name}                      "
    if task == TASK_DOWNLOAD:
        return f"Downloading video for: {segment_name}                    "
    if task == TASK_TIME:
        return f"Timing segment: {segment_name}                           "
    if task == TASK_GENERATE:
        return f"Generating split overlay for: {segment_name}                 "
    if task == TASK_OVERLAY:
        return f"Overlaying split on video for: {segment_name}                "
    if task == TASK_TABLE:
        return f"Generating timing table                                               "
    if task == TASK_WEBSITE:
        return f"Building website                                                      "
    if task == TASK_MERGE:
        return f"Merging all segments                                                  "
    return     f"Idle                                                                  "

TASKS = 10
S_OK = 0 # a task is done and succeeded
E_PENDING = 1 # a task is scheduled or running 
E_EMPTY = 2 # a task is not scheduled
E_FAIL = 3 # a task failed
def add_task_dependencies(task, seg, queue, status_matrix, should_clean, should_download):
    """Add direct dependencies of the task, the status of the task should be pending"""
    if status_matrix[task][seg] != E_PENDING:
        print("Fatal: adding task dependencies but the task is not pending")
        return
    if task == TASK_DOWNLOAD:
        add_task(TASK_CLEAN, seg, queue, status_matrix, should_clean, should_download)
    elif task == TASK_TIME:
        add_task(TASK_DOWNLOAD, seg, queue, status_matrix, should_clean, should_download)
        if seg > 0:
            add_task(TASK_TIME, seg-1, queue, status_matrix, should_clean, should_download)
    elif task == TASK_GENERATE:
        add_task(TASK_TIME, seg, queue, status_matrix, should_clean, should_download)
    elif task == TASK_OVERLAY:
        add_task(TASK_GENERATE, seg, queue, status_matrix, should_clean, should_download)
    elif task == TASK_TABLE:
        for s in range(0, len(status_matrix[TASK_TIME])):
            add_task(TASK_TIME, s, queue, status_matrix, should_clean, should_download)
    elif task == TASK_WEBSITE:
        add_task(TASK_TABLE, 0, queue, status_matrix, should_clean, should_download)
    elif task == TASK_MERGE:
        for s in range(0, len(status_matrix[TASK_OVERLAY])):
            add_task(TASK_OVERLAY, s, queue, status_matrix, should_clean, should_download)

def can_execute_task(task, seg, status_matrix):
    if status_matrix[task][seg] != E_PENDING:
        print("Fatal: querying task dependency status but the task is not pending")
        return
    if task == TASK_DOWNLOAD:
        return status_matrix[TASK_CLEAN][seg]
    if task == TASK_TIME:
        dep_status = status_matrix[TASK_DOWNLOAD][seg]
        if dep_status != S_OK:
            return dep_status
        if seg > 0:
            return status_matrix[TASK_TIME][seg-1]
        return S_OK
    if task == TASK_GENERATE:
        return status_matrix[TASK_TIME][seg]
    if task == TASK_OVERLAY:
        return status_matrix[TASK_GENERATE][seg]
    if task == TASK_TABLE:
        for s in range(0, len(status_matrix[TASK_TIME])):
            dep_status = status_matrix[TASK_TIME][s]
            if dep_status != S_OK:
                return dep_status
        return S_OK
    if task == TASK_WEBSITE:
        return status_matrix[TASK_TABLE][0]
    if task == TASK_MERGE:
        for s in range(0, len(status_matrix[TASK_OVERLAY])):
            dep_status = status_matrix[TASK_OVERLAY][s]
            if dep_status != S_OK:
                return dep_status
        return S_OK
    return S_OK

def add_task(task, seg, queue, status_matrix, should_clean, should_download):
    # print(f"calling {task} {seg}")
    if task in (TASK_TABLE, TASK_WEBSITE, TASK_MERGE):
        seg = 0
    if status_matrix[task][seg] != E_EMPTY:
        # already added
        # print("Ignore already added")
        return
    if task == TASK_CLEAN and not should_clean:
        status_matrix[task][seg]=S_OK
        return
    if task == TASK_DOWNLOAD and not should_download:
        status_matrix[task][seg]=S_OK
        return
    queue.append((task, seg))
    status_matrix[task][seg]=E_PENDING
    # print(f"adding {task} {seg}")
    add_task_dependencies(task, seg, queue, status_matrix, should_clean, should_download)


def process_main(task, seg, context):
    if task == TASK_CLEAN:
        wrapper.execute_clean_segment(seg)
        return
    if task == TASK_DOWNLOAD:
        wrapper.execute_download_segment(seg)
        return
    if task == TASK_TIME:
        timeseg.compute_time(seg, context)
        return
    if task == TASK_GENERATE:
        gensplit.generate_overlay(seg)
        return
    if task == TASK_OVERLAY:
        wrapper.execute_overlay_splits(seg)
        return
    if task == TASK_MERGE:
        wrapper.execute_merge()
        return
    if task == TASK_TABLE:
        genhtml.generate_table()
        return
    
    time.sleep(1)

def elapsed_time(start_time):
    return sec_to_strh(round(time.time()-start_time))

last_line = None
def print_status(self_task, start_time, total, completed, processes, seg_names):
    
    global last_line
    if last_line is not None:
        print(f"\033[{last_line}A")
    line = 2
    progress = f"[{completed}/{total}]" if total >= 0 else ""
    print(f"[{elapsed_time(start_time)}]{progress} {self_task}")
    for task, seg, is_active, start_time, _ in processes:
        if is_active:
            print(f"  [{elapsed_time(start_time)}] {get_description(task, seg_names[seg])}")
            line+=1
    extra = 1
    if last_line is not None and line < last_line:
        for _ in range(last_line - line):
            print(f"                                                                                             ")
            extra += 1
    print(f"\033[{extra}A")
    last_line = line
    
BUILD_STATUS_TEXT = "Executing build sub-processes                                     "

def is_gpu(task):
    return task == TASK_OVERLAY

def manager_main(tasks, only_segment, should_clean, should_download, after):
    start_time = time.time()
    end_result = E_PENDING
    # (task, seg, is_active, start_time, object )
    processes = []
    num_subprocess = MAX_SUBPROCESS if only_segment is None else 1
    for _ in range(num_subprocess):
        processes.append((-1, -1, False, 0, None))

    print_status("Loading segment names", start_time, -1, -1, processes, [])
    seg_names = info.load_seg_names()
    # mat[task][seg] = status
    status_matrix = []
    for _ in range(TASKS):
        status_matrix.append([E_EMPTY]*len(seg_names))
    if after is not None:
        for s in range(len(seg_names)):
            status_matrix[after][s] = S_OK
    # (task, segment_index)
    task_queue = []
    print_status("Initializing tasks        ", start_time, -1, -1, processes, seg_names)
    # add initial tasks
    if only_segment is not None:
        seg_id = seg_names.index(only_segment) # exception if not found
        for t in tasks:
            add_task(t, seg_id, task_queue, status_matrix, should_clean, should_download)
    else:
        for t in tasks:
            for s in range(len(seg_names)):
                add_task(t, s, task_queue, status_matrix, should_clean, should_download)

    total_tasks = len(task_queue)
    completed = 0

    # print(task_queue)
    # sys.exit(1)

    print_status(BUILD_STATUS_TEXT, start_time, total_tasks, completed, processes, seg_names)
    # number of current gpu tasks
    gpu_usage = 0
    # Manage subprocesses
    while True:
        #print(task_queue)
        # try to start a process in all empty slots
        for i in range(len(processes)):
            #print(task_queue)
            _, _, is_active, _, _ = processes[i]
            if not is_active:
                # find a task
                polled = []
                found_task = None
                #print(f"try finding job for process {i}")
                while len(task_queue) > 0:
                    current_task, current_seg = task_queue.pop()
                    if is_gpu(current_task) and gpu_usage >= GPU_LIMIT:
                        polled.append((current_task, current_seg))
                        continue

                    can_execute_status = can_execute_task(current_task, current_seg, status_matrix)
                    if can_execute_status == S_OK:
                        found_task = (current_task, current_seg)
                        break
                    elif can_execute_status == E_PENDING:
                        polled.append((current_task, current_seg))
                    elif can_execute_status == E_FAIL:
                        status_matrix[current_task][current_seg] = E_FAIL
                        end_result = E_FAIL
                task_queue.extend(polled)

                if found_task is not None:
                    found_task_id, found_seg_id = found_task
                    if is_gpu(found_task_id):
                        gpu_usage+=1
                    process = Process(target=process_main, args=(found_task_id, seg_names[found_seg_id], get_context_seg_names(found_seg_id, seg_names)), daemon=True)
                    sub_start_time = time.time()
                    processes[i] = (found_task_id, found_seg_id, True, sub_start_time, process)
                    
                    process.start()
        # try joining processes
        active_count = 0
        did_print_this_loop = False
        for i in range(len(processes)):
            task, seg, is_active, _, process = processes[i]
            if is_active:
                active_count+=1
                process.join(1)
                if process.exitcode is not None:
                    status = S_OK if process.exitcode == 0 else E_FAIL
                    status_matrix[task][seg] = status
                    if status == E_FAIL:
                        end_result = E_FAIL
                    completed+=1
                    processes[i] = (-1, -1, False, 0, None)
                    if is_gpu(task):
                        gpu_usage-=1
                else:
                    did_print_this_loop=True
                    print_status(BUILD_STATUS_TEXT, start_time, total_tasks, completed, processes, seg_names)
        if active_count == 0 and len(task_queue) == 0:
            if end_result == E_PENDING:
                end_result = S_OK
            break
        if not did_print_this_loop:
            print_status(BUILD_STATUS_TEXT, start_time, total_tasks, completed, processes, seg_names)

    print_status("Reporting build result                                 ", start_time, total_tasks, completed, processes, seg_names)
    
    print()
    if end_result == S_OK:
        print("BUILD SUCCEEDED")
    else:
        for task, result_list in enumerate(status_matrix):
            for seg, result in enumerate(result_list):
                if result == E_FAIL:
                    print(f"[FAIL] {get_description(task, seg_names[seg])}")
        print("BUILD FAILED")


if __name__ == "__main__":
    should_clean = False
    should_download = False
    only_segment = None
    after = None

    start = 1
    if len(sys.argv) > 3 and sys.argv[1] == "after":
        after = str_to_task(sys.argv[2])
        start = 3
        if after is None:
            print("Invalid task for \"after\"")
            sys.exit(1)

    tasks = []
    for arg in sys.argv[start:]:
        task = str_to_task(arg)
        if task is None:
            only_segment = arg
            break
        if task == TASK_CLEAN:
            should_clean = True
        elif task == TASK_DOWNLOAD:
            should_download = True
        tasks.append(task)

    if len(tasks) == 0:
        print("Fatal: no task given. mbuild [clean] [download] task [segment]")
        sys.exit(1)
    
    if should_clean:
        should_download = True

   # print(only_segment)

    manager_main(tasks, only_segment, should_clean, should_download, after)

