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

Entry = namedtuple('Entry', ['name', 'contents', 'type', 'parent'])

class InvalidArguments(Exception):
    """Exception thrown when the arguments given are not suitable for the command being run."""
    pass


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

        return 'quit'


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
    
    def run(self, args):
        if len(args) > 1:
            raise InvalidArguments
            
        def _visit(result, full_path, entry):
            result.append(PATH_SEPARATOR + PATH_SEPARATOR.join(full_path))
            for item_name, item_entry in entry.contents.items():
                if item_entry.type == DIRECTORY_TYPE:
                    _visit(result, full_path + [item_name], item_entry)
                else:
                    result.append(item_name)

        recursive = False
        if len(args) == 1:
            if args[0] != self.RECURSIVE_OPTION:
                raise InvalidArguments
            else:
                recursive = True

        cwd = self._system.getCWD()
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
            return DIRECTORY_ALREADY_EXISTS
            
        self._system.createDir(name)

        return ''


class CdCommand(Command):
    def run(self, args):
        if len(args) != 1:
            raise InvalidArguments
        
        name = args[0]
        if len(name) > 100:
            raise InvalidArguments

        if name == '..':
            self._system.changeDir(name)
        else:
            items = self._system.getCWD().contents
            if name in items:
                if items[name].type != DIRECTORY_TYPE:
                    return DIRECTORY_NOT_FOUND
                else:
                    self._system.changeDir(name)
            else:
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
            if result == 'quit':
                break
            if result != '':
                print(result)
