from unittest import TestLoader, TextTestRunner

if __name__ == "__main__":
    loader = TestLoader()
    suite = loader.discover("tests")

    # from tests.e2e.test_db import TestDB
    # suite = loader.loadTestsFromTestCase(TestDB)

    # from tests.e2e.test_user import TestUser
    # suite = loader.loadTestsFromTestCase(TesUser)

    # from tests.unit.test_query_string import TestQueryString
    # suite = loader.loadTestsFromTestCase(TestQueryString)

    # from tests.unit.test_weather_api import TestWeatherAPI
    # suite = loader.loadTestsFromTestCase(TestWeatherAPI)

    # from tests.unit.test_query_builder import TestQueryBuilder
    # suite = loader.loadTestsFromTestCase(TestQueryBuilder)

    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
