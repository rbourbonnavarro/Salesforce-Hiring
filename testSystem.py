import unittest

from solution import System, INVALID_COMMAND, UNRECOGNIZED_COMMAND


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

        

if __name__ == '__main__':
    unittest.main()
