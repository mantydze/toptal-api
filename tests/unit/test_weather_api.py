import unittest

from app.utils.weather_api import get_weather


class TestWeatherAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_01_no_key(self):
        """ Try use API without api key
        """

        weather = get_weather(10, 10)
        assert weather is None

    @classmethod
    def tearDownClass(cls):
        pass
