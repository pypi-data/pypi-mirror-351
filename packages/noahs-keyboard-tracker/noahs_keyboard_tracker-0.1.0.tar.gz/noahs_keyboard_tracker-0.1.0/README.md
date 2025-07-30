## Usage: `noahs_keyboard_tracker`

This library provides a simple way to asynchronously monitor for keyboard input.

### Getting Started

First, install the library (after uploading to PyPI):

```bash
pip install noahs_keyboard_tracker
```

```python
from noahs_keyboard_tracker import start_keyboard_tracker, get_key_states, stop_keyboard_tracker

print("press q to stop tracking")
start_keyboard_tracker()
go = True
while go:
    states = get_key_states()
    keys_detected = []
    for key in states.keys():
        keys_detected.append(key)
    if len(keys_detected) > 0:
        print(f"DETECTED: {keys_detected}")
        if "q" in keys_detected:
            go = False
    time.sleep(0.1)
stop_keyboard_tracker()


```



### Check out Source Code

`https://github.com/jonesnoah45010/keyboard_tracker`




