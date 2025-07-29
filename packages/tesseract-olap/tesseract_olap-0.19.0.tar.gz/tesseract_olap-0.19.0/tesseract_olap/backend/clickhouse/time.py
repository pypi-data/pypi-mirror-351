from typing import Optional

from pypika.functions import Count, Function, Max
from pypika.queries import Selectable
from pypika.terms import Criterion, Field, Term
from typing_extensions import Literal

from tesseract_olap.exceptions.query import TimeScaleUnavailable
from tesseract_olap.query import (
    DataQuery,
    HierarchyField,
    LevelField,
    Restriction,
    TimeConstraint,
    TimeScale,
)

from .dialect import ClickHouseQuery, ToYYYYMMDD


def _find_timerestriction(
    query: DataQuery,
) -> Optional[tuple[HierarchyField, LevelField, TimeConstraint]]:
    """Return the TimeRestriction object in a query, if defined."""
    gen_restriction = (
        (hiefi, lvlfi, lvlfi.time_restriction.constraint)
        for hiefi in query.fields_qualitative
        for lvlfi in hiefi.levels
        if lvlfi.time_restriction is not None
    )
    return next(gen_restriction, None)


SQL_for_continuous_dates = """
WITH date_range AS (
    SELECT toDate('2023-01-01') + number AS date
    FROM numbers(365)  -- Adjust the range as needed
)
SELECT 
    date_range.date,
    sum(transactions.amount) AS total_amount
FROM date_range
LEFT JOIN transactions ON date_range.date = toDate(transactions.date)
GROUP BY date_range.date
ORDER BY date_range.date
"""

SQL_for_highest_complete_year = """
SELECT
    toYear(date) AS year,
    sum(value) AS total_value
FROM transactions
WHERE toYear(date) < (
    SELECT max(toYear(date))
    FROM transactions
    GROUP BY toYear(date)
    HAVING count(distinct toMonth(date)) = 12
)
GROUP BY year
ORDER BY year
"""


