import unittest

from solution import System, INVALID_COMMAND, UNRECOGNIZED_COMMAND, DIRECTORY_NOT_FOUND, INVALID_FILE_OR_FOLDER_NAME, QUIT_MESSAGE, DIRECTORY_ALREADY_EXISTS, FILE_ALREADY_EXISTS


class TestSystem(unittest.TestCase):
    def setUp(self) -> None:
        self._system = System()

        return super().setUp()
    
    def _assertNoOutput(self, output):
        self.assertEqual(output, '')
        
    def testUnrecognizedCommand(self):
        rv = self._system.runCommand('nonexistent')
        self.assertEqual(rv, UNRECOGNIZED_COMMAND)

    
    def testExtraWhitespacesNotRejected(self):
        # checks leading whitespaces
        rv = self._system.runCommand('  pwd')
        self.assertEqual(rv, '/root')

        # checks trailing whitespaces
        rv = self._system.runCommand('pwd   ')
        self.assertEqual(rv, '/root')

        # checks leading and trailing whitespaces
        rv = self._system.runCommand('   pwd   ')
        self.assertEqual(rv, '/root')
    
    def testPWD(self):
        # checks the root directory
        rv = self._system.runCommand('pwd')
        self.assertEqual(rv, '/root')

        # checks invalid command
        rv = self._system.runCommand('pwd 1')
        self.assertEqual(rv, INVALID_COMMAND)

        # checks subdirectories directory
        self._assertNoOutput(self._system.runCommand('mkdir sub1'))
        self._assertNoOutput(self._system.runCommand('cd sub1'))
        rv = self._system.runCommand('pwd')
        self.assertEqual(rv, '/root/sub1')

        self._assertNoOutput(self._system.runCommand('mkdir sub2'))
        self._assertNoOutput(self._system.runCommand('cd sub2'))
        rv = self._system.runCommand('pwd')
        self.assertEqual(rv, '/root/sub1/sub2')

    def testCD(self):
        # checks invalid command
        rv = self._system.runCommand('cd 1 2')
        self.assertEqual(rv, INVALID_COMMAND)

        # checks changing to a subdirectory and back to parent
        self._assertNoOutput(self._system.runCommand('mkdir sub1'))
        self._assertNoOutput(self._system.runCommand('cd sub1'))
        rv = self._system.runCommand('pwd')
        self.assertEqual(rv, '/root/sub1')

        self._assertNoOutput(self._system.runCommand('cd ..'))
        rv = self._system.runCommand('pwd')
        self.assertEqual(rv, '/root')
        
        # tests going to parent in root directory stays there
        self._assertNoOutput(self._system.runCommand('cd ..'))
        rv = self._system.runCommand('pwd')
        self.assertEqual(rv, '/root')

        # checks nonexistent directory
        rv = self._system.runCommand('cd nonexistent')
        self.assertEqual(rv, DIRECTORY_NOT_FOUND)


    def testTouch(self):
        # checks invalid command
        rv = self._system.runCommand('touch 1 2')
        self.assertEqual(rv, INVALID_COMMAND)
        
        # checks unsupported name lenght
        rv = self._system.runCommand('touch name0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        self.assertEqual(rv, INVALID_FILE_OR_FOLDER_NAME)

        # checks correct creation
        self._assertNoOutput(self._system.runCommand('touch file'))
        rv = self._system.runCommand('ls')
        self.assertEqual(rv, 'file')

        # checks overriding file
        self._assertNoOutput(self._system.runCommand('touch file'))
        rv = self._system.runCommand('ls')
        self.assertEqual(rv, 'file')

    def testMkDir(self):
        # checks invalid command
        rv = self._system.runCommand('mkdir 1 2')
        self.assertEqual(rv, INVALID_COMMAND)
        
        # checks unsupported name lenght
        rv = self._system.runCommand('mkdir name0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        self.assertEqual(rv, INVALID_FILE_OR_FOLDER_NAME)

        # checks correct creation
        self._assertNoOutput(self._system.runCommand('mkdir dir'))
        rv = self._system.runCommand('ls')
        self.assertEqual(rv, 'dir')
        
        # checks already existent directory
        rv = self._system.runCommand('mkdir dir')
        self.assertEqual(rv, DIRECTORY_ALREADY_EXISTS)

        # checks directory with file name not allowed
        self._assertNoOutput(self._system.runCommand('touch file'))
        rv = self._system.runCommand('mkdir file')
        self.assertEqual(rv, FILE_ALREADY_EXISTS)

        # checks directory can be accessed
        self._assertNoOutput(self._system.runCommand('cd dir'))
        rv = self._system.runCommand('pwd')
        self.assertEqual(rv, '/root/dir')

    def testLS(self):
        # checks invalid command
        rv = self._system.runCommand('ls r')
        self.assertEqual(rv, INVALID_COMMAND)

        # checks correct behavior
        self._assertNoOutput(self._system.runCommand('touch root-file'))
        self._assertNoOutput(self._system.runCommand('mkdir sub1'))

        rv = self._system.runCommand('ls')
        self.assertEqual(rv, """root-file
sub1""")

        # checks invalid recursive option
        rv = self._system.runCommand('ls -r 1')
        self.assertEqual(rv, INVALID_COMMAND)

        # builds a directory structure to test recursive option
        self._assertNoOutput(self._system.runCommand('cd sub1'))
        self._assertNoOutput(self._system.runCommand('touch sub1-file'))
        self._assertNoOutput(self._system.runCommand('mkdir sub2'))
        self._assertNoOutput(self._system.runCommand('cd sub2'))
        self._assertNoOutput(self._system.runCommand('touch sub2-file1'))
        self._assertNoOutput(self._system.runCommand('mkdir sub3'))
        # creating file after directory to check files are always printed before directories
        # and their contents when using recursive option
        self._assertNoOutput(self._system.runCommand('touch sub2-file2'))
        self._assertNoOutput(self._system.runCommand('cd sub3'))
        self._assertNoOutput(self._system.runCommand('mkdir sub4'))
        self._assertNoOutput(self._system.runCommand('cd sub4'))
        self._assertNoOutput(self._system.runCommand('touch sub4-file1'))
        self._assertNoOutput(self._system.runCommand('touch sub4-file2'))
        self._assertNoOutput(self._system.runCommand('touch sub4-file3'))
        self._assertNoOutput(self._system.runCommand('cd ..'))
        self._assertNoOutput(self._system.runCommand('cd ..'))
        self._assertNoOutput(self._system.runCommand('cd ..'))
        self._assertNoOutput(self._system.runCommand('cd ..'))

        rv = self._system.runCommand('ls -r')
        self.assertEqual(rv, """/root
root-file
/root/sub1
sub1-file
/root/sub1/sub2
sub2-file1
sub2-file2
/root/sub1/sub2/sub3
/root/sub1/sub2/sub3/sub4
sub4-file1
sub4-file2
sub4-file3""")

        
        # checks multi-faceted paths
        rv = self._system.runCommand('ls -mf sub1')
        self.assertEqual(rv, """sub1-file
sub2""")

        # checks trailing slashes
        rv = self._system.runCommand('ls -mf sub1//')
        self.assertEqual(rv, """sub1-file
sub2""")

        # checks nested directories
        rv = self._system.runCommand('ls -mf sub1/sub2')
        self.assertEqual(rv, """sub2-file1
sub3
sub2-file2""")

        # checks recursive option
        rv = self._system.runCommand('ls -mf sub1/sub2 -r')
        self.assertEqual(rv, """/sub2
sub2-file1
sub2-file2
/sub2/sub3
/sub2/sub3/sub4
sub4-file1
sub4-file2
sub4-file3""")

    def testQuit(self):
        # checks invalid command
        rv = self._system.runCommand('quit 1')
        self.assertEqual(rv, INVALID_COMMAND)

        # checks invalid command
        rv = self._system.runCommand('quit')
        self.assertEqual(rv, QUIT_MESSAGE)


if __name__ == '__main__':
    unittest.main()
