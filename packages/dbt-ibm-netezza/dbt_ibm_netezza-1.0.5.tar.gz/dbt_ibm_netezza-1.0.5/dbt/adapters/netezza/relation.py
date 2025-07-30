from dataclasses import dataclass, field
from typing import Optional, Type, TypeVar
from dbt.adapters.base.relation import BaseRelation, Policy, Path, InformationSchema
from dbt.adapters.contracts.relation import ComponentName, RelationType

@dataclass
class NetezzaPath(Path):
    def get_part(self, key: ComponentName) -> Optional[str]:
        if key == ComponentName.Database:
            if self.database is None:
                return self.database
            return self.database.replace('"', "")
        elif key == ComponentName.Schema:
            if self.schema is None:
                return None
            return self.schema
        elif key == ComponentName.Identifier:
            if self.identifier is None:
                return None
            return self.identifier
        else:
            raise ValueError(
                "Got a key of {}, expected one of {}".format(key, list(ComponentName))
            )

@dataclass
class NetezzaQuotePolicy(Policy):
    database: bool = True
    schema: bool = True
    identifier: bool = True


@dataclass(frozen=True, eq=False, repr=False)
class NetezzaRelation(BaseRelation):
    path: NetezzaPath
    quote_policy: Policy = field(default_factory=lambda: NetezzaQuotePolicy())

    def _is_exactish_match(self, field: ComponentName, value: str) -> bool:
        # Remove requirement for dbt_created due to dbt bug with cache preservation
        # of that property
        if self.quote_policy.get_part(field) is False:
            return self.path.get_lowered_part(field) == value.lower()
        else:
            return self.path.get_part(field) == value.replace('"', "")

    @staticmethod
    def add_ephemeral_prefix(name: str):
        # Netezza reserves '_' name prefix for system catalogs
        return f"dbt__cte__{name}"

    def information_schema(self, view_name=None) -> "NetezzaInformationSchema":
        # some of our data comes from jinja, where things can be `Undefined`.
        if not isinstance(view_name, str):
            view_name = None

        # Kick the user-supplied schema out of the information schema relation
        # Instead address this as <database>.information_schema by default
        info_schema = NetezzaInformationSchema.from_relation(self, view_name)
        return info_schema.incorporate(path={"schema": None})

Info = TypeVar("Info", bound="NetezzaInformationSchema")

class NetezzaInformationSchema(InformationSchema):
    @classmethod
    def get_path(cls, relation: NetezzaRelation, information_schema_view: Optional[str]) -> NetezzaPath:
        return Path(
            database=relation.database.replace('"', ""),
            schema=relation.schema,
            identifier="INFORMATION_SCHEMA",
        )

    @classmethod
    def from_relation(
        cls: Type[Info],
        relation: NetezzaRelation,
        information_schema_view: Optional[str],
    ) -> Info:
        include_policy = cls.get_include_policy(relation, information_schema_view)
        quote_policy = cls.get_quote_policy(relation, information_schema_view)
        path = cls.get_path(relation, information_schema_view)
        return cls(
            type=RelationType.View,
            path=path,
            include_policy=include_policy,
            quote_policy=quote_policy,
            information_schema_view=information_schema_view,
        )