def qb_timerel_yyyymmdd(
    query: DataQuery,
    tfrom: Selectable,
    hiefi: HierarchyField,
    lvlfi: LevelField,
    constr: tuple[Literal[Restriction.LEADING, Restriction.TRAILING], int],
) -> Criterion:
    """Create a Criterion for LEADING/TRAILING restrictions on YYYYMMDD columns."""
    fkey_column = hiefi.deepest_level.id_column(query.locale)
    field_name = f"lv_{fkey_column.hash}" if not hiefi.table else f"fk_{hiefi.alias}"
    field_fkey = tfrom.field(field_name)

    direction, amount = constr
    qb_limit = ClickHouseQuery.from_(tfrom)
    dir_function = "max" if direction is Restriction.TRAILING else "min"
    field_limit = Function("YYYYMMDDToDate", Function(dir_function, field_fkey))
    time_scale = lvlfi.time_scale

    if time_scale is TimeScale.YEAR:
        field_limit = Function("toStartOfYear", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractYears", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addYears", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    if time_scale is TimeScale.QUARTER:
        field_limit = Function("toStartOfQuarter", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractQuarters", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addQuarters", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    if time_scale is TimeScale.MONTH:
        field_limit = Function("toStartOfMonth", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractMonths", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addMonths", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    if time_scale is TimeScale.WEEK:
        field_limit = Function("toStartOfWeek", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractWeeks", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addWeeks", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    if time_scale is TimeScale.DAY:
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractDays", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(field_since)

        field_until = ToYYYYMMDD(Function("addDays", field_limit, amount))
        return field_fkey < qb_limit.select(field_until)

    raise TimeScaleUnavailable(query.cube.name, time_scale.value)


def qb_timerel_yyyymm(
    query: DataQuery,
    tfrom: Selectable,
    hiefi: HierarchyField,
    lvlfi: LevelField,
    constr: tuple[Literal[Restriction.LEADING, Restriction.TRAILING], int],
) -> Criterion:
    """Create a Criterion for LEADING/TRAILING restrictions on YYYYMM columns."""
    fkey_column = hiefi.deepest_level.id_column(query.locale)
    field_name = f"lv_{fkey_column.hash}" if not hiefi.table else f"fk_{hiefi.alias}"
    field_fkey = tfrom.field(field_name)

    direction, amount = constr
    qb_limit = ClickHouseQuery.from_(tfrom)
    dir_function = "max" if constr[0] is Restriction.TRAILING else "min"
    field_limit = Function("YYYYMMDDToDate", Function(dir_function, field_fkey) * 100 + 1)
    time_scale = lvlfi.time_scale

    if time_scale is TimeScale.YEAR:
        field_limit = Function("toStartOfYear", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractYears", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(Function("intDiv", field_since, 100))

        field_until = ToYYYYMMDD(Function("addYears", field_limit, amount))
        return field_fkey < qb_limit.select(Function("intDiv", field_until, 100))

    if time_scale is TimeScale.QUARTER:
        field_limit = Function("toStartOfQuarter", field_limit)
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractQuarters", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(Function("intDiv", field_since, 100))

        field_until = ToYYYYMMDD(Function("addQuarters", field_limit, amount))
        return field_fkey < qb_limit.select(Function("intDiv", field_until, 100))

    if time_scale is TimeScale.MONTH:
        if direction is Restriction.TRAILING:
            field_since = ToYYYYMMDD(Function("subtractMonths", field_limit, amount - 1))
            return field_fkey >= qb_limit.select(Function("intDiv", field_since, 100))

        field_until = ToYYYYMMDD(Function("addMonths", field_limit, amount))
        return field_fkey < qb_limit.select(Function("intDiv", field_until, 100))

    raise TimeScaleUnavailable(query.cube.name, time_scale.value)


def qb_timerel_yyyy(
    query: DataQuery,
    tfrom: Selectable,
    hiefi: HierarchyField,
    lvlfi: LevelField,
    constr: tuple[Literal[Restriction.LEADING, Restriction.TRAILING], int],
) -> Criterion:
    """Create a Criterion for LEADING/TRAILING restrictions on YYYY columns."""
    fkey_column = hiefi.deepest_level.id_column(query.locale)
    field_name = f"lv_{fkey_column.hash}" if not hiefi.table else f"fk_{hiefi.alias}"
    field_fkey = tfrom.field(field_name)

    direction, amount = constr
    qb_limit = ClickHouseQuery.from_(tfrom)
    dir_function = "max" if constr[0] is Restriction.TRAILING else "min"
    field_limit = Function(dir_function, field_fkey)
    time_scale = lvlfi.time_scale

    if time_scale is TimeScale.YEAR:
        if direction is Restriction.TRAILING:
            field_since = field_limit - (amount - 1)
            return field_fkey >= qb_limit.select(field_since)

        field_until = field_limit + amount
        return field_fkey < qb_limit.select(field_until)

    raise TimeScaleUnavailable(query.cube.name, time_scale.name)


def _qb_trailing_full(query: DataQuery, tfrom: Selectable) -> tuple[Criterion, list[Term]]:
    result = _find_timerestriction(query)
    if not result:
        raise ValueError

    hiefi, lvlfi, restr = result
    field_fkey = tfrom.field(hiefi.foreign_key)
    fkey_type = hiefi.dimension.fkey_time_format

    if fkey_type == "YYYYMMDD":
        field_date = Function("YYYYMMDDToDate", field_fkey, alias="fulldate")
        field_year = Function("toYear", Field("fulldate"))
        field_month = Function("toMonth", Field("fulldate"))
        restricted_set = (
            ClickHouseQuery.from_(tfrom)
            .select(Max(field_year))
            .groupby(field_year)
            .having(Count(field_month).distinct() == 12)
        )
        return field_year <= restricted_set, [field_date]

    if fkey_type == "YYYYMM":
        field_year = Function("intDiv", field_fkey, 100)
        field_month = Function("modulo", field_fkey, 100)
        restricted_set = (
            ClickHouseQuery.from_(tfrom)
            .select(Max(field_year))
            .groupby(field_year)
            .having(Count(field_month).distinct() == 12)
        )
        return field_year < restricted_set, []

    if fkey_type == "YYYY":
        restricted_set = ClickHouseQuery.from_(tfrom).select(Max(field_fkey))
        return field_fkey <= restricted_set, []

    raise ValueError("Can't apply a restriction over this field")
