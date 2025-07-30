# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentGenerateParams"]


class DocumentGenerateParams(TypedDict, total=False):
    slug: Required[str]
    """The slug of the document template to use."""

    type: Required[Literal["pdf", "report"]]
    """The type of document to generate ('pdf' or 'report')."""

    variables: Required[Dict[str, str]]
    """An object containing key-value pairs for template variables."""

    file_name: Annotated[str, PropertyInfo(alias="fileName")]
    """Optional desired file name for the generated document."""
