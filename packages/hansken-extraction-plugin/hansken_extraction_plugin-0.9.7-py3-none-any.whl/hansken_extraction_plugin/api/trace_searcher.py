"""This module contains the definition of a trace searcher."""
from abc import abstractmethod
from enum import Enum
from typing import Union

from hansken_extraction_plugin.api.search_result import SearchResult


class SearchScope(str, Enum):
    """Scope to describe the search context for TraceSearcher.search calls."""

    image = 'image'
    project = 'project'


class TraceSearcher:
    """This class can be used to search for traces, using the search method."""

    @abstractmethod
    def search(self, query: str, count: int, scope: Union[str, SearchScope] = SearchScope.image) -> SearchResult:
        """
        Search for indexed traces in Hansken using provided query returning at most count results.

        :param query: HQL-query used for searching
        :param count: Maximum number of traces to return
        :param scope: Select search scope: 'image' to search only search for other traces within the image of the trace
                      that is being processed, or 'project' to search in the scope of the full project (either Scope-
                      enum value can be used, or the str-values directly).
        :return: SearchResult containing found traces
        """
