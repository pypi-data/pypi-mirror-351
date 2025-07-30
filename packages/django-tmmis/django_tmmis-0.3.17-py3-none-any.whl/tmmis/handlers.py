from collections import namedtuple
from enum import Enum
from typing import Any, Tuple

from django.db import connections


class ResultType(Enum):
    TUPLE = 0
    DICT = 1
    NAMEDTUPLE = 2


# noinspection PyArgumentList
def select_all(sql: str, params: Tuple[Any] = None, result_type: ResultType = ResultType.TUPLE):
    with connections["tmmis"].cursor() as cursor:
        cursor.execute(sql, params)
        if result_type == ResultType.DICT:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif result_type == ResultType.NAMEDTUPLE:
            desc = cursor.description
            result = namedtuple("Result", [col[0] for col in desc])
            return [result(*row) for row in cursor.fetchall()]
        else:
            return cursor.fetchall()


def select_one(sql: str, params: Tuple[Any] = None):
    with connections["tmmis"].cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def query(sql: str, params: Tuple[Any] = None):
    with connections["tmmis"].cursor() as cursor:
        cursor.execute(sql, params)
