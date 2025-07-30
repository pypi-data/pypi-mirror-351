from typing import List

from sqlalchemy.orm import query

from thalentfrx.core.entities.Filter import Filter, OperatorTypes
from thalentfrx.core.entities.Sort import Sort, SortDirections

def order_query(q: query, sort_list: List[Sort], model_name: str = "", eval_context: dict = None):
    if eval_context is None:
        eval_context = {}

    for s in sort_list:
        if s["dir"] == SortDirections.DESC.value:
            if model_name is None or model_name != "":
                exp = f"{model_name}.{s['property']}.desc()"
            else:
                exp = f"{s['property']}.desc()"
        else:
            if model_name is None or model_name != "":
                exp = f"{model_name}.{s['property']}"
            else:
                exp = f"{s['property']}"

        q = q.order_by(eval(exp, globals(), eval_context))
    return q


def filter_query(q: query, filter_list: List[Filter], model_name: str = "", eval_context: dict = None):
    if eval_context is None:
        eval_context = {}

    for f in filter_list:
        operator = f["operator"] if f["operator"] is not None else OperatorTypes.EQUAL.value

        if f["operator"] == OperatorTypes.LIKE.value:
            if model_name is None or model_name != "":
                exp = f"{model_name}.{f['property']}.like('%{f['value']}%')"
            else:
                exp = f"{f['property']}.like('%{f['value']}%')"

        elif f["operator"] == OperatorTypes.IN.value:
            in_clause = __construct_in_clause(f)
            if model_name is None or model_name != "":
                exp = f"{model_name}.{f['property']}.in_({in_clause})"
            else:
                exp = f"{f['property']}.in_({in_clause})"

        elif f["operator"] == OperatorTypes.BETWEEN.value:
            if model_name is None or model_name != "":
                exp = f"{model_name}.{f['property']}.between({f['value']})"
            else:
                exp = f"{f['property']}.between({f['value']})"

        elif f["operator"] == OperatorTypes.NOT_IN.value:
            in_clause = __construct_in_clause(f)
            if model_name is None or model_name != "":
                exp = f"{model_name}.{f['property']}.not_in({in_clause})"
            else:
                exp = f"{f['property']}.not_in({in_clause})"

        elif f["operator"] == OperatorTypes.START_WITH.value:
            if model_name is None or model_name != "":
                exp = f"{model_name}.{f['property']}.startswith('{f['value']}')"
            else:
                exp = f"{f['property']}.startswith('{f['value']}')"

        elif f["operator"] == OperatorTypes.END_WITH.value:
            if model_name is None or model_name != "":
                exp = f"{model_name}.{f['property']}.endswith('{f['value']}')"
            else:
                exp = f"{f['property']}.endswith('{f['value']}')"

        elif f["operator"] == OperatorTypes.CONTAINS.value:
            if model_name is None or model_name != "":
                exp = f"{model_name}.{f['property']}.contains('{f['value']}')"
            else:
                exp = f"{f['property']}.contains('{f['value']}')"

        else:
            if type(f['value']) is str:
                if model_name is None or model_name != "":
                    exp = f"{model_name}.{f['property']}{operator}'{f['value']}'"
                else:
                    exp = f"{f['property']}{operator}'{f['value']}'"
            else:
                if model_name is None or model_name != "":
                    exp = f"{model_name}.{f['property']}{operator}{f['value']}"
                else:
                    exp = f"{f['property']}{operator}{f['value']}"

        q = q.filter(eval(exp, globals(), eval_context))
    return q


def __construct_in_clause(f):
    values = f['value']
    in_clause = "["
    vals = []
    for v in values:
        value = "'" + v + "'"
        vals.append(value)
    in_clause += ",".join(vals) + "]"
    return in_clause


class Helpers:
    pass
