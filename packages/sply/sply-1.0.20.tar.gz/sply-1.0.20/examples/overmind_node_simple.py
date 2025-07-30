#!/usr/bin/env python3

import sply.overmind as overmind
n = overmind.node("n", "a primary node connected to the Overmind")
jane = n.node("jane", "a lady named Jane, age 25.")
print(jane["name"])

snacks = n.node("snacks", "some delicious snacks")
print(n("give the 'snacks' to 'jane'"))

print(jane("What's up?"))

