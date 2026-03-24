📁 What is an In-Memory File System?
You already know what a file system is, you use one every day. Open Finder or Windows Explorer, and you're navigating folders, creating files, moving things around. An in-memory file system is just that, minus the disk. Everything lives in RAM, which means we get to focus purely on the data structures and operations without worrying about persistence, caching, or I/O performance.

Requirements
When the interview starts, you'll get something like:
"Design an in-memory file system that supports creating files and directories, navigating paths, and basic file operations."
File systems are familiar territory, which makes this problem deceptively tricky. Everyone knows how file systems work from using their computer, so candidates often skip clarification and start designing immediately. That's a mistake. The interviewer has specific expectations about scope, and your mental model of "file system" might not match theirs.


Requirements:
1. Hierarchical file system with single root directory
2. Files store string content
3. Folders contain files and other folders
4. Create and delete files and folders
5. List contents of a folder
6. Navigate/resolve absolute paths (e.g., /home/user/docs)
7. Rename and move files and folders
8. Retrieve full path from any file/folder reference
9. Scale to tens of thousands of entries in memory

Out of Scope:
- Search functionality
- Relative path resolution (../ or ./)
- Permissions, ownership, timestamps
- File type-specific behavior
- Persistence / disk storage
- Symbolic links
- UI layer


FileSystem
- root
+ createFile()
+ createFolder()
+ deleteFile()
+ deleteFolder()
+ move()
+ listContentofFolder()
+ navigateAbsolutePath()
+ retrievePath()

Folder
- files
- folders
+ getFiles()

File
- content
- path
+ getContent()
+ getPath()

FileSystem
    └── root: Folder
            ├── Folder ("home")
            │       └── Folder ("user")
            │               ├── File ("notes.txt")
            │               └── Folder ("docs")
            └── File ("readme.txt")