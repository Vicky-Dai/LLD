from FileSystemEntry import FileSystemEntry

class File(FileSystemEntry): #!!!!! 继承记得写
    def __init__(self, name: str, content: str):
        super().__init__(name) #先去执行父类的构造函数，把父类里通用的初始化做好，不用再写一遍了
        self._content = content

    def get_content(self) -> str:
        return self._content

    def set_content(self, content: str) -> None:
        self._content = content

    def is_directory(self) -> bool:
        return False
