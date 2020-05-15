""" utils/query_builder.py"""

import math
from sqlalchemy import asc, desc, and_, or_
from werkzeug.exceptions import InternalServerError, BadRequest


class QueryBuilder:

    def __init__(self, qs, cls):
        """ Parameters
            ----------
            qs (QueryString): instance of QueryString
            cls (Model): Mapped class to DB table, based on SA Model class """

        self.qs = qs
        self.cls = cls
        self.q = None
        self.links = None

    def build_query(self):
        """ Builds a SA query using QueryString.
            Applies sorting, filtering, pagination

            Returns
            -------
            SA query
        """

        # Create query
        q = self.cls.query

        # -------------------------------------------------------------------------
        # Sorting
        for field in self.qs.sort:
            sort_func = asc

            if field[0] == '-':
                field = field[1:]
                sort_func = desc

            # Apply sorting to a query
            q = q.order_by(sort_func(field))

        # -------------------------------------------------------------------------
        # Filtering

        operator_function = {
            "eq": lambda x, y: x == y,
            "ne": lambda x, y: x != y,
            "lt": lambda x, y: x < y,
            "le": lambda x, y: x <= y,
            "gt": lambda x, y: x > y,
            "ge": lambda x, y: x >= y
        }

        def build_criterion(expression):

            op = expression[1].lower()

            if op in ["and", "or"]:
                # Recursively build left and right branches for logical join
                left = build_criterion(expression[0])
                right = build_criterion(expression[2])

                op_func = or_ if op == "or" else and_

            elif op in operator_function:
                # End of branch, actual fitler against value is here
                op_func = operator_function.get(op)

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
            q = q.filter(build_criterion(self.qs.filter))

        # Count = Total matches.
        # In come cases Count might be very SLOW and might need to be excluded
        total_matches = -1

        total_matches = q.order_by(None).count()
        # self.meta["total_matches"] = total_matches # FIXME

        if not hasattr(self.cls, "base_url"):
            raise InternalServerError("""There is a problem with class '{}'.
                Link assembly is Not Implemented. Consider excluding links
                ?exclude=links
                """.format(self.cls.__name__))

        base_url = self.cls.base_url

        base_qs = self.qs.get_querystring(include_pagination=False)

        if not base_qs:
            base_qs = "?page[size]=%d" % self.qs.page["size"]
        else:
            base_qs += "&page[size]=%d" % self.qs.page["size"]

        link_first = None
        link_prev = None
        link_next = None
        link_last = None

        last_page = int(
            math.ceil((total_matches*1.0) / self.qs.page["size"]))

        if self.qs.page["number"] > 1:
            link_first = base_url + base_qs + "&page[number]=1"
            link_prev = base_url + base_qs + \
                "&page[number]=%d" % (self.qs.page["number"] - 1)

        if self.qs.page["number"] < last_page:
            link_last = base_url + base_qs + "&page[number]=%d" % last_page
            link_next = base_url + base_qs + \
                "&page[number]=%d" % (self.qs.page["number"] + 1)

        self.links = {}
        self.links["first"] = link_first
        self.links["prev"] = link_prev
        self.links["next"] = link_next
        self.links["last"] = link_last

        # -------------------------------------------------------------------------
        # Pagination
        q = q.limit(self.qs.page["size"]).offset(
            (self.qs.page["number"]-1)*self.qs.page["size"])

        # -------------------------------------------------------------------------

        self.q = q
