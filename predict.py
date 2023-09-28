import os
import pathlib
import subprocess
import time

# model.txt is generated by the Makefile
with open("model.txt") as f:
    model = f.read().strip()
model_path = f"/models/{model}"
# model_url = f"https://storage.googleapis.com/replicate-weights/llamacpp/{model}"
if "34b-instruct" in model:
    # use accelerated storage for only the most frequently used
    model_url = f"https://replicate-weights.accel-object.lga1.coreweave.com/llamacpp/{model}"
else:
    model_url = f"https://replicate-weights.object.lga1.coreweave.com/llamacpp/{model}"

# don't download if we're running in docker (i.e. generating schema)
# if (
#     os.getenv("PGET")
#     or not pathlib.Path("/.dockerenv").exists()
#     and pathlib.Path(model_path).exists()
# ):
#     pget_proc: subprocess.Popen | None = subprocess.Popen(
#         ["/usr/bin/pget", model_url, model_path], close_fds=True
#     )
#     print("Downloading model weights...")
# else:
#     pget_proc = None

import inspect
from cog import BasePredictor, ConcatenateIterator, Input
from llama_cpp import Llama

# This prompt formatting was copied from the original CodeLlama repo:
# https://github.com/facebookresearch/llama/blob/6c7fe276574e78057f917549435a2554000a876d/llama/generation.py#L44

# These are components of the prompt that should not be changed by the users
B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
PROMPT_TEMPLATE = f"<s>{B_INST} {{instruction}} {E_INST}"
PROMPT_TEMPLATE_WITH_SYSTEM_PROMPT = (
    f"<s>{B_INST} {B_SYS}{{system_prompt}}{E_SYS}{{instruction}} {E_INST}"
)

DEFAULT_SYSTEM_PROMPT = """"""


def wait_pget(file_name: str) -> bool:
    for i in range(int(300 / 0.05)):
        if pathlib.Path(file_name).exists():
            return True
        print("waiting for download to finish")
        time.sleep(0.05)
    return False


class Predictor(BasePredictor):
    is_instruct = "-instruct" in model

    def setup(self) -> None:
        # need_download = False
        # if pget_proc:
        #     if pget_proc.wait() != 0:
        #         need_download = True
        # else:
        #     wait_time = time.time()
        #     need_download = not wait_pget(model_path)
        #     print(f"Spent {time.time() - wait_time:.3f} waiting for previously launched pget")
        if not os.path.exists(model_path):
            print(f"Downloading model weights from {model_url}....")
            start = time.time()
            # model_url = f"https://weights.replicate.delivery/llamacpp/{model}"
            subprocess.check_call(["pget", "-f", model_url, model_path], close_fds=True)
            print("Downloading weights took: ", time.time() - start)
        self.llm = Llama(
            model_path, n_ctx=4096, n_gpu_layers=-1, main_gpu=0, n_threads=1
        )

    def predict(
        self,
        prompt: str = Input(description="Prompt"),
        system_prompt: str = Input(
            description="System prompt to send to CodeLlama. This is prepended to the prompt and helps guide system behavior.",
            default=DEFAULT_SYSTEM_PROMPT,
        ),
        max_tokens: int = Input(
            description="Max number of tokens to return", default=500
        ),
        temperature: float = Input(description="Temperature", default=0.8),
        top_p: float = Input(description="Top P", default=0.95),
        top_k: int = Input(description="Top K", default=10),
        frequency_penalty: float = Input(
            description="Frequency penalty", ge=0.0, le=2.0, default=0.0
        ),
        presence_penalty: float = Input(
            description="Presence penalty", ge=0.0, le=2.0, default=0.0
        ),
        repeat_penalty: float = Input(
            description="Repetition penalty", ge=0.0, le=2.0, default=1.1
        ),
    ) -> ConcatenateIterator[str]:
        

        # If USE_SYSTEM_PROMPT is True, and the user has supplied some sort of system prompt, we add it to the prompt.
        if self.is_instruct:
            user_prompt = prompt.strip("\n").lstrip(B_INST).rstrip(E_INST).strip()
            prompt_templated = PROMPT_TEMPLATE_WITH_SYSTEM_PROMPT.format(
                    system_prompt=system_prompt, instruction=user_prompt
            )
        
        elif not self.is_instruct:
            prompt_templated = prompt


        print("Prompt:\n" + prompt_templated)

        for tok in self.llm(
            prompt_templated,
            grammar=None,
            max_tokens=max_tokens,
            stream=True,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            repeat_penalty=repeat_penalty,
            mirostat_mode=0,
        ):
            yield tok["choices"][0]["text"]

    _predict = predict

    def base_predict(self, *args, **kwargs) -> ConcatenateIterator:
        kwargs["system_prompt"] = None
        return self._predict(*args, **kwargs)

    # for the purposes of inspect.signature as used by predictor.get_input_type,
    # remove the argument (system_prompt)
    # this removes system_prompt from the Replicate API for non-chat models.

    if not is_instruct:
        wrapper = base_predict
        sig = inspect.signature(_predict)
        params = [p for name, p in sig.parameters.items() if name != "system_prompt"]
        wrapper.__signature__ = sig.replace(parameters=params)
        predict = wrapper
