#!/usr/bin/env python3

import sys
import random
import sply
import time


def main ():
    log_path_default = "sply_double_chat.log"
    log_path = log_path_default

    names = {
        "ai_1": "AI_1",
        "ai_2": "AI_2",
        }

    c1_args = sply.chat.get_default_args()
    c1_args |= {
        "backend": "llama-server",
        "port": 8080,
        "user_name": names["ai_2"],
        "user_desc": "is an LLM",
        "ai_name": names["ai_1"],
        "ai_desc": "is a different LLM",
        "in_suffix": "",
        "in_suffix_enabled": False,
        "rev_prompt": f"{names["ai_2"]}:",
        "seed": -1,
        "temp": 0.6,
        "num_ctx": 16384,
        }

    c2_args = sply.chat.get_default_args()
    c2_args |= {
        "backend": "llama-server",
        "port": 8081,
        "user_name": names["ai_1"],
        "user_desc": c1_args["ai_desc"],
        "ai_name": names["ai_2"],
        "ai_desc": c1_args["user_desc"],
        "in_suffix": "",
        "in_suffix_enabled": False,
        "rev_prompt": f"{names["ai_1"]}:",
        "seed": -1,
        "temp": 0.9,
        "num_ctx": 16384,
        }

    for sys_arg in sys.argv[1:]:
        found_sys_arg = False
        if sys_arg.find("--help") == 0:
            print(f"Usage: {sys.argv[0]} [options]\n"
                  f"  where [options] are zero or more of:\n"
                  f"    log_path=(str): chat log file path (default: \"{log_path_default}\")"
                  )
            sply.chat.print_default_args("    c1_", c1_args)
            sply.chat.print_default_args("    c2_", c2_args)
            exit(-1)
        elif sys_arg.find("log_path=") == 0:
            log_path = sys_arg[10:]
            continue

        for param_d in sply.chat.param_desc:
            for prefix, c_args in (("c1_", c1_args), ("c2_", c2_args)):
                if sys_arg.find(prefix + param_d["name"] + "=") == 0:
                    sys_arg_param, sys_arg_value = sys_arg.split("=")
                    sys_arg_param = sys_arg_param[3:]
                    param_type = param_d["type"]
                    if param_type == str:
                        c_args[sys_arg_param] = sys_arg_value
                    elif param_type == bool:
                        c_args[sys_arg_param] = True if sys_arg_value == "True" else False
                    elif param_type == int:
                        c_args[sys_arg_param] = int(sys_arg_value)
                    elif param_type == float:
                        c_args[sys_arg_param] = float(sys_arg_value)
                    found_sys_arg = True
                    break
                if found_sys_arg:
                    break
            if found_sys_arg:
                break
        if found_sys_arg:
            continue

    if c1_args["seed"] == -1:
        c1_args["seed"] = random.randrange(2**32)

    if c2_args["seed"] == -1:
        c2_args["seed"] = random.randrange(2**32)

    print(f"c1_args={c1_args}")
    print(f"c2_args={c2_args}")

    c1 = sply.chat(**c1_args)
    c2 = sply.chat(**c2_args)

    # modify the default prompt's greeting, which is prefaced with '\n'
    c2.prompt = c2.prompt[: c2.prompt.find("\n")] +\
          c2.make_prompt_greet(c2_args["ai_name"], c2_args["user_name"])
    c2.updated_prompt()

    interactive = False
    interrupted = False
    turn = 1

    running = True
    while running:
        while interactive:
            cmd = input("> ")
            if not cmd:
                break
            elif cmd == "h":
                print("[[ interactive commands ]]")
                print("enter: next iteration")
                print("h: this help")
                print("a1: list c1 adjustable params and current values")
                print("a1 [param]: display c1 param's value")
                print("a1 [param]=[value]: adjust c1 param to value")
                print("a2: list c2 adjustable params and current values")
                print("a2 [param]: display c2 param's value")
                print("a2 [param]=[value]: adjust c2 param to value")
                print("c: exit interactive mode and continue")
                print("e1: edit c1 prompt")
                print("e2: edit c2 prompt")
                print("i: interrupt turn and continue")
                print("p1: display [[c1 prompt]]")
                print("p2: display [[c2 prompt]]")
                print("q: quit running")
                print("t: show turn")
                print("t1: set turn to 1")
                print("t2: set turn to 2")
            elif cmd == "a1":
                c1.adjust("list")
            elif cmd == "a2":
                c2.adjust("list")
            elif cmd[0:3] == "a1 ":
                c1.adjust(cmd[3:])
            elif cmd[0:3] == "a2 ":
                c2.adjust(cmd[3:])
            elif cmd == "c":
                interactive = False
                break
            elif cmd == "e1":
                c1.edit_prompt()
            elif cmd == "e2":
                c2.edit_prompt()
            elif cmd == "i":
                if turn == 1:
                    msg = "\n" + c1_args["rev_prompt"]
                    turn = 2
                else:
                    msg = "\n" + c2_args["rev_prompt"]
                    turn = 1

                with open(log_path, "a") as f:
                    f.write(msg)

                c1.write(msg, show=False)
                c2.write(msg, show=True)

                interactive = False
                break

            elif cmd == "p1":
                print(f"[[{c1.prompt}]]")
            elif cmd == "p2":
                print(f"[[{c2.prompt}]]")
            elif cmd == "q":
                running = False
                break
            elif cmd == "t":
                print(f"turn is {turn}")
            elif cmd == "t1":
                turn = 1
            elif cmd == "t2":
                turn = 2

        if not running:
            break

        if turn == 1:
            while True:
                msg, interrupted = c1.read(show=True)
                if msg:
                    break
                else:
                    print("", end="", flush=True)
                    time.sleep(1)

            with open(log_path, "a") as f:
                f.write(msg)

            c2.write(msg, show=False)

            if interrupted:
                interrupted = False
                interactive = True
                print("\n[[ entering interactive mode: enter h for help ]]")
                continue

            turn = 2

        if turn == 2:
            while True:
                msg, interrupted = c2.read(show=True)
                if msg:
                    break
                else:
                    print("", end="", flush=True)
                    time.sleep(1)

            with open(log_path, "a") as f:
                f.write(msg)

            c1.write(msg, show=False)

            if interrupted:
                interrupted = False
                interactive = True
                continue

            turn = 1


    return 0


if __name__ == "__main__":
    exit(main())

