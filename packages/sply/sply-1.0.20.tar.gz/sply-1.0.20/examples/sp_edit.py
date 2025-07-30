#!/usr/bin/env python3

import sys
import sply


def main ():
    backend = ""
    model_id = ""
    for sys_arg in sys.argv[1:]:
        if sys_arg.find("backend=") == 0:
            backend = sys_arg[8:]
        if sys_arg.find("model_id=") == 0:
            model_id = sys_arg[9:]

    sp = sply.sp(
        show=True,
        backend=backend,
        model_id=model_id,
        num_ctx=1_000,
        )

    sp.runcode("y = 1")
    s = sp.runcode("y + 1")
    print(f"**{s}**")

    sp.edit_prompt()
    return 0


if __name__ == "__main__":
    exit(main())


