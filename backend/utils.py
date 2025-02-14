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

    # the label heritaged from the merging
    step_merge_label = {}

    origin_step_indexes = []

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
                steps_existed = step_merge_map.get(len(model_answer_steps_valid), [])
                step_merge_map[len(model_answer_steps_valid)] = steps_existed + [curr_pt]

                # The latest base step being merged provide the label
                step_merge_label[len(model_answer_steps_valid)] = curr_pt if not len(steps_existed) else steps_existed[-1]

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
            origin_step_indexes.append(curr_pt - 1)
            continue

        if len(unmerged_step_buffer):
            curr_step = "\n".join([x[1] for x in unmerged_step_buffer]) + "\n" + curr_step
            curr_step = curr_step.lstrip("\n")
            step_merge_map[len(model_answer_steps_valid)] = [x[0] for x in unmerged_step_buffer] + [curr_pt - 1]
            unmerged_step_buffer = []
        else:
            step_merge_map[len(model_answer_steps_valid)] = [curr_pt - 1]

        # use the last label as the label to pass
        step_merge_label[len(model_answer_steps_valid)] = curr_pt - 1

        model_answer_steps_valid.append(curr_step)
        origin_step_indexes.append(curr_pt - 1)

    if len(unmerged_step_buffer):
        step_merge_map[len(model_answer_steps_valid)] = [x[0] for x in unmerged_step_buffer]
        # first label of the left steps
        step_merge_label[len(model_answer_steps_valid)] = step_merge_map[len(model_answer_steps_valid)][0]
        model_answer_steps_valid.append("\n".join([x[1] for x in unmerged_step_buffer]).lstrip("\n"))
        unmerged_step_buffer = []

    return model_answer_steps_valid, step_merge_map, step_merge_label

def report_timestamp():
    # datetime object containing current date and time
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("Date=%d/%m/%Y Time=%H:%M:%S")
    return dt_string + f" Timezone={time.tzname[0]}"