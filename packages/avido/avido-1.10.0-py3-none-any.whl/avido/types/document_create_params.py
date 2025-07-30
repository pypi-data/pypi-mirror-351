# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .document_status import DocumentStatus

__all__ = ["DocumentCreateParams"]


class DocumentCreateParams(TypedDict, total=False):
    assignee: Required[str]
    """User ID of the person assigned to this document"""

    content: Required[str]
    """Content of the document"""

    status: Required[DocumentStatus]
    """Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED."""

    title: Required[str]
    """Title of the document"""

    metadata: Dict[str, object]
    """Optional metadata associated with the document"""

    original_sentences: Annotated[List[str], PropertyInfo(alias="originalSentences")]
    """Array of original sentences from the source"""

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]
    """Optional ID of the parent document"""

    scrape_job_id: Annotated[str, PropertyInfo(alias="scrapeJobId")]
    """Optional ID of the scrape job that generated this document"""
