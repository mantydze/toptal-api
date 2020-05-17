from unittest import TestLoader, TextTestRunner

if __name__ == "__main__":
    loader = TestLoader()
    suite = loader.discover("tests")
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
