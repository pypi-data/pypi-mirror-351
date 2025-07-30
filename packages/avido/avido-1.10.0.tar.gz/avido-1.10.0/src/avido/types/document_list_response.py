# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .document_status import DocumentStatus

__all__ = ["DocumentListResponse", "Child", "ChildScrapeJob", "Parent", "ParentScrapeJob", "ScrapeJob"]


class ChildScrapeJob(BaseModel):
    id: str
    """Unique identifier of the scrape job"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the scrape job was created"""

    initiated_by: str = FieldInfo(alias="initiatedBy")
    """User ID who initiated the scrape job"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the scrape job was last modified"""

    name: str
    """Name of the scrape job"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this scrape job"""

    status: Literal["PENDING", "IN_PROGRESS", "RUNNING", "COMPLETED", "FAILED"]
    """Status of the scrape job.

    Valid options: PENDING, IN_PROGRESS, RUNNING, COMPLETED, FAILED.
    """

    pages: Optional[Dict[str, object]] = None
    """JSON object containing scraped pages data"""

    url: Optional[str] = None
    """Optional URL that was scraped"""


class Child(BaseModel):
    id: str
    """Unique identifier of the document"""

    assignee: str
    """User ID of the person assigned to this document"""

    content: str
    """Content of the document"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the document was created"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the document was last modified"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this document"""

    original_sentences: List[str] = FieldInfo(alias="originalSentences")
    """Array of original sentences from the source"""

    status: DocumentStatus
    """Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED."""

    title: str
    """Title of the document"""

    metadata: Optional[Dict[str, object]] = None
    """Optional metadata associated with the document"""

    scrape_job: Optional[ChildScrapeJob] = FieldInfo(alias="scrapeJob", default=None)
    """Optional scrape job that generated this document"""

    scrape_job_id: Optional[str] = FieldInfo(alias="scrapeJobId", default=None)
    """Optional ID of the scrape job that generated this document"""


class ParentScrapeJob(BaseModel):
    id: str
    """Unique identifier of the scrape job"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the scrape job was created"""

    initiated_by: str = FieldInfo(alias="initiatedBy")
    """User ID who initiated the scrape job"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the scrape job was last modified"""

    name: str
    """Name of the scrape job"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this scrape job"""

    status: Literal["PENDING", "IN_PROGRESS", "RUNNING", "COMPLETED", "FAILED"]
    """Status of the scrape job.

    Valid options: PENDING, IN_PROGRESS, RUNNING, COMPLETED, FAILED.
    """

    pages: Optional[Dict[str, object]] = None
    """JSON object containing scraped pages data"""

    url: Optional[str] = None
    """Optional URL that was scraped"""


class Parent(BaseModel):
    id: str
    """Unique identifier of the document"""

    assignee: str
    """User ID of the person assigned to this document"""

    content: str
    """Content of the document"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the document was created"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the document was last modified"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this document"""

    original_sentences: List[str] = FieldInfo(alias="originalSentences")
    """Array of original sentences from the source"""

    status: DocumentStatus
    """Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED."""

    title: str
    """Title of the document"""

    metadata: Optional[Dict[str, object]] = None
    """Optional metadata associated with the document"""

    scrape_job: Optional[ParentScrapeJob] = FieldInfo(alias="scrapeJob", default=None)
    """Optional scrape job that generated this document"""

    scrape_job_id: Optional[str] = FieldInfo(alias="scrapeJobId", default=None)
    """Optional ID of the scrape job that generated this document"""


class ScrapeJob(BaseModel):
    id: str
    """Unique identifier of the scrape job"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the scrape job was created"""

    initiated_by: str = FieldInfo(alias="initiatedBy")
    """User ID who initiated the scrape job"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the scrape job was last modified"""

    name: str
    """Name of the scrape job"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this scrape job"""

    status: Literal["PENDING", "IN_PROGRESS", "RUNNING", "COMPLETED", "FAILED"]
    """Status of the scrape job.

    Valid options: PENDING, IN_PROGRESS, RUNNING, COMPLETED, FAILED.
    """

    pages: Optional[Dict[str, object]] = None
    """JSON object containing scraped pages data"""

    url: Optional[str] = None
    """Optional URL that was scraped"""


class DocumentListResponse(BaseModel):
    id: str
    """Unique identifier of the document"""

    assignee: str
    """User ID of the person assigned to this document"""

    content: str
    """Content of the document"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the document was created"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the document was last modified"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this document"""

    original_sentences: List[str] = FieldInfo(alias="originalSentences")
    """Array of original sentences from the source"""

    status: DocumentStatus
    """Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED."""

    title: str
    """Title of the document"""

    children: Optional[List[Child]] = None
    """Array of child documents"""

    metadata: Optional[Dict[str, object]] = None
    """Optional metadata associated with the document"""

    parent: Optional[Parent] = None
    """Parent document"""

    scrape_job: Optional[ScrapeJob] = FieldInfo(alias="scrapeJob", default=None)
    """Optional scrape job that generated this document"""

    scrape_job_id: Optional[str] = FieldInfo(alias="scrapeJobId", default=None)
    """Optional ID of the scrape job that generated this document"""
