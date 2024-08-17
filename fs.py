import yaml
import json
import copy

class FSException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message

class File:
    def __init__(self, name: str, channel_id: int, parent_dir: 'Directory') -> None:
        self.name = name
        self.channel_id = channel_id
        self.parent_dir = parent_dir

class Directory:
    def __init__(self, name: str | None, path: list, data: dict, parent: 'Directory', allow_corrupt: bool = False) -> None:
        self.name = name
        self.path = path
        self.parent = parent
        self.files = {}
        self.directories = {}
        for key, value in data.copy().items():
            if type(value) is int:
                self.files[key] = File(key, value, self)
            elif type(value) is dict:
                new_path = path.copy()
                if name is not None:
                    new_path.append(name)
                self.directories[key] = Directory(key, new_path, value, self, allow_corrupt)
            elif allow_corrupt:
                continue
            else:
                raise FSException("Corrupt directory")

    # GET 
    def get_file(self, name: str) -> File:
        if name in self.files:
            return self.files[name]
        else:
            raise FSException("No such file")
    def get_directory(self, name: str) -> 'Directory':
        if name in self.directories:
            return self.directories[name]
        else:
            raise FSException("No such directory")
        
    # CHECK
    def exists(self, name: str) -> bool:
        if name in self.files or name in self.directories:
            return True
        return False
    def is_file(self, name: str) -> bool:
        if name in self.files:
            return True
        return False
    def is_dir(self, name: str) -> bool:
        if name in self.directories:
            return True
        return False

    # LIST
    def ls_file(self) -> list:
        return list(self.files.keys())
    def ls_dir(self) -> list:
        return list(self.directories.keys())

class FileSystem:
    def __init__(self, yaml_data: str, allow_corrupt: bool = False) -> None:
        data = yaml.safe_load(yaml_data)
        if data is None:
            raise FSException("Corrupt file system")
        self.root = Directory(None, [], data, None, allow_corrupt)
        self.wd = copy.deepcopy(self.root)

    # PATH
    def pwd(self) -> str:
        return f"/{"/".join(self.wd.path + ([self.wd.name] if self.wd.name is not None else []))}"
    
    def resolve_path(self, path: list) -> Directory | File:
        current_dir: Directory = copy.deepcopy(self.wd)
        for i in range(len(path)):
            name = path[i]
            if name == "":
                current_dir = copy.deepcopy(self.root)
            elif name == ".":
                continue
            elif name == "..":
                current_dir = copy.deepcopy(current_dir.parent)
            elif not current_dir.exists(name):
                raise FSException("No such file or directory")
            elif current_dir.is_dir(name):
                current_dir = copy.deepcopy(current_dir.get_directory(name))
            elif i == len(path) - 1:
                return current_dir.get_file(name) # file return
            else:
                raise FSException("This is a file not a directory")
        return current_dir # directory return

    def parse_path(self, path: str) -> list:
        return path.split("/")
    
    def cd(self, path: str) -> None:
        path_list = self.parse_path(path)
        new_dir = self.resolve_path(path_list)
        if type(new_dir) is Directory:
            self.wd = copy.deepcopy(new_dir)
        else:
            raise FSException("This is a file not a directory")
    
    # LIST
    def ls_file(self, path: str | None) -> list:
        if path is None:
            return self.wd.ls_file()
        else:
            path_list = self.parse_path(path)
            new_dir = self.resolve_path(path_list)
            if type(new_dir) is Directory:
                return new_dir.ls_file()
            else:
                raise FSException("This is a file not a directory")

    def ls_dir(self, path: str | None) -> list:
        if path is None:
            return self.wd.ls_dir()
        else:
            path_list = self.parse_path(path)
            new_dir = self.resolve_path(path_list)
            if type(new_dir) is Directory:
                return new_dir.ls_dir()
            else:
                raise FSException("This is a file not a directory")
    
    # GET
    def get_file(self, path: str) -> File:
        path_list = self.parse_path(path)
        new_dir = self.resolve_path(path_list)
        if type(new_dir) is Directory:
            raise FSException("This is a directory not a file")
        else:
            return new_dir
    
    def get_directory(self, path: str) -> Directory:
        path_list = self.parse_path(path)
        new_dir = self.resolve_path(path_list)
        if type(new_dir) is Directory:
            return new_dir
        else:
            raise FSException("This is a file not a directory")
        
    # CREATE
    def mkdir(self, path: str) -> None:
        path_list = self.parse_path(path)
        current_dir = self.resolve_path(path_list[:-1])
        if current_dir.exists(path_list[-1]):
            raise FSException("A file or directory with that name already exists")
        current_dir.directories[path_list[-1]] = Directory(path_list[-1], path_list[:-1], {}, current_dir)

    def touch(self, path: str, channel_id: int) -> None:
        path_list = self.parse_path(path)
        current_dir = self.resolve_path(path_list[:-1])
        if current_dir.exists(path_list[-1]):
            raise FSException("A file or directory with that name already exists")
        current_dir.files[path_list[-1]] = File(path_list[-1], channel_id, current_dir)

    # DELETE
    def rm(self, path: str) -> None:
        path_list = self.parse_path(path)
        current_dir = self.resolve_path(path_list[:-1])
        if current_dir.is_file(path_list[-1]):
            del current_dir.files[path_list[-1]]
        else:
            raise FSException("Directories cannot be removed with `rm` use `rmdir`")
        
    def rmdir(self, path: str) -> None:
        path_list = self.parse_path(path)
        current_dir = self.resolve_path(path_list[:-1])
        if current_dir.is_dir(path_list[-1]):
            del current_dir.directories[path_list[-1]]
        else:
            raise FSException("Files cannot be removed with `rmdir` use `rm`")