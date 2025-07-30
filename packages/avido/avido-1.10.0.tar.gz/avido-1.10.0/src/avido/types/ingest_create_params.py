# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "IngestCreateParams",
    "Event",
    "EventIngestTrace",
    "EventIngestLlmStep",
    "EventIngestLlmStepUsage",
    "EventIngestToolStep",
    "EventIngestRetrieverStep",
    "EventIngestLogStep",
    "EventIngestGroupStep",
]


class IngestCreateParams(TypedDict, total=False):
    events: Required[Iterable[Event]]
    """Array of events to be ingested, which can be threads or traces."""


class EventIngestTrace(TypedDict, total=False):
    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["trace"]]

    group: Optional[str]
    """Optionally, the key for a group step to group the step with."""

    metadata: Optional[str]
    """Arbitrary metadata for this thread (e.g., userId, source, etc.)."""

    name: Optional[str]
    """The name of the step."""

    params: Optional[str]
    """Arbitrary params for the step."""

    reference_id: Annotated[Optional[str], PropertyInfo(alias="referenceId")]
    """Unique Trace ID (UUID).

    If not provided, it will be generated server-side. We recommend using the same
    ID as you have for the conversation or interaction in your own database.
    """

    test_id: Annotated[Optional[str], PropertyInfo(alias="testId")]
    """Optional test ID for the trace if this was an Avido triggered run.

    It will be provided in the body of the webhook.
    """


class EventIngestLlmStepUsage(TypedDict, total=False):
    completion_tokens: Annotated[Optional[float], PropertyInfo(alias="completionTokens")]
    """Number of completion tokens used by the LLM."""

    prompt_tokens: Annotated[Optional[float], PropertyInfo(alias="promptTokens")]
    """Number of prompt tokens used by the LLM."""


class EventIngestLlmStep(TypedDict, total=False):
    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["llm"]]

    event: Optional[Literal["start", "end"]]
    """The event type (e.g., 'start', 'end')."""

    group: Optional[str]
    """Optionally, the key for a group step to group the step with."""

    input: Optional[str]
    """The input for the LLM step."""

    metadata: Optional[str]
    """Arbitrary metadata for this thread (e.g., userId, source, etc.)."""

    model_id: Annotated[Optional[str], PropertyInfo(alias="modelId")]
    """The model ID (e.g., 'gpt-4o-2024-08-06')."""

    name: Optional[str]
    """The name of the step."""

    output: Optional[str]
    """The output for the LLM step."""

    params: Optional[str]
    """Arbitrary params for the step."""

    trace_id: Annotated[Optional[str], PropertyInfo(alias="traceId")]
    """
    Add the Trace ID to link the step to a trace if no trace is included as an event
    """

    usage: Optional[EventIngestLlmStepUsage]
    """Number of input and output tokens used by the LLM."""


class EventIngestToolStep(TypedDict, total=False):
    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["tool"]]

    group: Optional[str]
    """Optionally, the key for a group step to group the step with."""

    metadata: Optional[str]
    """Arbitrary metadata for this thread (e.g., userId, source, etc.)."""

    name: Optional[str]
    """The name of the step."""

    params: Optional[str]
    """Arbitrary params for the step."""

    tool_input: Annotated[Optional[str], PropertyInfo(alias="toolInput")]
    """The input for the tool step."""

    tool_output: Annotated[Optional[str], PropertyInfo(alias="toolOutput")]
    """The output for the tool step."""

    trace_id: Annotated[Optional[str], PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


class EventIngestRetrieverStep(TypedDict, total=False):
    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["retriever"]]

    group: Optional[str]
    """Optionally, the key for a group step to group the step with."""

    metadata: Optional[str]
    """Arbitrary metadata for this thread (e.g., userId, source, etc.)."""

    name: Optional[str]
    """The name of the step."""

    params: Optional[str]
    """Arbitrary params for the step."""

    query: Optional[str]
    """The query for the retriever step."""

    result: Optional[str]
    """The result for the retriever step."""

    trace_id: Annotated[Optional[str], PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


class EventIngestLogStep(TypedDict, total=False):
    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["log"]]

    content: Optional[str]
    """The content for the log step."""

    group: Optional[str]
    """Optionally, the key for a group step to group the step with."""

    metadata: Optional[str]
    """Arbitrary metadata for this thread (e.g., userId, source, etc.)."""

    name: Optional[str]
    """The name of the step."""

    params: Optional[str]
    """Arbitrary params for the step."""

    trace_id: Annotated[Optional[str], PropertyInfo(alias="traceId")]
    """The trace ID (UUID)."""


class EventIngestGroupStep(TypedDict, total=False):
    key: Required[str]
    """
    A unique identifier for the grouping, which must be appended to the
    corresponding steps
    """

    timestamp: Required[str]
    """
    ISO-8601 datetime with up to microsecond precision (e.g.,
    2025-01-05T12:34:56.789123Z). Numeric millisecond timestamps (number or numeric
    string) are also accepted and automatically converted.
    """

    type: Required[Literal["group"]]

    group: Optional[str]
    """Optionally, the key for a group step to group the step with."""

    metadata: Optional[str]
    """Arbitrary metadata for this thread (e.g., userId, source, etc.)."""

    name: Optional[str]
    """The name of the step."""

    params: Optional[str]
    """Arbitrary params for the step."""


Event: TypeAlias = Union[
    EventIngestTrace,
    EventIngestLlmStep,
    EventIngestToolStep,
    EventIngestRetrieverStep,
    EventIngestLogStep,
    EventIngestGroupStep,
]
