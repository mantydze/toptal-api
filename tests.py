from unittest import TestLoader, TextTestRunner

from tests.e2e.test_run import TestRun

if __name__ == "__main__":
    loader = TestLoader()
    # suite = loader.discover("tests")

    suite = loader.loadTestsFromTestCase(TestRun)

    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
