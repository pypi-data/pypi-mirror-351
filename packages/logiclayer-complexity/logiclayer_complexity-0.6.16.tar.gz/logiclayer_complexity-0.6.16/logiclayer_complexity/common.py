from __future__ import annotations

from typing import Iterable

import pandas as pd

VALID_COMPARISONS = ("lt", "lte", "gt", "gte", "eq", "neq")


def split_list(items: list[str], tokensep: str = ",") -> Iterable[str]:
    """Split the items in a list of strings, and filter empty strings."""
    return (token.strip() for item in items for token in item.split(tokensep))


def split_dict(items: list[str], tokensep: str, keysep: str = ":") -> Iterable[tuple[str, str]]:
    """Split the items in a list of strings to generate a set of (key, value) pairs."""
    return (
        (key, value)
        for key, value in (
            tuple(token.split(keysep, maxsplit=1))
            for item in items
            for token in item.split(tokensep)
        )
    )


def series_compare(series: pd.Series, operator: str, value: float) -> pd.Series[bool]:
    """Apply the comparison operator against a scalar value over a pandas Series."""
    if operator == "lt":
        return series.lt(value)
    if operator == "lte":
        return series.le(value)
    if operator == "gt":
        return series.gt(value)
    if operator == "gte":
        return series.ge(value)
    if operator == "eq":
        return series.eq(value)
    if operator == "neq":
        return series.ne(value)

    msg = f"Invalid comparison operator '{operator}'"
    raise ValueError(msg)


def df_pivot(df: pd.DataFrame, *, index: str, column: str, value: str):
    """Pivot a DataFrame."""
    return (
        pd.pivot_table(df, index=[index], columns=[column], values=value)
        .reset_index()
        .set_index(index)
        .dropna(axis=1, how="all")
        .fillna(0)
        .astype(float)
    )


def df_melt(df: pd.DataFrame, *, index: str, value: str):
    """Unpivot a DataFrame.

    It also adds category labels for the drilldown IDs.
    """
    df = df.reset_index().set_index(index).dropna(axis=1, how="all").fillna(0).reset_index()
    return pd.melt(df, id_vars=[index], value_name=value)
