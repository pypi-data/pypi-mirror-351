from typing import Any, Optional

from relationalai.early_access.builder import Concept as QBConcept
from relationalai.early_access.builder.builder import python_types_to_concepts, Relationship as QBRelationship
from relationalai.early_access.dsl.orm.relationships import Relationship


class Concept(QBConcept):

    def __init__(self, model, name: str, extends: list[Any] = [], identify_by:dict[str, Any]={}):
        self._dsl_model = model
        # create an orm Relationship for each Concept to be able to refer to them in DSL model
        identify_args = {}
        new_relationships = []
        if identify_by:
            for k, v in identify_by.items():
                if python_types_to_concepts.get(v):
                    v = python_types_to_concepts[v]
                if isinstance(v, Concept):
                    rel = Relationship(self._dsl_model, f"{{{name}}} has {{{k}:{v._name}}}", short_name=k)
                    identify_args[k] = rel
                    new_relationships.append(rel)
                elif isinstance(v, QBRelationship):
                    identify_args[k] = v
                else:
                    raise ValueError(f"identify_by must be either a Concept or Relationship: {k}={v}")
            # add constraints required for reference schema
            self._dsl_model._ref_scheme_constraints(*identify_args.values())
        super().__init__(name, extends, model.qb_model(), identify_args)
        # add new relationships to Model only after Concept instantiation otherwise Relationship's parent will be empty
        for new_rel in new_relationships:
            self._dsl_model._add_relationship(new_rel)

    def identify_by(self, *relations:QBRelationship):
        super().identify_by(*relations)
        self._dsl_model._ref_scheme_constraints(*relations)

    def _is_value_type(self) -> bool:
        if len(self._extends) == 1:
            ext_concept = self._extends[0]
            if ext_concept._is_primitive():
                return True
            else:
                return ext_concept._is_value_type()
        return False

    def __eq__(self, other):
        return isinstance(other, Concept) and self._name == other._name

    def __hash__(self):
        return hash(self._name)


class EntityType(Concept):

    def __init__(self, model, nm, extends: list[Concept] = [], ref_schema_name: Optional[str] = None):
        self._domain = extends
        super().__init__(model, nm, extends)
        self.__ref_schema_name = ref_schema_name

    def _qualified_name(self):
        return self._name

    def _is_composite(self):
        return len(self._domain) > 1

    def _ref_schema_name(self):
        return self.__ref_schema_name

    def _is_value_type(self) -> bool:
        return False


class ValueType(Concept):

    def __init__(self, model, nm, extends: Optional[Any] = None):
        super().__init__(model, nm, [extends] if extends is not None else [])

    def _is_value_type(self) -> bool:
        return True