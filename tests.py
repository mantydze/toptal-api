from unittest import TestLoader, TextTestRunner

from tests.e2e.test_run import TestRun
from tests.e2e.test_user import TestUser

if __name__ == "__main__":
    loader = TestLoader()
    suite = loader.discover("tests")

    # suite = loader.loadTestsFromTestCase(TestRun)
    # suite = loader.loadTestsFromTestCase(TestUser)

    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
