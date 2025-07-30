"""
run:
python -m generate_instruction generate_instruction_following_data
    --prompt_file_path
    --output_dir
    --seed_tasks_path

    --num_prompt_instructions 用于提示的指令数量
    --num_total_instructions 总问题数量(=已有问题数量+需要生成问题数量)
    --model_name="qwen_turbo"(最便宜)

    --request_batch_size 1
    --temperature 1.0
    --top_p 1.0
"""
import time
import json
import os
import random
import re
import tqdm
import pkg_genins.utils as utils


import fire
# import string
# from functools import partial

def encode_prompt(prompt_file_path,prompt_instructions):
    """Encode multiple prompt instructions into a single string."""
    prompt = open(prompt_file_path, encoding="utf-8").read() + "\n"

    for idx, task_dict in enumerate(prompt_instructions):
        (instruction, input, output) = task_dict["instruction"], task_dict["input"], task_dict["output"]
        instruction = re.sub(r"\s+", " ", instruction).strip().rstrip(":")
        input = "<noinput>" if input.lower() == "" else input
        prompt += f"###\n"
        prompt += f"{idx + 1}. Instruction: {instruction}\n"
        prompt += f"{idx + 1}. Input:\n{input}\n"
        prompt += f"{idx + 1}. Output:\n{output}\n"
    prompt += f"###\n"
    prompt += f"{idx + 2}. Instruction:"
    return prompt


def post_process_llm_response(num_prompt_instructions, response):
    if response is None:
        return []
    # 提取指令、输入和输出
    pattern = r"(\d+).\sInstruction:(.?)\n\1.\sInput:(.?)\n\1.\sOutput:(.?)(?=\n\d+. Instruction:|\Z)"
    matches = re.findall(pattern, response["text"], re.DOTALL)
    instructions = []
    for match in matches:
        inst = match[1].strip()
        input_ = match[2].strip()
        input_ = "" if input_.strip().lower() == "<noinput>" else input_
        output_ = match[3].strip()
        # 长度过滤
        # 可以在这里加上其它过滤，比如长度、黑名单等
        if len(inst) <= 5 or len(inst) > 150:
            continue
        instructions.append({"instruction": inst, "input": input_, "output": output_})
    return instructions


def find_word_in_string(w, s):
    return re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE).search(s)


def generate_instruction_following_data(
    prompt_file_path=None,
    output_dir=".",
    seed_tasks_path="seed_tasks.jsonl",
    num_total_instructions=3,
    model_name="qwen-turbo",
    num_prompt_instructions=3,
    request_batch_size=1,
    temperature=1.0,
    top_p=1.0,
):
    # 加载人工种子任务
    seed_tasks = [json.loads(l) for l in open(seed_tasks_path, "r", encoding="utf-8")]
    seed_instruction_data = [
        {"instruction": t["instruction"], "input": t["instances"][0]["input"], "output": t["instances"][0]["output"]}
        for t in seed_tasks
    ]
    print(f"Loaded {len(seed_instruction_data)} human-written seed instructions")

    os.makedirs(output_dir, exist_ok=True)
    request_idx = 0

    # 加载机器生成的指令
    machine_instruction_data = []
    regen_path = "regen.json"
    if os.path.exists(regen_path):
        machine_instruction_data = utils.jload(regen_path)
        print(f"Loaded {len(machine_instruction_data)} machine-generated instructions")
    output_path = os.path.join(output_dir, "output.json")

    progress_bar = tqdm.tqdm(total=num_total_instructions)
    if machine_instruction_data:
        progress_bar.update(len(machine_instruction_data))

    while len(machine_instruction_data) < num_total_instructions:
        request_idx += 1

        batch_inputs = []
        for _ in range(request_batch_size):
            prompt_instructions = random.sample(seed_instruction_data, num_prompt_instructions)
            prompt = encode_prompt(prompt_file_path,prompt_instructions)
            batch_inputs.append(prompt)
        decoding_args = utils.QwenDecodingArguments(
            temperature=temperature,
            n=1,
            max_tokens=8192,
            top_p=top_p,
            stop=["\n20", "20.", "20."],
        )
        request_start = time.time()
        results = utils.qwen_completion(
            prompts=batch_inputs,
            model_name=model_name,
            batch_size=request_batch_size,
            decoding_args=decoding_args,
        )
        request_duration = time.time() - request_start

        process_start = time.time()
        instruction_data = []
        for result in results:
            response = {
                "text": result.message.content,
                "finish_reason": getattr(result, "finish_reason", "stop")
            }
            new_instructions = post_process_llm_response(num_prompt_instructions, response)
            instruction_data += new_instructions

        total = len(instruction_data)
        keep = 0
        for instruction_data_entry in instruction_data:
            keep += 1
            machine_instruction_data.append(instruction_data_entry)
            progress_bar.update(1)
        process_duration = time.time() - process_start
        print(f"Request {request_idx} took {request_duration:.2f}s, processing took {process_duration:.2f}s")
        print(f"Generated {total} instructions, kept {keep} instructions")
        utils.jdump(machine_instruction_data, regen_path)
        utils.jdump(machine_instruction_data, output_path)


def main(task, **kwargs):
    globals()[task](**kwargs)


if __name__ == "__main__":
    fire.Fire(main)
