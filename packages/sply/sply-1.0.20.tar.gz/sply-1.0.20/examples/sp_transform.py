#!/usr/bin/env python3

import sys
# import simulated python link library
import sply


def main ():
    backend = ""
    model_id = ""
    for sys_arg in sys.argv[1:]:
        if sys_arg.find("backend=") == 0:
            backend = sys_arg[8:]
        if sys_arg.find("model_id=") == 0:
            model_id = sys_arg[9:]

    # create a simulated python
    sp = sply.sp(
        show=True,
        backend=backend,
        model_id=model_id,
        num_ctx=1_000,
        )

    # set realish y's value to 1
    y = 1
    # print realish y's value
    print(f"y is {y}")

    # set y in simulated python to realish y + 1
    sp.runcode(f"y = {y} + 1")

    # set realish y's value to simulated y's value
    y = int(sp.runcode("y"))

    # print realish y's value
    print(f"y is {y}")

    #s.edit_prompt()
    return 0


if __name__ == "__main__":
    exit(main())


