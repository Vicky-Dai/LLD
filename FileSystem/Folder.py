from typing import Dict, List, Optional
from FileSystemEntry import FileSystemEntry

class Folder(FileSystemEntry):
    def __init__(self, name: str):
        super().__init__(name)
        self._children: Dict[str, FileSystemEntry] = {}

    def is_directory(self) -> bool:
        return True

    def add_child(self, entry: FileSystemEntry) -> bool:
        if entry is None:
            return False

        if entry.get_name() in self._children: # 检查重名
            return False

        self._children[entry.get_name()] = entry
        entry.set_parent(self) # 别忘了结构关系
        return True

    def remove_child(self, name: str) -> Optional[FileSystemEntry]:
        entry = self._children.pop(name, None) # pop删除同时会返回value
        if entry is not None:
            entry.set_parent(None) # 结构关系！！
        return entry

    def get_child(self, name: str) -> Optional[FileSystemEntry]:
        return self._children.get(name)

    def has_child(self, name: str) -> bool:
        return name in self._children

    def get_children(self) -> List[FileSystemEntry]:
        return list(self._children.values())
