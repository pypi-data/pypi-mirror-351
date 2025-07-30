from relationalai.early_access.lqp.validators import assert_valid_input
from relationalai.early_access.lqp.utils import UniqueNames
from relationalai.early_access.metamodel import ir, builtins as rel_builtins, helpers, types
from relationalai.early_access.metamodel.visitor import collect_by_type
from relationalai.early_access.lqp import ir as lqp
from relationalai.early_access.lqp.hash_utils import lqp_hash
from relationalai.early_access.lqp.primitives import relname_to_lqp_name, lqp_operator, lqp_avg_op
from relationalai.early_access.lqp.types import meta_type_to_lqp, type_from_constant
from relationalai.early_access.lqp.constructors import mk_and, mk_exists, mk_or, mk_abstraction

from typing import Tuple, cast, Union

class TranslationCtx:
    def __init__(self, model):
        # TODO: comment these fields
        # TODO: should we have a pass to rename variables instead of this?
        self.unique_names = UniqueNames()
        self.id_to_orig_name = {}
        self.output_ids = []

""" Main access point. Converts the model IR to an LQP program. """
def to_lqp(model: ir.Model) -> lqp.LqpProgram:
    assert_valid_input(model)
    ctx = TranslationCtx(model)
    program = _translate_to_program(ctx, model)
    return program

def _translate_to_program(ctx: TranslationCtx, model: ir.Model) -> lqp.LqpProgram:
    decls: list[lqp.Declaration] = []
    outputs: list[Tuple[str, lqp.RelationId]] = []

    # LQP only accepts logical tasks
    # These are asserted at init time
    root = cast(ir.Logical, model.root)

    seen_rids = set()
    for subtask in root.body:
        assert isinstance(subtask, ir.Logical)
        new_decls = _translate_to_decls(ctx, subtask)
        for decl in new_decls:
            assert isinstance(decl, lqp.Def), f"expected Def, got {type(decl)}: {decl}"
            rid = decl.name
            assert rid not in seen_rids, f"duplicate relation id: {rid}"
            seen_rids.add(rid)

            decls.append(decl)

    for output_id in ctx.output_ids:
        assert isinstance(output_id, lqp.RelationId)
        outputs.append(("output", output_id))

    debug_info = lqp.DebugInfo(id_to_orig_name=ctx.id_to_orig_name)

    return lqp.LqpProgram(defs=decls, outputs=outputs, debug_info=debug_info)

def _effect_bindings(effect: Union[ir.Output, ir.Update]) -> list[ir.Value]:
    if isinstance(effect, ir.Output):
        # Unions may not return anything. The generated IR contains a None value when this
        # happens. We ignore it here.
        # TODO: Improve handling of empty union outputs
        # TODO: we dont yet handle aliases, so we ignore v[0]
        return [v[1] for v in effect.aliases if v[1] is not None]
    else:
        return list(effect.args)

def _translate_to_decls(ctx: TranslationCtx, rule: ir.Logical) -> list[lqp.Declaration]:
    effects = collect_by_type((ir.Output, ir.Update), rule)
    aggregates = collect_by_type(ir.Aggregate, rule)

    # TODO: should this ever actually come in as input?
    if len(effects) == 0:
        return []

    conjuncts = []
    for task in rule.body:
        if isinstance(task, (ir.Output, ir.Update)):
            continue
        conjuncts.append(_translate_to_formula(ctx, task))

    # Aggregates reduce over the body
    if len(aggregates) > 0:
        aggr_body = mk_and(conjuncts)
        conjuncts = []
        for aggr in aggregates:
            conjuncts.append(_translate_aggregate(ctx, aggr, aggr_body))

    return [_translate_effect(ctx, effect, mk_and(conjuncts)) for effect in effects]

def _translate_effect(ctx: TranslationCtx, effect: Union[ir.Output, ir.Update], body: lqp.Formula) -> lqp.Declaration:
    # Handle the bindings
    bindings = _effect_bindings(effect)
    projection, eqs = translate_bindings(ctx, bindings)
    eqs.append(body)
    new_body = mk_and(eqs)

    is_output = isinstance(effect, ir.Output)
    def_name = "output" if is_output else effect.relation.name
    meta_id = effect.id if is_output else effect.relation.id
    rel_id = get_relation_id(ctx, def_name, meta_id)

    # Context bookkeeping
    if is_output:
        ctx.output_ids.append(rel_id)

    # TODO: is this correct? might need attrs tooo?
    return lqp.Def(
        name = rel_id,
        body = mk_abstraction(projection, new_body),
        attrs = [],
        meta = None,
    )

