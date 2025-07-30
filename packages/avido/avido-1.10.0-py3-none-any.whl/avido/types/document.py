# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["Document"]


class Document(BaseModel):
    document: Document
    """
    A Core Document represents a piece of content that can be organized
    hierarchically with parent-child relationships
    """
