import time
from datetime import datetime

from config import ending_next_merge_suffixes, starting_prev_merge_prefixes



def model_answer_step_merging(model_answer_steps_orig):
    model_answer_steps = [x for x in model_answer_steps_orig if len(x.strip()) != 0]
    model_answer_steps_void = [x for x in model_answer_steps_orig if len(x.strip()) == 0]

    model_answer_steps_valid = []
    prev_pt, curr_pt = -1, 0
    flag_merge_next_step = False
    flag_merge_prev_step = False
    unmerged_step_buffer = []
    # key is the idx of the new step, value is the list of corresponding idxes of old steps
    step_merge_map = {}

    while curr_pt < len(model_answer_steps):
        if prev_pt >= 0:
            prev_step = model_answer_steps[prev_pt]
        else:
            prev_step = None

        curr_step = model_answer_steps[curr_pt]
        curr_step_lower = curr_step.lower()

        for prev_merge_suffix in starting_prev_merge_prefixes:
            if curr_step_lower.startswith(prev_merge_suffix):
                prev_step_cached = model_answer_steps_valid.pop()
                curr_step_merged = f"{prev_step_cached}\n{curr_step}"
                model_answer_steps_valid.append(curr_step_merged)
                flag_merge_prev_step = True
                break

        for next_merge_suffix in ending_next_merge_suffixes:
            if curr_step_lower.endswith(next_merge_suffix):
                flag_merge_next_step = True
                
                unmerged_step_buffer.append([curr_pt, curr_step])
                break

        if prev_step is None:
            prev_pt = curr_pt
        else:
            prev_pt += 1

        curr_pt += 1
        if flag_merge_prev_step or flag_merge_next_step:
            flag_merge_next_step = False
            flag_merge_prev_step = False
            continue

        if len(unmerged_step_buffer):
            curr_step = "\n".join([x[1] for x in unmerged_step_buffer]) + "\n" + curr_step
            step_merge_map[curr_pt] = [x[0] for x in unmerged_step_buffer] + [curr_pt]
            unmerged_step_buffer = []
        model_answer_steps_valid.append(curr_step)

    return model_answer_steps_valid


def report_timestamp():
    # datetime object containing current date and time
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("Date=%d/%m/%Y Time=%H:%M:%S")
    return dt_string + f" Timezone={time.tzname[0]}"