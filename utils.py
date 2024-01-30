

import sys
import json

from typing import Any, List, Literal, Optional, Tuple, TypedDict
sys.path.insert(0, 'codellama')

from codellama.llama.tokenizer import Tokenizer

TOKENIZER = Tokenizer('tokenizer/tokenizer.model')

Role = Literal["system", "user", "assistant"]
class Message(TypedDict):
    role: Role
    content: str
    destination: str  # required for model responses

Dialog = List[Message]


B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"


SPECIAL_TAGS = [B_INST, E_INST, "<<SYS>>", "<</SYS>>", "<step>"]
UNSAFE_ERROR = "Error: special tags are not allowed as part of the prompt."


def dialog_prompt_tokens(tokenizer, dialog):
    """
    Prompt formatting for multi-turn dialogs.
    The dialog is expected to start with a system message and then alternate
    between user and assistant messages.
    """
    assert tokenizer.step_id is not None
    assert all([msg["role"] == "user" for msg in dialog[1::2]]) and all(
        [msg["role"] == "assistant" for msg in dialog[2::2]]
    ), "Model only supports 'system', 'user' and 'assistant' roles, starting with 'system', then 'user' and alternating (u/a/u/a/u...)"
    assert dialog[-1]["role"] == "user", f"Last message must be from user, got {dialog[-1]['role']}"

    dialog_tokens = [tokenizer.bos_id]
    headers = []
    for message in dialog:
        headers.clear()
        headers.append(f"Source: {message['role'].strip()}")
        if message.get("destination") is not None:
            headers.append(f"Destination: {message['destination'].strip()}")
        header = " " + "\n".join(headers)
        dialog_tokens += tokenizer.encode(header, bos=False, eos=False)

        if message["content"]:
            body = "\n\n " + message["content"].strip()
            dialog_tokens += tokenizer.encode(body, bos=False, eos=False)

        dialog_tokens += [tokenizer.step_id]

    # Start of reply
    headers.clear()
    headers.append("Source: assistant")
    headers.append("Destination: user")
    header = " " + "\n".join(headers)
    dialog_tokens += tokenizer.encode(header, bos=False, eos=False)
    dialog_tokens += tokenizer.encode("\n\n ", bos=False, eos=False)

    return dialog_tokens

def chat_completion_turns(tokenizer, dialogs, max_seq_len):
    """
    Process dialogs for chat completion using tokenizer and specified max sequence length.
    """
    if tokenizer.step_id is None:
        raise RuntimeError("Model not suitable for chat_completion_turns()")

    prompt_tokens = []
    unsafe_requests = []  # Assuming a mechanism to handle unsafe requests
    for dialog in dialogs:
        unsafe_requests.append(any(tag in msg["content"] for tag in SPECIAL_TAGS for msg in dialog))

        # Insert system message if not provided
        if dialog[0]["role"] != "system":
            dialog = [{"role": "system", "content": ""}] + dialog

        dialog_tokens = dialog_prompt_tokens(tokenizer, dialog)
        prompt_tokens.append(dialog_tokens)

    # Here you can handle generation_tokens and generation_logprobs as per your requirement

    return prompt_tokens
    
def tokenize(prompt) -> Any:
        
    # if utf-8, decode to string
    if isinstance(prompt, bytes):
        prompt = prompt.decode("utf-8")
    
    prompt = json.loads(prompt)

    if prompt["system_prompt"]:
        instructions = [
            [
                {
                    "role": "system",
                    "content": prompt["system_prompt"],
                },
                {
                    "role": "user",
                    "content": prompt["prompt"],
                }
            ],
        ]
        
    else:
        instructions = [
            [
                {
                    "role": "user",
                    "content": prompt["prompt"],
                }
            ],
        ]

    print(instructions)
    return chat_completion_turns(TOKENIZER, instructions, 2048)[0]


if __name__ == "__main__":

    prompt = "Write a function that computes the set of sums of all contiguous sublists of a given list."
    system_prompt = "Provide answers in JavaScript"
    prompt = json.dumps({"prompt": prompt, "system_prompt": system_prompt})
    tokens = tokenize(prompt)
    print(type(tokens))
    print(tokens)