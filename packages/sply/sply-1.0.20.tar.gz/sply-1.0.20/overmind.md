# The Overmind
#### _an experiment in abstract LLM control using the SPLY library_

## Table of Contents

- [Example usage](#example-usage)
- [Environment variables](#environment-variables)

## Example usage
```python
>>> import sply.overmind as overmind
>>> n = overmind.node("n", "a primary node connected to the Overmind")
>>> jane = n.node("jane", "a lady named Jane, age 25.")
>>> jane["name"]
"Jane"
>>> n("infer the meaning of a 'realism' property (i.e. jane[\"realism\"]) and briefly describe it to me")
"Realism in this context refers to the degree to which an entity or concept within the virtual world accurately reflects real-world characteristics or behaviors. For Jane, the realism property would indicate how closely her attributes and actions align with those of a typical 25-year-old woman in reality."
>>> jane["realism"] = "90% human-like"
>>> jane["IQ"] = "120.0"
>>> user = n.node("user", "a reference to myself, a man named John")
>>> jane["master"] = "user"
>>> jane("how are you feeling today?")
"Hello! I'm doing well, thank you for asking. How about yourself?"
>>> sue = n.node("sue", "Sue - a copy of Jane with various personal properties randomly changed by up to 20%")
>>> sue["master"] = "user"
>>> g = n.node("g", "an uninitialized node group")
>>> g["members"] = ["jane", "sue"]
>>> room = n.node("room", "a large and luxurious living room")
>>> user["location"] = "room"
>>> g["location"] = "room"
>>> n("add some items to the living room that Jane and Sue would like")
"OK"
>>> g("how do you like the room?")
```

## Environment variables
  * $overmind_show: if "True", show otherwise hidden generation for debugging
  * $overmind_backend: LLM backend
  * $overmind_model_id: LLM model
  * $overmind_editor: editor path for prompt editing
  * $overmind_seed: psuedo-random number generator seed for the LLM backend
  * $overmind_temp: temperature setting for the LLM backend
  * $overmind_num_ctx: context size for the LLM backend

