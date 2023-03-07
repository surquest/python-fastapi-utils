import datetime as dt
from fastapi import Query, Path


class QueryConfig(object):

    def __init__(self, type_, query):

        self.type_ = type_
        self.query = query

    @property
    def type(self):

        return self.type_


class PathConfig(object):

    def __init__(self, type_, path):

        self.type_ = type_
        self.path = path

    @property
    def type(self):

        return self.type_


class Args(object):

    @staticmethod
    def start_date(**config):

        defaults = {
            "default": dt.date.today(),
            "alias": "startDate",
            "description": "Start date (YYYY-MM-DD)",
            "example": dt.date.today()
        }

        if config:
            defaults.update(config)

        return QueryConfig(
            type_=dt.date,
            query=Query(
                **defaults
            )
        )

    @staticmethod
    def end_date(**config):

        defaults = {
            "default": dt.date.today(),
            "alias": "endDate",
            "description": "End date (YYYY-MM-DD)",
            "example": dt.date.today()
        }

        if config:
            defaults.update(config)

        return QueryConfig(
            type_=dt.date,
            query=Query(
                **defaults
            )
        )

    @staticmethod
    def offset(**config):

        defaults = {
            "default": 0,
            "alias": "offset",
            "description": "Offset for pagination",
            "example": 0
        }

        if config:
            defaults.update(config)

        return QueryConfig(
            type_=int,
            query=Query(
                **defaults
            )
        )

    @staticmethod
    def limit(**config):

        defaults = {
            "default": 1000,
            "alias": "limit",
            "description": "Limits number of records returned",
            "example": 1000
        }

        if config:
            defaults.update(config)

        return QueryConfig(
            type_=int,
            query=Query(
                **defaults
            )
        )
