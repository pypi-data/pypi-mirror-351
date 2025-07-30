# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["QuarkUpdateParams"]


class QuarkUpdateParams(TypedDict, total=False):
    created_at: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]
    """The timestamp indicating when the Quark was created."""

    identity_id: Required[int]
    """Identity of Quark runner"""

    input: Required[object]
    """Input data associated with the Quark, stored as a JSON value."""

    lattice_id: Required[str]
    """Identifier of the associated Lattice."""

    output: Required[object]
    """Output data produced by the Quark execution, stored as a JSON value."""

    quark_id: Required[str]
    """Unique identifier for the Quark."""

    registry_identifier: Required[str]
    """Identifier for the registry where the Quark is defined."""

    state: Required[object]
    """Quark State"""

    status: Required[Literal["New", "Scheduled", "Running", "OutputStaged", "Completed", "Failed"]]
    """Represents the status/stage of a Quark instance"""

    runner_task_id: str
    """Runner [WorkerTask] id Optional, as there are stages when no runner is assigned"""

    supervisor_task_id: str
    """
    Supervisor [WorkerTask] id Optional, as there are stages when no supervisor is
    assigned
    """

    worker_id: str
    """Runner [WorkerTask] id Optional, as there are stages when no worker is assigned"""
