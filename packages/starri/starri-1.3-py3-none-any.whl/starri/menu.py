import re
from blessed import Terminal

def starri(title, choices):
    selected = 0

    def visible_length(text):
        return len(re.sub(r'\x1b\[[0-9;]*m', '', text))

    term = Terminal()
    while True:
        with term.cbreak(), term.hidden_cursor():
            def render():
                print(term.clear)
                height, width = term.height, term.width
                title_lines = title.splitlines()

                for i, line in enumerate(title_lines):
                    visible_width = visible_length(line)
                    x = (width - visible_width) // 2
                    y = i
                    print(term.move_xy(x, y) + line)

                visible_index = 0
                for i, choice in enumerate(choices):
                    if choice.get("type") == "spacer":
                        y = len(title_lines) + 2 + visible_index
                        print(term.move_xy(0, y))
                        visible_index += 1
                        continue

                    label = choice["label"]
                    label_with_cursor = f"> {label}" if i == selected else f"  {label}"
                    x = (width - len(label_with_cursor)) // 2
                    y = len(title_lines) + 2 + visible_index
                    print(term.move_xy(x, y) + (term.reverse(label_with_cursor) if i == selected else label_with_cursor))
                    visible_index += 1

            def move_selection(delta):
                nonlocal selected
                while True:
                    selected = (selected + delta) % len(choices)
                    if choices[selected].get("type") != "spacer":
                        break

            render()
            key = term.inkey()
        # --- End of with block: terminal is back to normal here! ---
        if key.name == "KEY_UP":
            move_selection(-1)
        elif key.name == "KEY_DOWN":
            move_selection(1)
        elif key.name == "KEY_ENTER" or key == "\n":
            if choices[selected].get("type") != "spacer":
                print(term.clear)
                choices[selected]["onselect"]()
                break
        else:
            continue
