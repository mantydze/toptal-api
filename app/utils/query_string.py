import urllib.parse
import pyparsing as pp
from werkzeug.exceptions import BadRequest


class QSPair():
    """QSPair object holds 4 variables
        parameter (str) - query parameter
        keys (list) : list of keys (in square brackets)
        value (str) : value (everything what comes after '=' sign
        kv_str (str) : original key-value string
    """

    def __init__(self, parameter, keys, value, kv_str):
        self.parameter = parameter
        self.keys = keys
        self.value = value
        self.kv_str = kv_str

    def __str__(self):
        return "Parameter '{}' Keys [{}] Value '{}'".format(
            self.parameter,
            ", ".join(self.keys),
            self.value)


class QSParser():

    def __init__(self):
        self.pairs = []

    def parse(self, query_string):
        """ Parses given query string into list of QSPair objects

            Parameters
            ----------
            query_string (str) : decoded query string of a request
            Raise BadRequest if fails to parse
        """

        if query_string and query_string[0] == '?':
            query_string = query_string.replace("?", "")

        # Empty querystring
        if not query_string:
            return

        # Split querystring to key-value pairs
        for pair in query_string.split("&"):
            self.pairs.append(self._parse_pair(pair))

    def _parse_pair(self, pair):
        """ Parse key value pair

            Parameters
            ----------
            pair (str) : parameter pair
                        example: page[number]=1
                        example: filter=(x eq 1) AND (y gt 2)

            Returns
            -------
            obj (QSPair) : parsed key=value parameter pair

            Raise BadRequest if fails to parse
        """

        try:
            leftside, value = pair.split("=")

            # Split leftside into parameter and keys
            # for example page[size]
            elements = leftside.split('[')
            parameter = elements[0]
            # Array of keys. Supports multiple keys if needed in future
            keys = [key[:-1] for key in elements[1:]]

            return QSPair(parameter, keys, value, pair)

        except Exception:
            raise BadRequest("""QueryString(URL): Invalid parameter '{}'
                             """.format(pair))


class QueryString:

    # Supported parameters
    PARAMETERS = (
        'filter',
        'page',
        'sort'
    )

    def __init__(self, query_string):
        self.qs = urllib.parse.unquote(query_string)
        self.parser = QSParser()

        self.filter = []
        self.page = {"number": 1, "size": 20}
        self.sort = []

    def parse(self):
        """ Parses given query string into parameter pairs """

        self.parser.parse(self.qs)

        for pair in self.parser.pairs:
            if pair.parameter not in QueryString.PARAMETERS:
                raise BadRequest("""Unsupported parameter '{}'
                                 """.format(pair.kv_str))

            if pair.parameter == "filter":
                self._add_filter(pair)
            elif pair.parameter == "page":
                self._add_page(pair)
            elif pair.parameter == "sort":
                self._add_sort(pair)

    def _is_int(self, s):
        """ Helper function checks if given string is integer

            Parameters
            ----------
            s (str) : string value to be checked

            Returns:
            True if string is integer. Otherwise False
        """

        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    def _add_page(self, pair):
        """ Convert data of QSPair into querystring pagination

            Parameters
            ----------
            pair(QSPair) : data from URL

            Raises BadRequest if pagination parameters are invalid
        """

        if len(pair.keys) == 0:
            raise BadRequest("Pagination: missing key (number or size)")

        key = pair.keys[0]

        # Check if pagination key is supported
        if key not in ('number', 'size'):
            raise BadRequest(""" Pagination: key '{}' is not supported.
                                 Supported ('number', 'size')""".format(key))

        # Check if value is integer
        if not self._is_int(pair.value):
            raise BadRequest(""" Pagination: expected integer value,
                                 received '{}'""".format(pair.value))

        value = int(pair.value)

        # Any value must be greater than zero
        if value <= 0:
            raise BadRequest(""" Pagination: expected positive value,
                                 received '{}'""".format(value))

        self.page[key] = value

    def _add_sort(self, pair):
        """" Convert data of QSPair into querystring sort

            Parameters
            ----------
            pair(QSPair) : data from URL

            Raises BadRequest if trying to sort by unknown field
        """

        fields = pair.value.split(',')

        for field in fields:

            # Check if field is not empty
            if not field:
                return

            field_asc = field_desc = None  # field without and with minus sign

            if field[0] == '-':
                field_asc = field[1:]  # trim minus sign
                field_desc = field
            else:
                field_asc = field
                field_desc = "-{}".format(field)  # add minus sign

            # Checks if field name without minus sign in a valid field name
            if field_asc not in self.valid_fields:
                raise BadRequest("Sorting: Unknown field '{}'".format(field))

            # Checks if field name (with minus and without)
            # is not yet in list of sort fields
            if (field_asc not in self.sort) and (field_desc not in self.sort):
                # Add unmodified field name
                self.sort.append(field)

    def _add_filter(self, pair):
        """ Convert data of QSPair into filter expression

            Parameters
            ----------
            pair(QSPair) : data from URL

            Raises BadRequest if cannot parse given query
        """

        operator = pp.oneOf("eq ne lt le gt ge").setName("operator")
        number = pp.pyparsing_common.number()

        word = pp.Word(pp.alphas, pp.alphanums + "_-*(1234567890,)")
        term = word | number | pp.quotedString
        condition = pp.Group(term + operator + term)

        expr = pp.operatorPrecedence(condition, [('AND', 2, pp.opAssoc.LEFT,),
                                                 ('OR', 2, pp.opAssoc.LEFT,)])

        try:
            self.filter = expr.parseString(pair.value, parseAll=True)[0]
        except pp.ParseException:
            raise BadRequest("Filter query cannot be parsed. Check syntax")

    def get_querystring(self, include_pagination=True):
        """ Assemble query string from a parsed QueryString object.
            Should match original query string (without unsupported stuff).
            Intended usage for pagination links.

            Parameters
            ----------
            include_pagination (bool) : include or not

            Returns
            -------
            s (str) - assembled query string
        """

        def build_filter_string(arr):
            """ Assembles filter expression
            """
            result = ""

            op = arr[1]

            if op.upper() in ["AND", "OR"]:
                left = build_filter_string(arr[0])
                right = build_filter_string(arr[2])
            else:
                left = arr[0]
                right = arr[2]

            result = "({} {} {})".format(left, op, right)

            return result

        qs = []

        if self.sort:
            qs.append("sort=" + ",".join(self.sort))

        if self.filter:
            qs.append("filter=({})".format(build_filter_string(self.filter)))

        if include_pagination:
            qs.append("page[number]=%d" % self.page["number"])
            qs.append("page[size]=%d" % self.page["size"])

        # Assemble query string
        s = "?" + "&".join(qs) if qs else ""

        return s
