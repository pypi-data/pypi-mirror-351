from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel import ir, builtins as rel_builtins, factory as f, visitor
from relationalai.early_access.metamodel.typer.typer2 import InferTypes
from typing import cast, Tuple, Union
from relationalai.early_access.metamodel.util import NameCache
from relationalai.early_access.metamodel import types

from relationalai.early_access.metamodel.rewrite import Splinter, GarbageCollectNodes

# TODO: Move this into metamodel.rewrite
from relationalai.early_access.rel.rewrite import Flatten, QuantifyVars, ExtractCommon, CDC

import datetime

def lqp_passes() -> list[Pass]:
    # TODO: are these all needed from the Rel emitter?
    # TODO: should there be a pass to remove aliases from output?
    return [
        InferTypes(),
        GarbageCollectNodes(),
        CDC(),
        ExtractCommon(),
        Flatten(),
        QuantifyVars(),
        Splinter(), # Adds missing existentials + splits multi-headed rules into single rules
        NormalizeAggregates(),
        HoistAggregates(),
        UnifyDefinitions(),
        EliminateValueTypeConstants(),
    ]

# TODO: assert theres no nested nested nested aggregates
# TODO: assert theres only one aggregate per rule
# TODO: is this correct?
# Move aggregates to the same level as updates (i.e. top-level logical)
class HoistAggregates(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        root = cast(ir.Logical, model.root)
        new_subtasks = []
        for subtask in root.body:
            subtask = cast(ir.Logical, subtask)
            new_subsubtasks = []
            for subsubtask in subtask.body:
                if not isinstance(subsubtask, ir.Logical):
                    new_subsubtasks.append(subsubtask)
                    continue

                subsubtask = cast(ir.Logical, subsubtask)
                if self.has_aggregate(subsubtask):
                    new_subsubtask, aggrs = self._hoist_aggregates(subsubtask)
                    new_subsubtasks.append(new_subsubtask)
                    new_subsubtasks.extend(aggrs)
                else:
                    new_subsubtasks.append(subsubtask)

            new_subtask = ir.Logical(
                    subtask.engine,
                    subtask.hoisted,
                    tuple(new_subsubtasks),
                )
            new_subtasks.append(new_subtask)

        new_root = ir.Logical(root.engine, root.hoisted, tuple(new_subtasks))
        model = ir.Model(
            model.engines,
            model.relations,
            model.types,
            new_root,
        )
        return model

    def has_aggregate(self, task: ir.Task) -> bool:
        assert isinstance(task, ir.Logical)
        for subtask in task.body:
            if isinstance(subtask, ir.Aggregate):
                return True
        return False

    def _hoist_aggregates(self, task: ir.Task) -> Tuple[ir.Task, list[ir.Aggregate]]:
        assert isinstance(task, ir.Logical)
        aggrs = []
        new_subtasks = []
        for subtask in task.body:
            if isinstance(subtask, ir.Aggregate):
                aggrs.append(subtask)
            else:
                new_subtasks.append(subtask)
        assert len(aggrs) > 0, "should have found an aggregate"
        return (ir.Logical(
            task.engine,
            task.hoisted,
            tuple(new_subtasks),
        ), aggrs)

# Rewrites aggregates when necessary e.g. avg -> sum/count
class NormalizeAggregates(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        self.var_name_cache: NameCache = NameCache()
        root = cast(ir.Logical, model.root)
        new_subtasks = []
        for subtask in root.body:
            subtask = cast(ir.Logical, subtask)
            if self.has_aggregate(subtask):
                new_subtask = self._rewrite_subtask(subtask)
                new_subtasks.append(new_subtask)
            else:
                new_subtasks.append(subtask)
        new_root = ir.Logical(root.engine, root.hoisted, tuple(new_subtasks))
        model = ir.Model(
            model.engines,
            model.relations,
            model.types,
            new_root,
        )
        return model

    def _rewrite_subtask(self, task: ir.Task) -> ir.Task:
        assert isinstance(task, ir.Logical)
        new_subtasks = []
        for subtask in task.body:
            if isinstance(subtask, ir.Aggregate):
                assert isinstance(subtask, ir.Aggregate)
                if subtask.aggregation.name == "sum":
                    new_subtasks.append(subtask)
                elif subtask.aggregation.name == "count":
                    new_subtasks.append(subtask)
                elif subtask.aggregation.name == "avg":
                    new_subtasks.append(subtask)
                elif subtask.aggregation.name == "max":
                    new_subtasks.append(subtask)
                elif subtask.aggregation.name == "min":
                    new_subtasks.append(subtask)
                else:
                    raise NotImplementedError(f"Unsupported aggregate: {subtask.aggregation.name}")
            else:
                new_subtasks.append(subtask)

        return ir.Logical(
            task.engine,
            task.hoisted,
            tuple(new_subtasks),
        )

    def has_aggregate(self, task: ir.Task) -> bool:
        assert isinstance(task, ir.Logical)
        for subtask in task.body:
            if isinstance(subtask, ir.Aggregate):
                return True
        return False

class UnifyDefinitions(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        multidef_relations = self.get_multidef_relations(model)
        for relation in multidef_relations:
            model = self.rename_multidef(model, relation)
        return model

    def get_multidef_relations(self, model: ir.Model) -> set[ir.Relation]:
        seen = set()
        result = set()
        root = cast(ir.Logical, model.root)
        for task in root.body:
            task = cast(ir.Logical, task)
            for subtask in task.body:
                if isinstance(subtask, ir.Output):
                    name = "output"
                    if name in seen:
                        raise NotImplementedError("multiple outputs not supported yet")
                    seen.add(name)
                elif isinstance(subtask, ir.Update):
                    assert subtask.effect == ir.Effect.derive, "only derive updates supported yet"
                    name = subtask.relation
                    if name in seen:
                        result.add(name)
                    seen.add(name)
        return result

    def rename_multidef(self, model: ir.Model, relation: ir.Relation) -> ir.Model:
        defname = relation.name
        root = cast(ir.Logical, model.root)
        new_subtasks = []
        new_relations = []
        total_ct = 0
        for subtask in root.body:
            subtask = cast(ir.Logical, subtask)
            new_subsubtasks = []
            for subsubtask in subtask.body:
                if isinstance(subsubtask, ir.Update):
                    assert subsubtask.effect == ir.Effect.derive, "only derive updates supported yet"
                    name = subsubtask.relation
                    if name == relation:
                        total_ct += 1
                        # TODO: this needs to be unique btw (gensym)
                        new_name = f"{defname}_{total_ct}"
                        new_subsubtask = self.rename_relation(subsubtask, new_name)
                        new_subsubtasks.append(new_subsubtask)
                        new_relation = ir.Relation(
                            new_name,
                            relation.fields,
                            relation.requires,
                        )
                        new_relations.append(new_relation)
                    else:
                        new_subsubtasks.append(subsubtask)
                else:
                    new_subsubtasks.append(subsubtask)

            new_subtask = ir.Logical(
                subtask.engine,
                subtask.hoisted,
                tuple(new_subsubtasks),
            )
            new_subtasks.append(new_subtask)
        assert total_ct > 0, f"should have found at least one definition for {defname}"

        args = []
        for field in relation.fields:
            args.append(ir.Var(field.type, field.name))

        # Also add the new definition
        final_relation = ir.Relation(
            defname,
            relation.fields,
            relation.requires,
        )
        new_update = ir.Update(
            root.engine,
            final_relation,
            tuple(args),
            ir.Effect.derive,
        )

        logical_tasks = []
        lookups = []
        for new_relation in new_relations:
            new_lookup = ir.Lookup(
                root.engine,
                new_relation,
                tuple(args),
            )
            lookups.append(new_lookup)

        disj = ir.Union(
            root.engine,
            tuple(),
            tuple(lookups),
        )
        logical_tasks.append(disj)
        logical_tasks.append(new_update)
        new_logical = ir.Logical(
            root.engine,
            root.hoisted,
            tuple(logical_tasks),
        )
        new_subtasks.append(new_logical)

        new_root = ir.Logical(root.engine, root.hoisted, tuple(new_subtasks))
        model = ir.Model(
            model.engines,
            model.relations | new_relations,
            model.types,
            new_root,
        )
        return model

    def rename_relation(self, task: ir.Update, new_name: str) -> ir.Update:
        assert isinstance(task, ir.Update)
        assert task.effect == ir.Effect.derive, "only derive updates supported yet"
        old_relation = task.relation
        new_relation = ir.Relation(
            new_name,
            old_relation.fields,
            old_relation.requires,
        )
        new_task = ir.Update(
            task.engine,
            new_relation,
            task.args,
            task.effect,
        )
        return new_task

# We don't have a proto representation for these, so we rewrite them to be constructed directly
class EliminateValueTypeConstants(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        p = RewriteBadLiterals()
        return p.walk(model)

class RewriteBadLiterals(visitor.DeprecatedPass):
    def handle_lookup(self, node: ir.Lookup, parent: ir.Node) -> Union[ir.Lookup, ir.Exists]:
        args = node.args
        vars_to_existify = []
        new_conjs = []
        new_args = []
        for arg in args:
            if isinstance(arg, datetime.datetime):
                new_var = f.var("dt_var", types.DateTime)
                new_args.append(new_var)
                vars_to_existify.append(new_var)

                year = arg.year
                month = arg.month
                day = arg.day
                hour = arg.hour
                minute = arg.minute
                second = arg.second

                lookup = f.lookup(
                        rel_builtins.construct_datetime,
                        tuple([
                            f.literal(year),
                            f.literal(month),
                            f.literal(day),
                            f.literal(hour),
                            f.literal(minute),
                            f.literal(second),
                            new_var,
                        ])
                    )
                new_conjs.append(lookup)
            elif isinstance(arg, datetime.date):
                new_var = f.var("dt_var", types.Date)
                new_args.append(new_var)
                vars_to_existify.append(new_var)

                year = arg.year
                month = arg.month
                day = arg.day

                lookup = f.lookup(
                        rel_builtins.construct_date,
                        tuple([
                            f.literal(year),
                            f.literal(month),
                            f.literal(day),
                            new_var,
                        ])
                    )
                new_conjs.append(lookup)
            else:
                new_args.append(arg)

        if len(vars_to_existify) == 0:
            return node

        new_lookup = f.lookup(
            node.relation,
            tuple(new_args),
        )
        new_conjs.append(new_lookup)

        result = f.exists(
            vars_to_existify,
            f.logical(tuple(new_conjs)),
        )

        return result
