# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .document_status import DocumentStatus

__all__ = ["DocumentUpdateParams"]


class DocumentUpdateParams(TypedDict, total=False):
    assignee: str
    """User ID of the person assigned to this document"""

    content: str
    """Content of the document"""

    metadata: Dict[str, object]
    """Optional metadata associated with the document"""

    original_sentences: Annotated[List[str], PropertyInfo(alias="originalSentences")]
    """Array of original sentences from the source"""

    parent_id: Annotated[Optional[str], PropertyInfo(alias="parentId")]
    """Optional ID of the parent document"""

    status: DocumentStatus
    """Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED."""

    title: str
    """Title of the document"""
