import os
import tempfile
import json
from pz_fileio import File

def test_create_and_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.txt")
        f = File(path)
        assert not f.Exists()
        f.Create()
        assert f.Exists()

def test_write_read_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.txt")
        f = File(path).Create()
        f.Overwrite("First line", "Second line")
        content = f.Read()
        assert "First line" in content
        assert "Second line" in content

def test_append():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.txt")
        f = File(path).Create()
        f.Overwrite("Line1")
        f.Append("Line2", "Line3")
        lines = f.ReadLines()
        assert lines[0].strip() == "Line1"
        assert lines[1].strip() == "Line2"
        assert lines[2].strip() == "Line3"

def test_is_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "empty.txt")
        f = File(path).Create()
        assert f.IsEmpty()
        f.Overwrite("not empty")
        assert not f.IsEmpty()

def test_json_read_write():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "data.json")
        f = File(path).Create()
        data = {"name": "fileio", "version": 1.0}
        f.WriteAsJson(data)
        loaded = f.ReadAsJson()
        assert loaded == data

def test_csv_read_write():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "data.csv")
        f = File(path).Create()
        rows = [["name", "value"], ["fileio", "awesome"]]
        f.WriteAsCsv(rows)
        read_rows = f.ReadAsCsv()
        assert read_rows == rows

def test_get_basename_dirname_absolute():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "subdir", "file.txt")
        f = File(path)
        assert f.GetBasename() == "file.txt"
        assert os.path.basename(f.GetDirname()) == "subdir"
        assert os.path.isabs(f.GetAbsolutePath())

def test_get_mime_type():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "file.txt")
        f = File(path).Create()
        assert f.GetMimeType() == "text/plain"

def test_hash_and_backup():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "file.txt")
        f = File(path).Create()
        f.Overwrite("Some content")
        hash_value = f.Hash()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # sha256 -> 64 hex chars
        backup_path = f.Backup()
        assert os.path.exists(backup_path)

def test_delete_and_recreate():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "file.txt")
        f = File(path).Create().Overwrite("Some text")
        f.Delete()
        assert not f.Exists()
        f.Recreate()
        assert f.Exists()

def test_context_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "file.txt")
        f = File(path).Create()
        with open(path, 'w', encoding='utf-8') as fhandle:
            fhandle.write("Hello context!")
        with File(path) as fobj:
            content = fobj.Read()
        assert "Hello context!" in content
