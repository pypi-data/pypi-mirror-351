import logging
import math
import os
import io
import sys
import time
import json
from typing import Sequence, Union, Dict
import tqdm
from openai import OpenAI
import copy

# 初始化OpenAI客户端
client = OpenAI()

# 请设置环境变量 DASHSCOPE_API_KEY
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")

class QwenDecodingArguments:
    def __init__(
        self,
        temperature=0.2,
        top_p=1.0,
        max_tokens=2048,
        n=1,
        stop=None,
        stream=False,
        echo=False,
        **kwargs
    ):
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.n = n
        self.stop = stop
        self.stream = stream
        self.echo = echo
        for k, v in kwargs.items():
            setattr(self, k, v)


def qwen_completion(
    prompts: Union[str, Sequence[str], Sequence[Dict[str, str]], Dict[str, str]],
    decoding_args,
    model_name="qwen-turbo",
    sleep_time=2,
    batch_size=1,
    max_instances=sys.maxsize,
    max_batches=sys.maxsize,
    return_text=False,
    enable_thinking=None,  # Qwen3特有参数
    **decoding_kwargs,
) -> Union[str, Sequence[str], Sequence[Sequence[str]]]:
    """
    用阿里通义千问API进行多轮对话completion（仿openai_completion接口风格）。
    """
    is_single_prompt = isinstance(prompts, (str, dict))
    if is_single_prompt:
        prompts = [prompts]

    if max_batches < sys.maxsize:
        logging.warning(
            "`max_batches` will be deprecated in the future, please use `max_instances` instead."
            "Setting `max_instances` to `max_batches * batch_size` for now."
        )
        max_instances = max_batches * batch_size

    prompts = prompts[:max_instances]
    num_prompts = len(prompts)
    prompt_batches = [
        prompts[batch_id * batch_size : (batch_id + 1) * batch_size]
        for batch_id in range(int(math.ceil(num_prompts / batch_size)))
    ]

    client = OpenAI(
        api_key=dashscope_api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completions = []
    for batch_id, prompt_batch in tqdm.tqdm(
        enumerate(prompt_batches),
        desc="prompt_batches",
        total=len(prompt_batches),
    ):
        batch_decoding_args = copy.deepcopy(decoding_args)

        while True:
            try:
                shared_kwargs = dict(
                    model=model_name,
                    temperature=batch_decoding_args.temperature,
                    top_p=batch_decoding_args.top_p,
                    max_tokens=batch_decoding_args.max_tokens,
                    n=batch_decoding_args.n,
                )
                if batch_decoding_args.stop is not None:
                    shared_kwargs["stop"] = batch_decoding_args.stop
                shared_kwargs.update(decoding_kwargs)

                # 处理enable_thinking参数
                if enable_thinking is not None:
                    shared_kwargs["extra_body"] = {"enable_thinking": enable_thinking}

                # 组装messages
                formatted_messages_batch = []
                for prompt in prompt_batch:
                    if isinstance(prompt, str):
                        formatted_messages_batch.append([
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt},
                        ])
                    elif isinstance(prompt, dict):
                        if "role" in prompt and "content" in prompt:
                            formatted_messages_batch.append([prompt])
                        else:
                            raise ValueError("每个dict类型prompt必须包含'role'和'content'")
                    elif isinstance(prompt, list):
                        formatted_messages_batch.append(prompt)
                    else:
                        raise ValueError("prompt格式不正确，必须是str、dict或list[dict]")

                # Qwen不支持批处理，逐条请求
                for messages in formatted_messages_batch:
                    completion = client.chat.completions.create(
                        messages=messages,
                        **shared_kwargs,
                    )
                    # 直接把 choices 都加进去
                    completions.extend(completion.choices)
                break
            except Exception as e:
                logging.warning(f"Qwen API Error: {e}.")
                if "Please reduce your prompt" in str(e):
                    batch_decoding_args.max_tokens = int(batch_decoding_args.max_tokens * 0.8)
                    logging.warning(f"Reducing target length to {batch_decoding_args.max_tokens}, Retrying...")
                else:
                    logging.warning("Hit request rate limit or other error; retrying...")
                    time.sleep(sleep_time)

    # 只返回文本
    if return_text:
        completions = [c.message.content for c in completions]
    if decoding_args.n > 1:
        completions = [completions[i : i + decoding_args.n] for i in range(0, len(completions), decoding_args.n)]
    if is_single_prompt:
        (completions,) = completions
    return completions


def _make_w_io_base(f, mode: str):
    if not isinstance(f, io.IOBase):
        f_dirname = os.path.dirname(f)
        if f_dirname != "":
            os.makedirs(f_dirname, exist_ok=True)
        f = open(f, mode=mode, encoding='utf-8')
    return f


def _make_r_io_base(f, mode: str):
    if not isinstance(f, io.IOBase):
        f = open(f, mode=mode, encoding='utf-8')
    return f


def jdump(obj, f, mode="w", indent=4, default=str):
    """将对象或字符串以json格式写入文件."""
    f = _make_w_io_base(f, mode)
    if isinstance(obj, (dict, list)):
        json.dump(obj, f, indent=indent, default=default, ensure_ascii=False)
    elif isinstance(obj, str):
        f.write(obj)
    else:
        raise ValueError(f"Unexpected type: {type(obj)}")
    f.close()


def jload(f, mode="r"):
    """从.json文件加载为字典."""
    f = _make_r_io_base(f, mode)
    jdict = json.load(f)
    f.close()
    return jdict