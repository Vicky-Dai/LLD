from typing import List
from FileSystemEntry import FileSystemEntry
from File import File
from Folder import Folder

class InvalidPathException(Exception):
    pass

class NotFoundException(Exception):
    pass

class AlreadyExistsException(Exception):
    pass

class NotADirectoryException(Exception):
    pass

# 最重要的就是两个helper函数 然后调用其他对象进行一些操作
class FileSystem:
    def __init__(self):
        self._root = Folder("/")

    def create_file(self, path: str, content: str) -> File:
        if path == "/":
            raise InvalidPathException("Cannot create file at root")

        parent = self._resolve_parent(path)
        file_name = self._extract_name(path)

        if parent.has_child(file_name):
            raise AlreadyExistsException(f"Entry already exists: {file_name}")

        file = File(file_name, content)
        parent.add_child(file)
        return file

    def create_folder(self, path: str) -> Folder:
        if path == "/":
            raise AlreadyExistsException("Root already exists")

        parent = self._resolve_parent(path)
        folder_name = self._extract_name(path)

        if parent.has_child(folder_name):
            raise AlreadyExistsException(f"Entry already exists: {folder_name}")

        folder = Folder(folder_name)
        parent.add_child(folder)
        return folder

    def delete(self, path: str) -> None:
        if path == "/":
            raise InvalidPathException("Cannot delete root")

        parent = self._resolve_parent(path)
        name = self._extract_name(path)

        removed = parent.remove_child(name)
        if removed is None:
            raise NotFoundException(f"Entry not found: {path}")

    def list(self, path: str) -> List[FileSystemEntry]:
        entry = self._resolve_path(path)

        if not entry.is_directory():
            raise NotADirectoryException("Cannot list a file")

        return entry.get_children()

    def get(self, path: str) -> FileSystemEntry:
        return self._resolve_path(path)

    def rename(self, path: str, new_name: str) -> None:
        if path == "/":
            raise InvalidPathException("Cannot rename root")

        if not new_name or "/" in new_name: # 非法情况
            raise InvalidPathException("Invalid name")

        parent = self._resolve_parent(path)
        old_name = self._extract_name(path)

        if not parent.has_child(old_name): # 考虑exception
            raise NotFoundException("Entry not found")

        if parent.has_child(new_name): # 这里面exception真多 比较常见的就是没有，或者重复
            raise AlreadyExistsException(f"Entry already exists: {new_name}")

        #  rename 的本质不是只改对象字段，而是要把 parent 这层索引一起更新 ！！！
        # 否则索引没变只是改了名字数据会出错
        entry = parent.remove_child(old_name)
        entry.set_name(new_name)
        parent.add_child(entry)

    def move(self, src_path: str, dest_path: str) -> None:
        if src_path == "/":
            raise InvalidPathException("Cannot move root")

        src_parent = self._resolve_parent(src_path)
        src_name = self._extract_name(src_path)
        entry = src_parent.get_child(src_name)

        if entry is None:
            raise NotFoundException(f"Source not found: {src_path}")

        dest_parent = self._resolve_parent(dest_path)
        dest_name = self._extract_name(dest_path)

        # 很有意思的一段逻辑，防止把一个文件夹移动到它自己里面，不然目录树会变成环，结构就坏了。
        if entry.is_directory():
            current = dest_parent
            while current is not None:
                if current is entry:
                    raise InvalidPathException("Cannot move folder into itself")
                current = current.get_parent()
        #检查重命名
        if dest_parent.has_child(dest_name):
            raise AlreadyExistsException(f"Destination already exists: {dest_path}")

        src_parent.remove_child(src_name)
        entry.set_name(dest_name)
        dest_parent.add_child(entry)

    def _resolve_path(self, path: str) -> FileSystemEntry:
        if not path:
            raise InvalidPathException("Path cannot be empty")

        if not path.startswith("/"):
            raise InvalidPathException("Path must be absolute")

        if path == "/":
            return self._root

        parts = path[1:].split("/")
        current: FileSystemEntry = self._root

        for part in parts:
            if not part:
                raise InvalidPathException("Invalid path: consecutive slashes")

            if not current.is_directory():
                raise NotADirectoryException("Not a directory")

            child = current.get_child(part)
            if child is None:
                raise NotFoundException(f"Path not found: {path}")

            current = child

        return current

    def _resolve_parent(self, path: str) -> Folder:
        if path == "/":
            raise InvalidPathException("Root has no parent")

        last_slash = path.rfind("/")
        parent_path = "/" if last_slash == 0 else path[:last_slash]

        parent = self._resolve_path(parent_path)

        if not parent.is_directory():
            raise NotADirectoryException("Parent is not a directory")

        return parent

    def _extract_name(self, path: str) -> str:
        last_slash = path.rfind("/")
        return path[last_slash + 1:]
