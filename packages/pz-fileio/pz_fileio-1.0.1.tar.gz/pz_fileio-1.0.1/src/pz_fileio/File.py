import os.path
import csv
import json
import hashlib
import mimetypes
import time

class File:
    """
    This class represents a file on the file system.
    """
    def __init__(self, *path):
        """
        Initializes the File object with the specified path.

        Args:
            Path (str): The path to the file.
        """
        self.Path = "" if path[0] == None else os.path.join(*path)

    def __enter__(self):
        """
        Enter method for context management support.
        """
        self._handle = open(self.Path, 'r', encoding='utf-8')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit method for context management support.
        Ensures that the file is properly closed.
        """
        self._handle.close()

    def GetBasename(self):
        """
        Returns the filename without the directory path.

        Returns:
            str: The filename.
        """
        return os.path.basename(self.Path)

    def GetDirname(self):
        """
        Returns the directory path of the file.

        Returns:
            str: The directory path.
        """
        return os.path.dirname(self.Path)

    def GetAbsolutePath(self):
        """
        Returns the absolute path of the file.

        Returns:
            str: The absolute path.
        """
        return os.path.abspath(self.Path)

    def GetFileSize(self):
        """
        Returns the size of the file in bytes.

        Returns:
            int: The size of the file in bytes, or None if the file does not exist.
        """
        if self.Exists():
            return os.path.getsize(self.Path)
        return None

    def GetMimeType(self):
        """
        Returns the MIME type of the file based on its extension.

        Returns:
            str: The MIME type of the file, or None if it cannot be determined.
        """
        mime_type, _ = mimetypes.guess_type(self.Path)
        return mime_type

    def Exists(self):
        """
        Checks if the file exists at the specified path.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.exists(self.Path)
    
    def Create(self):
        """
        Creates the file and its directory structure if they don't exist.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        os.makedirs(self.GetDirname(), exist_ok=True)
        with open(self.Path, 'x', encoding='utf-8'):
            pass
        return self
    
    def Delete(self):
        """
        Deletes the file from the file system.

        Returns:
            bool: True if the file was deleted successfully, False otherwise.
        """
        if self.Exists():
            os.remove(self.Path)
        return self
    
    def Recreate(self):
        """
        Deletes the file if it exists and then creates a new empty file.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        self.Delete()
        self.Create()
        return self
    
    def Read(self):
        """
        Reads the entire content of the file line by line and returns a list of strings.

        Returns:
            list[str]: A list of lines from the file, or None if there's an error.
        """
        if self.Exists():
            with open(self.Path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def ReadLines(self):
        """
        Reads the entire content of the file line by line and returns a list of strings.

        Returns:
            list[str]: A list of lines from the file, or None if there's an error.
        """
        if self.Exists():
            with open(self.Path, 'r', encoding='utf-8') as f:
                return f.readlines()
        return None
    
    def Append(self, *content):
        """
        Appends a line of text to the end of the file with a newline character.

        Args:
            content (str): The line of text to write.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        # Open the file in append mode with UTF-8 encoding
        with open(self.Path, 'a', encoding='utf-8') as f:
            for line in content:
                f.write(line + "\n")  # Add newline character

        return self  # Return self to allow chaining

    def Overwrite(self, *content):
        """
        Overwrites the entire content of the file with the provided content.

        Args:
            content (str): The content to write to the file.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        # Open the file in write mode with UTF-8 encoding
        with open(self.Path, 'w', encoding='utf-8') as f:
            for line in content:
                f.write(line + "\n")

        return self  # Return self to allow chaining

    def ReadAsJson(self):
        """
        Reads the contents of the file as JSON and returns the parsed data.

        Returns:
            object: The parsed JSON data, or None if there's an error.
        """
        if self.Exists():
            with open(self.Path, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return None
        return None
    
    def WriteAsJson(self, content):
        """
        Saves the provided content as JSON to the file.

        Args:
            content (object): The content to serialize and write as JSON.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        with open(self.Path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        return self
    
    def ReadAsCsv(self):
        """
        Reads the contents of the file as CSV and returns a list of rows.

        Returns:
            list[list[str]]: A list of rows from the CSV file, or None if there's an error.
        """
        if self.Exists():
            with open(self.Path, 'r', encoding='utf-8') as f:
                return [row for row in csv.reader(f)]
        return None

    def WriteAsCsv(self, rows):
        """
        Saves the provided rows as CSV to the file.

        Args:
            rows (list[list[str]]): A list of rows to write to the CSV file.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        with open(self.Path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        return self
    
    def IsEmpty(self):
        """
        Checks if the file is empty (has zero size).

        Returns:
            bool: True if the file is empty, False otherwise.
        """
        return not self.Exists() or os.path.getsize(self.Path) == 0
    
    def Hash(self, algorithm = 'sha256'):
        """
        Calculates the hash of the file content using the specified algorithm.

        Args:
            algorithm (str, optional): The hashing algorithm to use. Defaults to 'sha256'.

        Returns:
            str: The hash value of the file content in hexadecimal format, or None if there's an error.
        """
        if not self.Exists():
            return None
        hasher = hashlib.new(algorithm)
        with open(self.Path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def Backup(self):
        """
        Creates a backup of the file with a timestamp appended to the filename.

        Returns:
            str: The path to the backup file.
        """
        if not self.Exists():
            return None
        backup_path = f"{self.Path}.{time.strftime('%Y%m%d%H%M%S')}.bak"
        with open(self.Path, 'r', encoding='utf-8') as src, \
             open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        return backup_path