def _translate_aggregate(ctx: TranslationCtx, aggr: ir.Aggregate, body: lqp.Formula) -> Union[lqp.Reduce, lqp.Formula]:
    # TODO: handle this properly
    aggr_name = aggr.aggregation.name
    supported_aggrs = ("sum", "count", "avg", "min", "max")
    assert aggr_name in supported_aggrs, f"only support {supported_aggrs} for now, not {aggr.aggregation.name}"

    # TODO: This is not right, we need to handle input args and output args properly
    # Last one is output arg, the rest are input args
    input_args = [_translate_term(ctx, arg) for arg in aggr.args[:-1]]
    output_var, _ = _translate_term(ctx, aggr.args[-1])

    projected_args = [_translate_term(ctx, var) for var in aggr.projection]
    abstr_args = []
    abstr_args.extend(projected_args)
    abstr_args.extend(input_args)
    if aggr_name == "count" or aggr_name == "avg":
        # Count sums up "1"
        one_var, typ, eq = binding_to_lqp_var(ctx, 1)
        assert eq is not None
        body = mk_and([body, eq])
        abstr_args.append([one_var, typ])

    # Average needs to wrap the reduce in Exists(Conjunction(Reduce, div))
    if aggr_name == "avg":
        # The average will produce two output variables: sum and count.
        sum_result = lqp.Var(name=ctx.unique_names.get_name("sum"), meta=None)
        count_result = lqp.Var(name=ctx.unique_names.get_name("count"), meta=None)

        # Second to last is the variable we're summing over.
        (sum_var, sum_type) = abstr_args[-2]
        sum_name = sum_var.name if sum_var.name else "sum"

        result = lqp.Reduce(
            op=lqp_avg_op(ctx.unique_names, aggr.aggregation, sum_name, sum_type),
            body=mk_abstraction(abstr_args, body),
            terms=[sum_result, count_result],
            meta=None,
        )

        div = lqp.Primitive(name="rel_primitive_divide", terms=[sum_result, count_result, output_var], meta=None)
        conjunction = mk_and([result, div])

        # Finally, we need to wrap everything in an `exists` to project away the sum and
        # count variables and only keep the result of the division.
        result = mk_exists([(sum_result, sum_type), (count_result, lqp.PrimitiveType.INT)], conjunction)

        return result

    # `input_args`` hold the types of the input arguments, but they may have been modified
    # if we're dealing with a count, so we use `abstr_args` to find the type.
    (aggr_arg, aggr_arg_type) = abstr_args[-1]
    # TODO: Can name ever be blank? Should we handle primitive values here?
    aggr_arg_name = aggr_arg.name if aggr_arg.name else "agg"
    # Group-bys do not need to be handled at all, since they are introduced outside already
    reduce = lqp.Reduce(
        op=lqp_operator(ctx.unique_names, aggr.aggregation, aggr_arg_name, aggr_arg_type),
        body=mk_abstraction(abstr_args, body),
        terms=[output_var],
        meta=None
    )
    return reduce

def _translate_to_formula(ctx: TranslationCtx, task: ir.Task) -> lqp.Formula:
    if isinstance(task, ir.Logical):
        conjuncts = [_translate_to_formula(ctx, child) for child in task.body]
        return mk_and(conjuncts)
    elif isinstance(task, ir.Lookup):
        return _translate_to_atom(ctx, task)
    elif isinstance(task, ir.Not):
        return lqp.Not(arg=_translate_to_formula(ctx, task.task), meta=None)
    elif isinstance(task, ir.Exists):
        lqp_vars, conjuncts = translate_bindings(ctx, list(task.vars))
        conjuncts.append(_translate_to_formula(ctx, task.task))
        return mk_exists(lqp_vars, mk_and(conjuncts))
    elif isinstance(task, ir.Construct):
        assert len(task.values) >= 1, "construct should have at least one value"
        # TODO: what does the first value do
        terms = [_translate_term(ctx, arg) for arg in task.values[1:]]
        terms.append(_translate_term(ctx, task.id_var))
        return lqp.Primitive(
            name="rel_primitive_hash_tuple_uint128",
            terms=[v for v, _ in terms],
            meta=None
        )
    elif isinstance(task, ir.Union):
        # TODO: handle hoisted vars if needed
        disjs = [_translate_to_formula(ctx, child) for child in task.tasks]
        return mk_or(disjs)
    elif isinstance(task, ir.Aggregate):
        # Nothing to do here, handled in _translate_to_decls
        return mk_and([])
    else:
        raise NotImplementedError(f"Unknown task type (formula): {type(task)}")

