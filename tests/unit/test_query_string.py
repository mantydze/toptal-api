import unittest
from app.utils.query_string import QueryString
from werkzeug.exceptions import BadRequest


class TestQueryString(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_01_invalid_none(self):
        """ Parse None """
        qs = QueryString(None)
        qs.parse()
        assert len(qs.parser.pairs) == 0

    def test_02_invalid_empty(self):
        """ Parse empty string  """
        qs = QueryString("")
        qs.parse()
        assert len(qs.parser.pairs) == 0

    def test_03_invalid_random(self):
        """ Parse invalid random parameters  """
        qs = QueryString("-235-235-2346561#$%^&*")
        self.assertRaises(BadRequest, qs.parse)

    def test_04_invalid_unknown_parameter(self):
        """ Parse unknown parameter  """
        qs = QueryString("?unknown_parameter[key]=value")
        self.assertRaises(BadRequest, qs.parse)

    def test_04_invalid_sort_unknown(self):
        """ Sort unknown field """
        qs = QueryString("?sort=field_name")
        self.assertRaises(BadRequest, qs.parse)

    def test_05_invalid_filter_unknown(self):
        """ Filter unknown field """
        qs = QueryString("?filter=(field_name eq 1")
        self.assertRaises(BadRequest, qs.parse)

    def test_06_invalid_paginate_unknown_key(self):
        """ Paginate unknown key """
        qs = QueryString("?page[siiize]=10")
        self.assertRaises(BadRequest, qs.parse)

    def test_07_invalid_paginate_no_key(self):
        """ Paginate no key """
        qs = QueryString("?page=10")
        self.assertRaises(BadRequest, qs.parse)

    def test_08_invalid_paginate_subzero(self):
        """ Paginate using sub zero value """
        qs = QueryString("?page[size]=-1")
        self.assertRaises(BadRequest, qs.parse)

    def test_09_invalid_paginate_nonint(self):
        """ Paginate using letter """
        qs = QueryString("?page[size]=abc")
        self.assertRaises(BadRequest, qs.parse)

    def test_10_valid_sort(self):
        """ Parse valid sort """
        qs = QueryString("?sort=field1,-field2", ["field1", "field2"])
        qs.parse()

        assert all(field in qs.sort for field in ["field1", "-field2"])

    def test_11_valid_paginate(self):
        """ Parse valid pagination """
        qs = QueryString("?page[size]=123&page[number]=321")
        qs.parse()

        assert (qs.page["size"] == 123) and (qs.page["number"] == 321)

    def test_12_valid_query(self):
        """ Parse valid query.
            Check if parsed and reconstructed querystring has same parts """

        qs_parts = []
        qs_parts.append("page[size]=123")
        qs_parts.append("page[number]=321")
        qs_parts.append("sort=field1,-field2")
        qs_parts.append("filter=((field1 eq 1) AND (field2 lt 2))")

        qs = QueryString("?" + "&".join(qs_parts), ["field1", "field2"])
        qs.parse()

        qstring = qs.get_querystring()

        assert all(part in qstring for part in qs_parts)

    def test_13_invalid_paginate(self):
        """ Parse invalid pagination. Exceeding max page size """
        qs = QueryString("?page[size]=9999999")
        self.assertRaises(BadRequest, qs.parse)

    @classmethod
    def tearDownClass(cls):
        pass
