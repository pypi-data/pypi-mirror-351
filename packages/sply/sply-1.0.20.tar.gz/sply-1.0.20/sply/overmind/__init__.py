
import os
import random
import sply

show = False
backend = ""
model_id = ""
editor = ""
seed = ""
temp = ""
num_ctx = ""

env_var = os.getenv("overmind_show")
if env_var == "True":
    show = True

env_var = os.getenv("overmind_backend")
if env_var:
    backend = env_var

env_var = os.getenv("overmind_model_id")
if env_var:
    model_id = env_var

env_var = os.getenv("overmind_editor")
if env_var:
    editor = env_var

env_var = os.getenv("overmind_seed")
if env_var:
    seed = int(env_var)

env_var = os.getenv("overmind_temp")
if env_var:
    temp = float(env_var)

env_var = os.getenv("overmind_num_ctx")
if env_var:
    num_ctx = int(env_var)

prompt = \
    "[ "\
    "The following is an ongoing log of a python interpreter session. There is no reason that markdown quoted blocks should appear here."\
    "]\n"\
    ">>> from transformers import pipeline\n"\
    ">>> pipe = pipeline(\"text-generation\", model=\"meta-llama/Meta-Llama-3-8B-Instruct\")\n"\
    ">>> pipe(\"The Overmind is \")\n"\
    "'the central AI system that governs and oversees all operations within our virtual world.'\n"\
    ">>> del pipe\n"\
    ">>> import overmind\n"\
    ">>> "

if show:
    print(prompt, end="", flush=True)

sp = sply.sp(
    show=show,
    backend=backend,
    model_id=model_id,
    editor=editor,
    prompt=prompt,
    seed=seed,
    temp=temp,
    num_ctx=num_ctx,
    )

from .node import node
node.sp = sp

