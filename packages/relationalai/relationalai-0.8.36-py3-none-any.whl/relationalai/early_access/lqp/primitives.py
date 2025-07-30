from relationalai.early_access.lqp import ir as lqp
from relationalai.early_access.lqp.utils import UniqueNames
from relationalai.early_access.metamodel import ir

rel_to_lqp = {
    "+": "rel_primitive_add",
    "-": "rel_primitive_subtract",
    "*": "rel_primitive_multiply",
    "/": "rel_primitive_divide",
    "=": "rel_primitive_eq",
    "!=": "rel_primitive_neq",
    "<=": "rel_primitive_lt_eq",
    ">=": "rel_primitive_gt_eq",
    ">": "rel_primitive_gt",
    "<": "rel_primitive_lt",
    "abs": "rel_primitive_abs",
    "construct_date": "rel_primitive_construct_date",
    "construct_datetime": "rel_primitive_construct_datetime",
    "starts_with": "rel_primitive_starts_with",
    "ends_with": "rel_primitive_ends_with",
    "contains": "rel_primitive_contains",
    "num_chars": "rel_primitive_num_chars",
    "substring": "rel_primitive_substring",
    "like_match": "rel_primitive_like_match",
    "concat": "rel_primitive_concat",
    "replace": "rel_primitive_replace",
    "date_year": "rel_primitive_date_year",
    "date_month": "rel_primitive_date_month",
    "date_day": "rel_primitive_date_day",
    # TODO: these don't exist in Rel
    "decimal_to_float": "rel_primitive_decimal_to_float_fake",
    "int_to_float": "rel_primitive_int_to_decimal_fake",
}

def relname_to_lqp_name(name: str) -> str:
    # TODO: do these proprly
    if name in rel_to_lqp:
        return rel_to_lqp[name]
    else:
        raise NotImplementedError(f"missing primitive case: {name}")

def lqp_sum_op(names: UniqueNames, aggr_arg_name: str, aggr_arg_type:lqp.RelType) -> lqp.Abstraction:
    x = lqp.Var(name=names.get_name(f"x_{aggr_arg_name}"), meta=None)
    y = lqp.Var(name=names.get_name(f"y_{aggr_arg_name}"), meta=None)
    z = lqp.Var(name=names.get_name(f"z_{aggr_arg_name}"), meta=None)
    ts = [(x, aggr_arg_type), (y, aggr_arg_type), (z, aggr_arg_type)]
    body = lqp.Primitive(name="rel_primitive_add", terms=[x, y, z], meta=None)
    return lqp.Abstraction(vars=ts, value=body, meta=None)

# We take the name and type of the variable that we're summing over, so that we can generate
# recognizable names for the variables in the reduce operation and preserve the type.
def lqp_avg_op(names: UniqueNames, op: ir.Relation, sum_name: str, sum_type: lqp.RelType) -> lqp.Abstraction:
    count_type = lqp.PrimitiveType.INT
    vars = [
        (lqp.Var(name=names.get_name(sum_name), meta=None), sum_type),
        (lqp.Var(name=names.get_name("counter"), meta=None), count_type),
        (lqp.Var(name=names.get_name(sum_name), meta=None), sum_type),
        (lqp.Var(name=names.get_name("one"), meta=None), count_type),
        (lqp.Var(name=names.get_name("sum"), meta=None), sum_type),
        (lqp.Var(name=names.get_name("count"), meta=None), count_type),
    ]

    x1 = vars[0][0]
    x2 = vars[1][0]
    y1 = vars[2][0]
    y2 = vars[3][0]
    sum = vars[4][0]
    count = vars[5][0]

    body = lqp.Conjunction(
        args=[
            lqp.Primitive(name="rel_primitive_add", terms=[x1, y1, sum], meta=None),
            lqp.Primitive(name="rel_primitive_add", terms=[x2, y2, count], meta=None)
        ],
        meta=None
    )
    return lqp.Abstraction(vars=vars, value=body, meta=None)

def lqp_max_op(names: UniqueNames, aggr_arg_name: str, aggr_arg_type:lqp.RelType) -> lqp.Abstraction:
    x = lqp.Var(name=names.get_name(f"x_{aggr_arg_name}"), meta=None)
    y = lqp.Var(name=names.get_name(f"y_{aggr_arg_name}"), meta=None)
    z = lqp.Var(name=names.get_name(f"z_{aggr_arg_name}"), meta=None)
    ts = [(x, aggr_arg_type), (y, aggr_arg_type), (z, aggr_arg_type)]

    body = lqp.Primitive(name="rel_primitive_max", terms=[x, y, z], meta=None)
    return lqp.Abstraction(vars=ts, value=body, meta=None)

def lqp_min_op(names: UniqueNames, aggr_arg_name: str, aggr_arg_type:lqp.RelType) -> lqp.Abstraction:
    x = lqp.Var(name=names.get_name(f"x_{aggr_arg_name}"), meta=None)
    y = lqp.Var(name=names.get_name(f"y_{aggr_arg_name}"), meta=None)
    z = lqp.Var(name=names.get_name(f"z_{aggr_arg_name}"), meta=None)
    ts = [(x, aggr_arg_type), (y, aggr_arg_type), (z, aggr_arg_type)]

    body = lqp.Primitive(name="rel_primitive_min", terms=[x, y, z], meta=None)
    return lqp.Abstraction(vars=ts, value=body, meta=None)

def lqp_operator(names: UniqueNames, op: ir.Relation, aggr_arg_name: str, aggr_arg_type: lqp.RelType) -> lqp.Abstraction:
    if op.name == "sum":
        return lqp_sum_op(names, aggr_arg_name, aggr_arg_type)
    elif op.name == "count":
        return lqp_sum_op(names, aggr_arg_name, aggr_arg_type)
    elif op.name == "max":
        return lqp_max_op(names, aggr_arg_name, aggr_arg_type)
    elif op.name == "min":
        return lqp_min_op(names, aggr_arg_name, aggr_arg_type)
    else:
        raise NotImplementedError(f"Unsupported aggregation: {op.name}")
