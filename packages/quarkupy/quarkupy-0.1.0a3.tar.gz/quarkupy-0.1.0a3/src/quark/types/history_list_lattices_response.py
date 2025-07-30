# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .history.lattice_history_item import LatticeHistoryItem

__all__ = ["HistoryListLatticesResponse"]

HistoryListLatticesResponse: TypeAlias = List[LatticeHistoryItem]
