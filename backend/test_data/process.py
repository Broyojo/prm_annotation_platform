import json
import os

import nltk

for file in os.listdir("./old"):
    data = []

    if file.endswith(".json"):
        with open(os.path.join("./old", file), "r") as f:
            data = json.load(f)
    elif file.endswith(".jsonl"):
        with open(os.path.join("./old", file), "r") as f:
            data = []
            for line in f:
                data.append(json.loads(line))
    else:
        continue

    new_data = []
    for d in data:
        if isinstance(d, str):
            d = json.loads(json.loads(d))  # fix FRoG dataset
        steps = nltk.sent_tokenize(d["model_answer"])
        new_data.append(
            {
                "question": d["question"],
                "answer": d["answer"],
                "llm_answer": d["model_answer"],
                "steps": steps,
                "num_steps": len(steps),
                "is_correct": d.get("is_correct"),
                "solve_ratio": d.get("solve_ratio"),
                "llm_name": d.get("model_name"),
                "prompt_format": d.get("prompt_format"),
                "final_answer": d.get("final_answer"),
            }
        )

    with open(os.path.join("normalized", file.split(".")[0] + ".json"), "w") as f:
        json.dump(new_data, f)
