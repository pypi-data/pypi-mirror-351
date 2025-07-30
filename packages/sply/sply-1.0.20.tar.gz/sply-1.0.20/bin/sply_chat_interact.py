#!/usr/bin/env python3

import sys
import sply


def print_cmds ():
    print("commands:\n"
          "  [input]: input [input]\\n and return to generation\n"
          "  [input]\\: input [input]\\n and stay in input mode\n"
          "  //[input]: input /[input]\n"
          "  /a: list adjustable params and current values\n"
          "  /a [param]: display param's value\n"
          "  /a [param]=[value]: adjust param to value\n"
          "  /c: clear current input\n"
          "  /e: edit prompt and continue chat\n"
          "  /h: this help\n"
          "  /i: display [[current input]]\n"
          "  /p: display [[prompt]]\n"
          "  /q: quit\n"
          )


def print_usage ():
    print(f"Usage: {sys.argv[0]} [options]\n"
          f"  where [options] are zero or more of:"
          )
    sply.chat.print_default_args("    ")


def main ():
    chat_args = sply.chat.get_default_args()

    for sys_arg in sys.argv[1:]:
        if sys_arg.find("--help") == 0:
            print_usage()
            exit(-1)
        for param_d in sply.chat.param_desc:
            if sys_arg.find(param_d["name"] + "=") == 0:
                sys_arg_param, sys_arg_value = sys_arg.split("=")
                param_type = param_d["type"]
                if param_type == str:
                    chat_args[sys_arg_param] = sys_arg_value
                elif param_type == bool:
                    chat_args[sys_arg_param] = True if sys_arg_value == "True" else False
                elif param_type == int:
                    chat_args[sys_arg_param] = int(sys_arg_value)
                elif param_type == float:
                    chat_args[sys_arg_param] = float(sys_arg_value)
                break

    print("chat_args = ", end="")
    print(chat_args)

    c = sply.chat(**chat_args)

    print("")
    print(c.prompt, end="", flush=True)

    running_ = True
    while running_:
        c.read(show=True)

        add = ""
        while True:
            inp = input("> ")
            if not inp:
                add += "\n"
                break

            elif inp[0] == "/":
                if inp == "/h":
                    print_cmds()
                    continue
                elif inp == "/p":
                    print(f"[[{c.prompt}]]")
                    continue
                elif inp == "/i":
                    print(f"[[{add}]]")
                    continue
                elif inp == "/c":
                    add = ""
                    continue
                elif inp == "/a":
                    c.adjust("list")
                    continue
                elif inp[0:3] == "/a ":
                    c.adjust(inp[3:])
                    continue
                elif inp == "//":
                    inp = "/\n"
                    break
                elif inp == "/e":
                    c.edit_prompt()
                    add = ""
                    break
                elif inp == "/q":
                    running_ = False
                    break
                elif inp[0:2] == "//":
                    inp = inp[1:]
                    pass
                else:
                    print(f"unknown command \"{inp}\": try \"/h\"")
                    continue

            inp_tail = len(inp) - 1
            if inp[inp_tail] == "\\":
                add += inp[:inp_tail] + "\n"
            else:
                add += inp + "\n"
                break
            # end while True

        if not running_:
            break

        if add:
            c.write(add)
            if c.in_suffix_enabled:
                print(c.in_suffix, end="", flush=True)
        # end while running_
    return 0


if __name__ == "__main__":
    exit(main())


