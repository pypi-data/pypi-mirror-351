# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["HistoryListQuarksParams"]


class HistoryListQuarksParams(TypedDict, total=False):
    lattice_id: str

    max_timestamp: int

    min_timestamp: int

    registry_identifier: str
