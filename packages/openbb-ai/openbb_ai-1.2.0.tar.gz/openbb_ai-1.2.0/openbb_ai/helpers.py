from typing import Any, Literal

from .models import (
    Citation,
    CitationCollection,
    CitationCollectionSSE,
    DataSourceRequest,
    FunctionCallSSE,
    FunctionCallSSEData,
    MessageChunkSSE,
    MessageChunkSSEData,
    SourceInfo,
    StatusUpdateSSE,
    StatusUpdateSSEData,
    Widget,
    WidgetRequest,
)


def reasoning_step(
    message: str,
    event_type: Literal["INFO", "WARNING", "ERROR"] = "INFO",
    details: dict[str, Any] | None = None,
) -> StatusUpdateSSE:
    """Create a reasoning step (also known as a status update) SSE.

    This SSE is used to communicate the status of the agent, or any additional
    information as part of the agent's execution to the client.

    This Server-Sent Event (SSE) is typically `yield`ed to the client.

    Parameters
    ----------
    message: str
        The message to display.
    event_type: Literal["INFO", "WARNING", "ERROR"]
        The type of event to create.
        Default is "INFO".
    details: dict[str, Any] | None
        Additional details to display.
        Default is None.

    Returns
    -------
    StatusUpdateSSE
        The status update SSE.
    """
    return StatusUpdateSSE(
        data=StatusUpdateSSEData(
            eventType=event_type,
            message=message,
            details=[details] if details else [],
        )
    )


def message_chunk(text: str) -> MessageChunkSSE:
    """Create a message chunk SSE.

    This SSE is used to stream back chunks of text to the client, typically from
    the agent's streamed response.

    This Server-Sent Event (SSE) is typically `yield`ed to the client.

    Parameters
    ----------
    text: str
        The text chunk to stream to the client.

    Returns
    -------
    MessageChunkSSE
        The message chunk SSE.
    """
    return MessageChunkSSE(data=MessageChunkSSEData(delta=text))


def get_widget_data(widget_requests: list[WidgetRequest]) -> FunctionCallSSE:
    """Create a function call that retrieve data for a widget on the OpenBB Workspace

    The function call is typically `yield`ed to the client. After yielding this
    function call, you must immediately close the connection and wait for the
    follow-up function call.

    Parameters
    ----------
    widget_requests: list[WidgetRequest]
        A list of widget requests, where each request contains:
        - widget: A Widget instance defining the widget configuration
        - input_arguments: A dictionary of input parameters required by the widget

    Returns
    -------
    FunctionCallSSE
        The function call SSE.
    """

    data_sources: list[DataSourceRequest] = []
    for widget_request in widget_requests:
        data_sources.append(
            DataSourceRequest(
                widget_uuid=str(widget_request.widget.uuid),
                origin=widget_request.widget.origin,
                id=widget_request.widget.widget_id,
                input_args=widget_request.input_arguments,
            )
        )

    return FunctionCallSSE(
        data=FunctionCallSSEData(
            function="get_widget_data",
            input_arguments={"data_sources": data_sources},
        )
    )


def cite(
    widget: Widget,
    input_arguments: dict[str, Any],
    extra_details: dict[str, Any] | None = None,
) -> Citation:
    """Create a citation for a widget.

    Parameters
    ----------
    widget: Widget
        The widget to cite. Typically retrieved from the `QueryRequest` object.
    input_arguments: dict[str, Any] | None
        The input arguments used to retrieve data from the widget.
    extra_details: dict[str, Any] | None
        Extra details to display in the citation.
        Takes key-value pairs of the form `{"key": "value"}`.
        Default is None.

    Returns
    -------
    Citation
        The citation.
        Typically used as input to the `citations` function to be returned to
        the client.
    """
    return Citation(
        source_info=SourceInfo(
            type="widget",
            origin=widget.origin,
            widget_id=widget.widget_id,
            metadata={
                "input_args": input_arguments,
            },
        ),
        details=[extra_details] if extra_details else None,
    )


def citations(citations: list[Citation]) -> CitationCollectionSSE:
    """Create a citation collection SSE.

    This SSE is used to stream back citations to the client.

    This Server-Sent Event (SSE) is typically `yield`ed to the client.

    Parameters
    ----------
    citations: list[Citation]
        The citations to display.

    Returns
    -------
    CitationCollectionSSE
        The citation collection SSE.
    """
    return CitationCollectionSSE(data=CitationCollection(citations=citations))
