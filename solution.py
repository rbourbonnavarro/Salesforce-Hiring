import sys
from abc import ABC, abstractmethod
from collections import defaultdict, namedtuple


# System entry types
DIRECTORY_TYPE = 'd'
FILE_TYPE = 'f'

# System path separator
PATH_SEPARATOR = '/'

# Error messages
INVALID_COMMAND = 'Invalid command'
UNRECOGNIZED_COMMAND = 'Unrecognized command'
INVALID_FILE_OR_FOLDER_NAME = 'Invalid File or Folder Name'
DIRECTORY_NOT_FOUND = 'Directory not found'
DIRECTORY_ALREADY_EXISTS = 'Directory already exists'
FILE_ALREADY_EXISTS = 'File already exists'

# Exit message
QUIT_MESSAGE = 'quit'

Entry = namedtuple('Entry', ['name', 'contents', 'type', 'parent'])

class InvalidArguments(Exception):
    """Exception thrown when the arguments given are not suitable for the command being run."""
    pass



MULTI_FACETED_PATH_OPTION = '-mf'

class Command(ABC):    
    def __init__(self, system) -> None:
        self._system = system

    @abstractmethod
    def run(self, args):
        pass


class QuitCommand(Command):
    def run(self, args):
        if len(args) > 0:
            raise InvalidArguments

        return QUIT_MESSAGE


class PwdCommand(Command):
    def run(self, args):
        if len(args) > 0:
            raise InvalidArguments

        cwd = self._system.getCWD()

        cwd_name = cwd.name
        while cwd.parent is not None:
            cwd_name = cwd.parent.name + PATH_SEPARATOR + cwd_name
            cwd = cwd.parent

        return PATH_SEPARATOR + cwd_name


class LsCommand(Command):
    RECURSIVE_OPTION = '-r'
    
    def _validate_args(self, args):
        recursive = False
        path = ''
        multi_faceted_path = False

        if self.RECURSIVE_OPTION in args:
            recursive = True
            args.pop(args.index(self.RECURSIVE_OPTION))

        if MULTI_FACETED_PATH_OPTION in args:
            multi_faceted_path = True
            args.pop(args.index(MULTI_FACETED_PATH_OPTION))
            
            if len(args) != 1:
                raise InvalidArguments
                
            path = args.pop(0).rstrip('/')

        if len(args) > 0:
            raise InvalidArguments

        return recursive, multi_faceted_path, path

    def run(self, args):
        recursive, multi_faceted_path, path = self._validate_args(args)
            
        def _visit(result, full_path, entry):
            result.append(PATH_SEPARATOR + PATH_SEPARATOR.join(full_path))
            dirs = []
            for item_name, item_entry in entry.contents.items():
                if item_entry.type == DIRECTORY_TYPE:
                    dirs.append(item_entry)
                else:
                    result.append(item_name)
            for dir in dirs:
                _visit(result, full_path + [dir.name], dir)

        cwd = self._system.getCWD()
        if multi_faceted_path:
            dirs = path.split('/')
            for dir in dirs:
                if dir in cwd.contents and cwd.contents[dir].type == DIRECTORY_TYPE:
                    cwd = cwd.contents[dir]
                else:
                    return DIRECTORY_NOT_FOUND
            
        result = []
        if recursive:
            full_path = [cwd.name]
            _visit(result, full_path, cwd)
        else:
            result = cwd.contents

        return '\n'.join(result)


class MkdirCommand(Command):
    def run(self, args):
        if len(args) != 1:
            raise InvalidArguments
        
        name = args[0]
        if len(name) > 100:
            return INVALID_FILE_OR_FOLDER_NAME

        items = self._system.getCWD().contents
        if name in items:
            if items[name].type == DIRECTORY_TYPE:
                return DIRECTORY_ALREADY_EXISTS
            else:
                return FILE_ALREADY_EXISTS
            
        self._system.createDir(name)

        return ''


class CdCommand(Command):
    def _validate_args(self, args):
        path = ''
        multi_faceted_path = False

        if MULTI_FACETED_PATH_OPTION in args:
            multi_faceted_path = True
            args.pop(args.index(MULTI_FACETED_PATH_OPTION))
            
        if len(args) != 1:
            raise InvalidArguments
            
        path = args.pop(0).rstrip('/')

        return multi_faceted_path, path

    def run(self, args):
        multi_faceted_path, path = self._validate_args(args)

        def _change_dir(dir):
            if dir == '..':
                self._system.changeDir(dir)
            else:
                items = self._system.getCWD().contents
                if dir in items:
                    if items[dir].type != DIRECTORY_TYPE:
                        return False
                    else:
                        self._system.changeDir(dir)
                else:
                    return False

            return True

        if multi_faceted_path:
            dirs = path.split('/')
            for dir in dirs:
                if not _change_dir(dir):
                    return DIRECTORY_NOT_FOUND
        else:
            if not _change_dir(path):
                return DIRECTORY_NOT_FOUND

        return ''


class TouchCommand(Command):
    def run(self, args):
        if len(args) != 1:
            raise InvalidArguments
        
        name = args[0]
        if len(name) > 100:
            return INVALID_FILE_OR_FOLDER_NAME

        items = self._system.getCWD().contents
        if name not in items:
            self._system.createFile(name)

        return ''


class System(object):
    def __init__(self, ) -> None:
        self._root = Entry('root', {}, DIRECTORY_TYPE, None)
        self._cwd = self._root
        self._commands = {
            'quit': QuitCommand(self),
            'pwd': PwdCommand(self),
            'ls': LsCommand(self),
            'mkdir': MkdirCommand(self),
            'cd': CdCommand(self),
            'touch': TouchCommand(self),
        }

    def runCommand(self, commandLine):
        args = commandLine.strip().split(' ')
        command = args.pop(0)

        if command not in self._commands:
            return UNRECOGNIZED_COMMAND

        try:
            return self._commands[command].run(args)
        except InvalidArguments:
            return INVALID_COMMAND

    def getCWD(self):
        return self._cwd

    def createDir(self, name):
        self._cwd.contents[name] = Entry(name, {}, DIRECTORY_TYPE, self._cwd)

    def changeDir(self, name):
        if name == '..':
            if self._cwd.parent is not None:
                self._cwd = self._cwd.parent
        else:
            self._cwd = self._cwd.contents[name]

    def createFile(self, name):
        self._cwd.contents[name] = Entry(name, '', FILE_TYPE, self._cwd)


if __name__ == '__main__':
    system = System()
    while True:
            ri = input()
            if not ri:
                continue
            result = system.runCommand(ri)
            if result == QUIT_MESSAGE:
                break
            if result != '':
                print(result)
