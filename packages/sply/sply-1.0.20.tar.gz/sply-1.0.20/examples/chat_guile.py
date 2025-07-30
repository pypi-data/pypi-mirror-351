#!/usr/bin/env python3

import sys
import sply

prompt = "; "\
         "You are acting as a guile interpreter. "\
         "Assume the input code contains no mistakes or typos. "\
         "Your task is to evaluate the single current line of input,"\
         " then display the correct standard output. "\
         "Do not generate markdown code blocks or JSON responses. "\
         "Do not think out loud.\n"\
         "\n"\
         "scheme@(guile-user)> (+ 1 1)\n"\
         "$1 = 2\n"\
         "scheme@(guile-user)> (+ 2 1)\n"\
         "$1 = 3\n"\
         "scheme@(guile-user)> "\


def main ():
    backend = ""
    model_id = "default"
    for sys_arg in sys.argv[1:]:
        if sys_arg.find("backend=") == 0:
            backend = sys_arg[8:]
        if sys_arg.find("model_id=") == 0:
            model_id = sys_arg[9:]

    c = sply.chat(
        backend=backend,
        model_id=model_id,
        rev_prompt="\nscheme@(guile-user)> ",
        prompt=prompt,
        in_suffix_enabled=False,
        num_ctx=1_000,
        )

    print(c.prompt, end="", flush=True)
    c.read(show=True)

    c.write("(* 3 2)\n", show=True)
    c.read(show=True)

    print()
    return 0


if __name__ == "__main__":
    exit(main())


