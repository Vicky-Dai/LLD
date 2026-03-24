from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from Folder import Folder

""" ABC 是 Python 里用来写抽象基类的。你这里 class FileSystemEntry(ABC) 的意思是，
FileSystemEntry 是一个“父类模板”，可以放共享逻辑，但不希望你直接拿它来创建对象。
它通常和 @abstractmethod 一起用。 """
class FileSystemEntry(ABC):
    def __init__(self, name: str):
        self._name = name
        self._parent: Optional['Folder'] = None

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    def get_parent(self) -> Optional['Folder']:
        return self._parent

    def set_parent(self, parent: Optional['Folder']) -> None:
        self._parent = parent

    def get_path(self) -> str:
        if self._parent is None:
            return self._name

        parent_path = self._parent.get_path()
        if parent_path == "/":
            return "/" + self._name
        return parent_path + "/" + self._name

    @abstractmethod
    def is_directory(self) -> bool:
        pass
""" 因为 is_directory() 是父类没法给通用实现的方法，所以才标成 @abstractmethod。
name、parent、get_path() 这些在 File 和 Folder 里逻辑是共用的，父类可以直接实现，
但 is_directory() 的返回值在两个子类里正好相反，File 要返回 False，Folder 要返回 True，
所以必须强制子类自己实现。 """