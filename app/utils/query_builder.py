""" utils/query_builder.py"""

import math
from sqlalchemy import asc, desc, and_, or_
from werkzeug.exceptions import BadRequest, NotImplemented as NotImplemented501


class QueryBuilder:

    OPERATOR_FUNCTIONS = {
        "eq": lambda x, y: x == y,
        "ne": lambda x, y: x != y,
        "lt": lambda x, y: x < y,
        "le": lambda x, y: x <= y,
        "gt": lambda x, y: x > y,
        "ge": lambda x, y: x >= y
    }

    def __init__(self, qs, cls):
        """ Parameters
            ----------
            qs (QueryString): instance of QueryString
            cls (Model): Mapped class to DB table, based on SA Model class """

        self.qs = qs
        self.cls = cls
        self.q = self.cls.query
        self.links = None

    def _apply_sort(self):
        """ Applies sorting to a query """

        for field in self.qs.sort:
            sort_func = asc

            if field[0] == '-':
                field = field[1:]
                sort_func = desc

            # Apply sorting to a query
            self.q = self.q.order_by(sort_func(field))

    def _apply_filter(self):
        """ Applies filter to a query """

        def build_criterion(expression):
            """ Helper function to asseble chain of filters """

            op = expression[1].lower()

            if op in ["and", "or"]:
                # Recursively build left and right branches for logical join
                left = build_criterion(expression[0])
                right = build_criterion(expression[2])

                op_func = or_ if op == "or" else and_

            elif op in QueryBuilder.OPERATOR_FUNCTIONS:
                # End of branch, actual fitler against value is here
                op_func = QueryBuilder.OPERATOR_FUNCTIONS.get(op)

                # Get column from SA model
                attr_name = expression[0]
                if not hasattr(self.cls, attr_name):
                    raise BadRequest("""Resource {} does not have attribute '{}'
                                     """.format(self.cls.__name__, attr_name))

                left = getattr(self.cls, attr_name)

                # Value
                right = expression[2]

                # String values have single quote inside double quotes
                if isinstance(right, str):
                    right = right.replace("'", "")

            else:
                raise BadRequest("Unknown filter operator '{}'".format(op))

            return op_func(left, right)

        # Apply all filters if any
        if self.qs.filter:
            self.q = self.q.filter(build_criterion(self.qs.filter))

    def _apply_pagination(self):
        """ Applies Pagination to a query.
            Constructs links to first, next, previous, last pages """

        # Count = Total matches.
        total_matches = self.q.order_by(None).count()

        if not hasattr(self.cls, "base_url"):
            raise NotImplemented501("""There is a problem with class '{}'.
                Link assembly is Not Implemented. Consider excluding links
                ?exclude=links
                """.format(self.cls.__name__))

        base_url = self.cls.base_url

        base_qs = self.qs.get_querystring(include_pagination=False)

        if not base_qs:
            base_qs = "?page[size]={}".format(self.qs.page["size"])
        else:
            base_qs += "&page[size]={}".format(self.qs.page["size"])

        self.links = {
            "first": None,
            "prev": None,
            "next": None,
            "last": None
        }

        last_page = int(math.ceil((total_matches*1.0) / self.qs.page["size"]))

        base = base_url + base_qs
        if self.qs.page["number"] > 1:
            self.links["first"] = base + "&page[number]=1"
            self.links["prev"] = base + "&page[number]={}".format(
                (self.qs.page["number"] - 1))

        if self.qs.page["number"] < last_page:
            self.links["last"] = base + "&page[number]={}".format(last_page)
            self.links["next"] = base + "&page[number]={}".format(
                (self.qs.page["number"] + 1))

        # Apply Pagination
        offset = (self.qs.page["number"] - 1) * self.qs.page["size"]
        self.q = self.q.limit(self.qs.page["size"]).offset(offset)

    def build_query(self, apply_pagination=True):
        """ Builds a SA query using QueryString.
            Applies sorting, filtering, pagination

            Returns
            -------
            SA query
        """

        self._apply_sort()
        self._apply_filter()

        if apply_pagination:
            self._apply_pagination()
