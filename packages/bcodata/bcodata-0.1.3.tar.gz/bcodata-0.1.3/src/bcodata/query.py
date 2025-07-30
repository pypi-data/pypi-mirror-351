from collections.abc import Sequence
from typing import Any, Self


class QueryBuilder:
    """A builder for OData query parameters."""

    def __init__(self) -> None:
        """Initialize an empty query builder."""
        self._params: dict[str, Any] = {}

    def filter(self, condition: str) -> Self:
        """
        Add a $filter parameter to the query.

        Parameters
        ----------
        condition : str
            The filter condition (e.g., "Name eq 'John'").

        Returns
        -------
        Self
            The query builder instance for method chaining.

        """
        self._params["$filter"] = condition
        return self

    def select(self, fields: Sequence[str]) -> Self:
        """
        Add a $select parameter to the query.

        Parameters
        ----------
        fields : Sequence[str]
            The fields to select.

        Returns
        -------
        Self
            The query builder instance for method chaining.

        """
        self._params["$select"] = ",".join(fields)
        return self

    def top(self, count: int) -> Self:
        """
        Add a $top parameter to limit the number of results.

        Parameters
        ----------
        count : int
            The maximum number of results to return.

        Returns
        -------
        Self
            The query builder instance for method chaining.

        """
        if count <= 0:
            raise ValueError("Top count must be greater than 0")
        self._params["$top"] = count
        return self

    def skip(self, count: int) -> Self:
        """
        Add a $skip parameter to skip a number of results.

        Parameters
        ----------
        count : int
            The number of results to skip.

        Returns
        -------
        Self
            The query builder instance for method chaining.

        """
        if count < 0:
            raise ValueError("Skip count must be non-negative")
        self._params["$skip"] = count
        return self

    def order_by(self, field: str, descending: bool = False) -> Self:  # noqa: FBT001, FBT002
        """
        Add an $orderby parameter to sort the results.

        Parameters
        ----------
        field : str
            The field to sort by.
        descending : bool, optional
            Whether to sort in descending order, by default False.

        Returns
        -------
        Self
            The query builder instance for method chaining.

        """
        order = f"{field} desc" if descending else field
        self._params["$orderby"] = order
        return self

    def build(self) -> dict[str, Any]:
        """
        Build the query parameters.

        Returns
        -------
        dict[str, Any]
            The constructed query parameters.

        """
        return self._params.copy()

    def __str__(self) -> str:
        """
        Get a string representation of the query parameters.

        Returns
        -------
        str
            The query parameters as a string.

        """
        return "&".join(f"{k}={v}" for k, v in self._params.items())
