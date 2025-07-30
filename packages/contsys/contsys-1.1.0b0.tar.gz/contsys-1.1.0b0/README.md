# contsys

Python library simplifying system script management with handy functions like clearing the console, setting the window title, and detecting the operating system (Windows, Linux, macOS).

By **G-Azon** 🇫🇷

## Features

- CMD:
   - `CMD.clear` clear the console screen.
   - `CMD.title([TITLE])` change the title of the console screen to the specified title.

- system:  
   - `system.iswin32()` return **True** if the current OS is Windows, and return **False** if the current OS is not *Windows*.
   - `system.linux()` return **True** if the current OS is *Linux Based*, and return **False** if the current OS is not *Linux Based*.
   - `system.isdarwin()` return **True** if the current OS is MacOS, and return **False** if the current OS is not *MacOS*.

- monitor:
   - `monitor.cpu_usage()` return the current cpu usage in percents.
   - `monitor.ram_usage()` return the current virtual memory usage in percents.

## Installation

You can install contsys using pip:

```bash
pip install contsys
```

## License

This project is under the MIT License.

## Contact

if you have any trouble or you want to suggest an amelioration you can contact me at [G-Azon782345@protonmail.com](mailto:G-Azon782345@protonmail.com)

## Changelog

### 1.1.0
   - Add `monitor.cpu_usage()` `monitor.ram_usage()`.
   - Add the changelog section.
   - Add a new requiered dependency: *psutil*

### 1.0.2
   - Add a better description.

### 1.0.1
   - Add `system.iswin32()` `system.islinux()` `system.isdarwin()`.

### 1.0.0
   - The first version of **contsys**.
   - Add `CMD.clear()` `CMD.title()`.