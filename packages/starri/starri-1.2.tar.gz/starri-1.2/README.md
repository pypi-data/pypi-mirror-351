# Starri

Starri is a simple Python library for creating terminal-based menus. It supports navigation with the arrow keys and submenus for a dynamic user experience.

## Installation

You can install Starri with pip:

```pip install starri```

## Usage

Here’s how to use Starri:

```python
from starri import *

def main():
    starri(
        title = "Title",
        choices = [
            {"label": "Option 1", "onselect": lambda: print("Option 1 selected")},
            {"type": "spacer"},
            {"label": "Option 2", "onselect": lambda: print("Option 2 selected")},
            {"label": "Exit", "onselect": exit}
        ]
    )
    
if __name__ == "__main__":
    main()
```