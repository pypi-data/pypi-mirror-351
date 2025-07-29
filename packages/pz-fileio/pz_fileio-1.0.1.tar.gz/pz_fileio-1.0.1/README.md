# fileio

fileio is a lightweight, object-oriented utility library for convenient file management in Python. It provides a robust and intuitive API to perform file operations such as creation, reading, writing, appending, deleting, backup, and hashing, along with JSON and CSV support.

## Installation

fileio is a standalone Python package. To use it, simply download the `File.py` module and place it in your project directory.

Alternatively, if you plan to publish it on PyPI, you could install it via pip:

```bash
pip install fileio
```

*(Assuming the package is published under that name.)*

## Usage

Here’s how to use the `File` class:

### Import the module

```python
from pz_fileio import File
```

### Creating a File instance

```python
f = File("path/to/your/file.txt")
```

### Basic operations

- **Check if file exists**  
  ```python
  exists = f.Exists()
  ```

- **Create a new file**  
  ```python
  f.Create()
  ```

- **Delete a file**  
  ```python
  f.Delete()
  ```

- **Recreate the file (delete and create a new empty one)**  
  ```python
  f.Recreate()
  ```

- **Get basic information**  
  ```python
  print(f.GetBasename())      # filename only
  print(f.GetDirname())       # directory name
  print(f.GetAbsolutePath())  # absolute path
  print(f.GetFileSize())      # file size in bytes
  print(f.GetMimeType())      # file MIME type
  ```

### Reading and writing content

- **Read the entire file content**  
  ```python
  content = f.Read()
  ```

- **Read lines**  
  ```python
  lines = f.ReadLines()
  ```

- **Append content**  
  ```python
  f.Append("This is a new line.")
  ```

- **Overwrite content**  
  ```python
  f.Overwrite("This will replace everything.")
  ```

### JSON and CSV handling

- **Read as JSON**  
  ```python
  data = f.ReadAsJson()
  ```

- **Write as JSON**  
  ```python
  f.WriteAsJson({"name": "fileio", "version": 1.0})
  ```

- **Read as CSV**  
  ```python
  rows = f.ReadAsCsv()
  ```

- **Write as CSV**  
  ```python
  f.WriteAsCsv([["name", "value"], ["fileio", "awesome"]])
  ```

### Hashing and backup

- **Calculate file hash**  
  ```python
  file_hash = f.Hash()  # Defaults to SHA-256
  ```

- **Create a backup**  
  ```python
  backup_path = f.Backup()
  print(f"Backup created at: {backup_path}")
  ```

### Context manager usage

The `File` class implements the context management protocol (`with` statement). Use it for **read-only** scenarios:

```python
with File("path/to/your/file.txt") as f:
    content = f.Read()
```

### License

MIT License

---

Want to tweak this further (like adding examples for CSV, JSON, or advanced usage)? Let me know and I’ll extend it! 🚀