def _translate_term(ctx: TranslationCtx, value: ir.Value) -> Tuple[lqp.Term, lqp.RelType]:
    if isinstance(value, ir.Var):
        name = ctx.unique_names.get_name_by_id(value.id, value.name)
        t = meta_type_to_lqp(value.type)
        return lqp.var(name), t
    elif isinstance(value, ir.Literal):
        return _translate_term(ctx, value.value)
    else:
        assert isinstance(value, lqp.PrimitiveValue), \
            f"Cannot translate value {value!r} of type {type(value)} to LQP Term; not a PrimitiveValue."
        return value, type_from_constant(value)

# In the metamodel, type conversions are represented as special relations, whereas in LQP we
# have a dedicated `Cast` node. Eventually we might want to unify these, but for now we use
# this mapping here.
rel_to_cast = {
    "int_to_float": lqp.PrimitiveType.FLOAT,
    "int_to_decimal": lqp.RelValueType.DECIMAL,
    "decimal_to_float": lqp.PrimitiveType.FLOAT,
}

def _translate_to_atom(ctx: TranslationCtx, task: ir.Lookup) -> lqp.Formula:
    # TODO: want signature not name
    rel_name = task.relation.name
    terms = []
    for arg in task.args:
        if isinstance(arg, ir.PyValue):
            assert isinstance(arg, lqp.PrimitiveValue)
            term = arg
            terms.append(term)
            continue
        elif isinstance(arg, ir.Literal):
            if arg.type == types.Symbol:
                assert isinstance(arg.value, str)
                terms.append(lqp.Specialized(value=arg.value, meta=None))
                continue
            else:
                assert isinstance(arg.value, lqp.PrimitiveValue)
                term = arg.value
                terms.append(term)
                continue
        # TODO is this redundant?
        assert isinstance(arg, ir.Var), f"expected var, got {type(arg)}: {arg}"
        term, _t = _translate_term(ctx, arg)
        terms.append(term)

    if rel_builtins.is_builtin(task.relation):
        if task.relation.name in rel_to_cast:
            assert len(terms) == 2, f"expected two terms for cast {task.relation.name}, got {terms}"
            return lqp.Cast(type=rel_to_cast[task.relation.name], input=terms[0], result=terms[1], meta=None)
        else:
            lqp_name = relname_to_lqp_name(task.relation.name)
            return lqp.Primitive(name=lqp_name, terms=terms, meta=None)

    if helpers.is_external(task.relation):
        return lqp.RelAtom(name=task.relation.name, terms=terms, meta=None)

    rid = get_relation_id(ctx, rel_name, task.relation.id)
    return lqp.Atom(name=rid, terms=terms, meta=None)

def get_relation_id(ctx: TranslationCtx, orig_name: str, metamodel_id: int) -> lqp.RelationId:
    mid_str = str(metamodel_id)
    relation_id = lqp.RelationId(id=lqp_hash(mid_str), meta=None)
    ctx.id_to_orig_name[relation_id] = orig_name
    return relation_id

def translate_bindings(ctx: TranslationCtx, bindings: list[ir.Value]) -> Tuple[list[Tuple[lqp.Var, lqp.RelType]], list[lqp.Formula]]:
    lqp_vars = []
    conjuncts = []
    for binding in bindings:
        lqp_var, typ, eq = binding_to_lqp_var(ctx, binding)
        lqp_vars.append((lqp_var, typ))
        if eq is not None:
            conjuncts.append(eq)

    return lqp_vars, conjuncts

def binding_to_lqp_var(ctx: TranslationCtx, binding: ir.Value) -> Tuple[lqp.Var, lqp.RelType, Union[None, lqp.Formula]]:
    if isinstance(binding, ir.Var):
        var, typ = _translate_term(ctx, binding)
        assert isinstance(var, lqp.Var)
        return var, typ, None
    else:
        # Constant in this case
        assert isinstance(binding, lqp.PrimitiveValue), f"expected primitive value, got {type(binding)}: {binding}"
        value, typ = _translate_term(ctx, binding)

        var_name = ctx.unique_names.get_name("cvar")
        var = lqp.var(var_name)
        eq = lqp.Primitive(name="rel_primitive_eq", terms=[var, value], meta=None)
        return var, typ, eq
