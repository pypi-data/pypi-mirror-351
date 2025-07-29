"""ClickHouse SQL generation module.

Comprises all the functions which generate SQL code, through the pypika library.
"""

import logging
from typing import Optional, Union

from pypika import functions as fn
from pypika.dialects import ClickHouseQuery, QueryBuilder
from pypika.enums import Order
from pypika.queries import Join, Table
from pypika.terms import Criterion, Field, PyformatParameter

from tesseract_olap.backend import ParamManager
from tesseract_olap.common import shorthash
from tesseract_olap.query import MembersQuery
from tesseract_olap.schema import CubeTraverser, DataType, models

from .dialect import ClickhouseJoinType

logger = logging.getLogger(__name__)


def count_membersquery_sql(query: MembersQuery) -> tuple[QueryBuilder, ParamManager]:
    qb, meta = membersquery_sql(query)
    return ClickHouseQuery.from_(qb).select(fn.Count("*")), meta


def membersquery_sql(query: MembersQuery) -> tuple[QueryBuilder, ParamManager]:
    """Build the query which will list all the members of a Level in a dimension table.

    Depending on the filtering parameters set by the user, this list can also
    be limited by pagination, search terms, or members observed in a fact table.
    """
    meta = ParamManager()

    def _convert_table(
        table: Union[models.Table, models.InlineTable],
        alias: Optional[str],
    ):
        if isinstance(table, models.Table):
            return Table(table.name, schema=table.schema, alias=alias)
        meta.set_table(table)
        return Table(table.name, alias=alias)

    locale = query.locale
    hiefi = query.hiefield

    table_fact = _convert_table(query.cube.table, "tfact")

    table_dim = (
        _convert_table(query.cube.table, "tdim")
        if hiefi.table is None
        else _convert_table(hiefi.table, "tdim")
    )

    ancestor_columns = tuple(
        (alias, column_name)
        for depth, lvlfi in enumerate(hiefi.levels[:-1])
        for alias, column_name in (
            (f"ancestor.{depth}.key", lvlfi.level.key_column),
            (f"ancestor.{depth}.caption", lvlfi.level.get_name_column(locale)),
        )
        if column_name is not None
    )
    level_columns = ancestor_columns + tuple(
        (alias, column_name)
        for alias, column_name in (
            ("key", hiefi.deepest_level.level.key_column),
            ("caption", hiefi.deepest_level.level.get_name_column(locale)),
        )
        if column_name is not None
    )

    level_fields = tuple(
        Field(column_name, alias=alias, table=table_dim) for alias, column_name in level_columns
    )

    subquery = (
        ClickHouseQuery.from_(table_fact)
        .select(table_fact.field(hiefi.foreign_key))
        .distinct()
        .as_("tfact_distinct")
    )

    qb: QueryBuilder = (
        ClickHouseQuery.from_(table_dim)
        .right_join(subquery)
        .on(subquery.field(hiefi.foreign_key) == table_dim.field(hiefi.primary_key))
        .select(*level_fields)
        .distinct()
        .orderby(*level_fields, order=Order.asc)
    )

    limit, offset = query.pagination.as_tuple()
    if limit > 0:
        qb = qb.limit(limit)
    if offset > 0:
        qb = qb.offset(offset)

    if query.search is not None:
        pname = meta.set_param(f"%{query.search}%")
        param = PyformatParameter(pname)
        search_criterion = Criterion.any(
            Field(field).ilike(param)  # type: ignore
            for lvlfield in query.hiefield.levels
            for field in (
                lvlfield.level.key_column if lvlfield.level.key_type == DataType.STRING else None,
                lvlfield.level.get_name_column(locale),
            )
            if field is not None
        )
        qb = qb.where(search_criterion)

    return qb, meta
