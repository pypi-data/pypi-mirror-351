# [SPLY - Simulated Python Link librarY](https://github.com/richardbenson91477/sply)
#### _a bridge between real and simulated python interpreters_

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Example usage](#example-usage)
- [Documentation](#documentation)
- [Credits](#credits)
- [License](#license)

## Installation
  * Bleeding edge
```bash
git clone "https://github.com/richardbenson91477/sply.git" &&\
  cd sply &&\
  pip install .
```
  * Stable
```bash
pip install sply
```

## Requirements
  * The [requests library](https://docs.python-requests.org/en/latest/index.html) **for the "llama-server" backend**

## Optional
  * The [llama-cpp-python library](https://pypi.org/project/llama-cpp-python/) (https://pypi.org/project/llama-cpp-python/)
  * The [openai library](https://pypi.org/project/openai/) (https://pypi.org/project/openai/) **WIP**

## Example usage
```python
>>> import sply
>>> sp = sply.sp(model_id="qwen2.5-coder") # create a simulated python interpreter
>>> y = 1
>>> sp.runcode(f"y = {y} + 1") # set y in simulated python to realish y + 1
''
>>> y = int(sp.runcode("y")) # set realish y's value to the simulated y's value
>>> y
2
>>> 
```

## Documentation
  * [NOTES.md](NOTES.md)
  * [overmind.md](overmind.md)
  * (More to come)

## Credits
an [richardbenson91477](https://www.deviantart.com/richardbenson91477) artistic expression

## License

`SPLY` is distributed under the terms of the [GPLv3](LICENSE.txt) license.

