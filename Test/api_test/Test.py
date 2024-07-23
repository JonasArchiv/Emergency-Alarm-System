import unittest
from tests.ping_test import PingTestCase
from tests.apikeycheck_test import APIKeyCheckTestCase

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PingTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(APIKeyCheckTestCase))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
