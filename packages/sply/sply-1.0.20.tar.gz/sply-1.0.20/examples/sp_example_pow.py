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

    ex.runcode("i = 3 + 2")
    
    res = ex.runcode("print(i ** 3)")
    print(f"**{res}**")

    res = ex.runcode("print(i ** 3)")
    print(f"**{res}**")

    return 0


if __name__ == "__main__":
    exit(main())


