import asyncio
import threading
import platform
import time

current_key = None
key_states = {}
key_lock = threading.Lock()

OS_NAME = platform.system()

# Shared control variables
stop_event = threading.Event()
tracker_thread = None
listener = None  # Only used for macOS/Windows


# --------------------- Linux Implementation ---------------------
if OS_NAME == "Linux":
    from evdev import InputDevice, categorize, ecodes, list_devices

    def find_keyboard_device():
        for path in list_devices():
            try:
                dev = InputDevice(path)
                capabilities = dev.capabilities()
                if ecodes.EV_KEY in capabilities:
                    return path
            except Exception as e:
                pass
                # print(f"[WARNING] Skipping device {path}: {e}")
        raise RuntimeError("No suitable keyboard input device found.")

    keyboard_device = find_keyboard_device()

    async def monitor_keyboard_linux(device_path=keyboard_device):
        global current_key
        device = InputDevice(device_path)

        async for event in device.async_read_loop():
            if stop_event.is_set():
                break
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                key_name = key_event.keycode
                with key_lock:
                    if key_event.keystate == 1:
                        current_key = key_name
                        key_states[key_name] = True
                    elif key_event.keystate == 0:
                        current_key = None
                        key_states.pop(key_name, None)


    def linux_monitor_runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(monitor_keyboard_linux())


# --------------------- macOS / Windows Implementation ---------------------
elif OS_NAME in ["Darwin", "Windows"]:
    from pynput import keyboard

    def on_press(key):
        global current_key
        with key_lock:
            try:
                key_name = key.char if hasattr(key, 'char') else str(key)
            except Exception:
                key_name = str(key)
            current_key = key_name
            key_states[key_name] = True

    def on_release(key):
        global current_key
        with key_lock:
            try:
                key_name = key.char if hasattr(key, 'char') else str(key)
            except Exception:
                key_name = str(key)
            current_key = None
            key_states.pop(key_name, None)

    def macos_windows_monitor_runner():
        global listener
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        listener.join()  # Keep the thread alive until `listener.stop()` is called


# --------------------- Public API ---------------------

def get_current_key():
    """Returns the currently pressed key or None."""
    with key_lock:
        return current_key

def get_key_states():
    """Returns a copy of the current key state dictionary."""
    with key_lock:
        return dict(key_states)

def start_keyboard_tracker(quiet=False):
    """Starts the keyboard tracker in a background thread."""
    global tracker_thread
    if tracker_thread and tracker_thread.is_alive():
        if not quiet:
            print("[INFO] Keyboard tracker is already running.")
        return

    stop_event.clear()
    if OS_NAME == "Linux":
        tracker_thread = threading.Thread(target=linux_monitor_runner, daemon=True)
    elif OS_NAME in ["Darwin", "Windows"]:
        tracker_thread = threading.Thread(target=macos_windows_monitor_runner, daemon=True)
    else:
        raise NotImplementedError(f"Unsupported OS: {OS_NAME}")
    tracker_thread.start()
    if not quiet:
        print("[INFO] Keyboard tracker started.")

def stop_keyboard_tracker(quiet=False):
    """Stops the keyboard tracker."""
    stop_event.set()
    if OS_NAME in ["Darwin", "Windows"]:
        global listener
        if listener is not None:
            listener.stop()
            listener = None
            if not quiet:
                print("[INFO] Pynput listener stopped.")
    if not quiet:            
        print("[INFO] Keyboard tracker stop signal sent.")





if __name__ == "__main__":
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
















