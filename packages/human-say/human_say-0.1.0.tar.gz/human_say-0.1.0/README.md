markdown
# Hello World PyPI

`human-say` is a simple Python package that provides functions to greet and bid farewell to users. It includes a `human_say` package with two modules: `say_hello` and `say_goodbye`, which print personalized greeting and farewell messages.

## Installation

You can install `human-say` using pip. Once published to PyPI, use the command below. For local development, install from the source.

### From PyPI 
```bash
pip install human-say
```

### From Source 
- Clone the repository:
```bash
git clone https://github.com/abbasi0abolfazl/hello_world_pypi.git
cd human-say
```
- Install using pip:
```bash
pip install .
```

### Usage
The package provides two functions in the human_say package:
- say_hello(name): Prints a greeting message.
- say_goodbye(name): Prints a farewell message.

Example:
```python
from human_say.say_hello import say_hello
from human_say.say_goodbye import say_goodbye

def main():
    print(say_hello("john doe"))  # Output: Hi john doe What's new?
    print(say_goodbye("john doe"))  # Output: Goodbye john doe See you later.

if __name__ == "__main__":
    main()
```

### Project Structure
```
human-say/
├── human_say/
│   ├── __init__.py
│   ├── say_hello.py
│   ├── say_goodbye.py
├── main.py
├── pyproject.toml
├── README.md
├── LICENSE
└── uv.lock
```

### Contact
- Author: Abolfazl Abbasi
- Email: a.abbasi5775@gmail.com
- GitHub: abbasi0abolfazl
