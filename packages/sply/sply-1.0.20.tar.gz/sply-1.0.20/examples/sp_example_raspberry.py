#!/usr/bin/env python3

from sp_examples import sp_example


def main ():
    ex = sp_example(
        mode="think",
        show=True,
        num_ctx=1_000,
        )

    if ex.res:
        return ex.res

    ex.runcode("name = \"raspberry\"")

    res = ex.runcode("print(name.count(\"r\"))")
    print(f"**{res}**")

    res = ex.runcode("print(name.count(\"r\"))")
    print(f"**{res}**")

    return 0


if __name__ == "__main__":
    exit(main())


