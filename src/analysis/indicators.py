"""Reusable descriptive indicators shared by several posts.

Only put here what you have already used in more than one notebook. One-off analysis stays in the
notebook and, once final, in the post's .qmd.
"""

import polars as pl


def rebase(df: pl.DataFrame, value: str, time: str, base, by: list[str] | None = None) -> pl.DataFrame:
    """Add column '<value>_index' = 100 * value / value at `base` (per group if `by` is given)."""
    over = by or []
    base_value = pl.col(value).filter(pl.col(time) == base).first()
    expr = 100 * pl.col(value) / (base_value.over(over) if over else base_value)
    return df.with_columns(expr.alias(f"{value}_index"))


def share(df: pl.DataFrame, value: str, by: list[str]) -> pl.DataFrame:
    """Add column '<value>_share' = value / sum of value within `by` (e.g. foreign share per year)."""
    return df.with_columns((pl.col(value) / pl.col(value).sum().over(by)).alias(f"{value}_share"))
