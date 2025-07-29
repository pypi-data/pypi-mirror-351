import json
import logging
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    TypeAlias,
    TypeVar,
    cast,
    Sequence,
)

import html_generators as h
from django.db.models import Model, QuerySet
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
    QueryDict,
)
from django.utils.translation import gettext as _

log = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Model)
AggregateResult = TypeVar("AggregateResult")

# Some definitions:
HtmlGeneratorsContent = Any  # Content meant for display by html_generators
InlineHtmlGeneratorsContent = Any  # Inline content meant for display by html generators
FilterFunction: TypeAlias = (
    "Callable[[QueryDict, QuerySet[ModelType]], QuerySet[ModelType]]"
)
PK = Any  # Anything that can be serialized as JSON
SortFunction: TypeAlias = "Callable[[QuerySet[ModelType]], QuerySet[ModelType]]"


class ColumnFormatter(Generic[ModelType]):
    """
    To be used by "advanced" Column instances, where a simple Callable formatter isn't powerful enough.

    aggregator:
        Will be called by the Column once, before generating an entire page of table data. The result will be passed to the formatter function for each row. This allows you to create a separate queryset of related data, and then use info from that queryset in each row. This can useful when following foreign keys backward (eg. when `related_name` is set to '+', or when you are using type-checked code and don't want to use automagical reverse accessors).
    """

    def __init__(
        self,
        aggregator: "Callable[[QuerySet[ModelType]], AggregateResult]",
        formatter: "Callable[[ModelType, AggregateResult], HtmlGeneratorsContent]",
    ):
        def make_simple_formatter(
            qs: QuerySet[ModelType],
        ) -> Callable[[ModelType], HtmlGeneratorsContent]:
            aggregate_result = aggregator(qs)

            def format(o: ModelType):
                return formatter(o, aggregate_result)

            return format

        self.make_simple_formatter = make_simple_formatter


class Column(Generic[ModelType]):
    def __init__(
        self,
        *,
        # Note - may also be a lazy (translatable) string
        header: str,
        # Note - if you return anything other than an h.Element, in will be wrapped in a <div>
        # Note - if you return an h.Element, it will be used as the cell element directly (and have the cell's background color, border, padding, etc.)
        # If you do NOT want that to happen, wrap that element in a plain div
        # So you if you want "an <i>apple</i>" to show up on one line, you have to wrap in div AND span
        formatter: "Callable[[ModelType], HtmlGeneratorsContent]|ColumnFormatter[ModelType]",
        # Set to false to make initially-disabled, but still available in column list
        enabled: bool = True,
        # Fixed columns are "sticky" when scrolling horizontally
        # They are "transported" to the left-most part of the table
        # They cannot be sorted/disabled by the user
        # Intended mainly for "main action" column
        fixed: bool = False,
        sort_function: "Optional[SortFunction[ModelType]]" = None,
        # Called only when fetching a page of data which includes this column, and before passing the queryset to your sort_function (when sorting on this column)
        prepare: "Callable[[QuerySet[ModelType]], QuerySet[ModelType]]" = lambda qs: qs,
        width: int = 150,
        # Note - may also be a lazy (translatable) string
        help_text: str = "",
    ) -> None:
        self.header = header
        self.formatter = formatter
        self.sort_function = sort_function
        self.prepare = prepare
        self.width = width
        self.help_text = help_text

        self.enabled = enabled
        self.fixed = fixed


OverflowFormatter = Callable[[int, int], InlineHtmlGeneratorsContent]


def _default_line_overflow_indicator(total: int, overflow_count: int):
    text = (
        (
            # In this case, max_lines is set to 1.
            # There are no "normal" lines showing.
            _("{count} items").format(count=total)
        )
        if total == overflow_count
        # max_lines is more than 1. At least one "normal line" is visible above this.
        else (
            h.template(
                _("{plus_sign}{count} more"),
                count=overflow_count,
                plus_sign=h.B("+"),
            )
        )
    )

    return h.Span(text, class_="django-data-tables-overflow-indicator")


class LineCapper:
    """
    Utility class for rendering multi-line content that is capped to a certain number of lines.

    You'll likely want to create one instance per TableManager instance, so that all of your columns are using the same # of max lines.

    Columns that render a "single thing" (like an email address) which should never take up more than one line have no need for this. Just output that thing directly.
    """

    def __init__(self, max_lines: int):
        self.max_lines = max_lines

    def _unwrapped_line_items(
        self,
        line_items: Iterable[InlineHtmlGeneratorsContent],
        overflow_formatter: OverflowFormatter,
    ):
        items = [item for item in line_items if item]
        total = len(items)
        if total > self.max_lines:
            show_lines = self.max_lines - 1
            return (
                (h.Div(item) for item in items[:show_lines]),
                h.Div(overflow_formatter(total, total - show_lines)),
            )
        return (h.Div(item) for item in items)

    def line_items(
        self,
        line_items: Iterable[InlineHtmlGeneratorsContent],
        overflow_formatter: OverflowFormatter = _default_line_overflow_indicator,
    ) -> h.Element:
        """
        Each item will be rendered on it's own line.
        If there are more items than max lines, the last line will be used to show an "overflow indicator".

        Note - the line_items should NOT include any br's' or block-level elements. If they do, cells might end up showing more than max_lines.
        """
        return h.Div(
            self._unwrapped_line_items(line_items, overflow_formatter),
        )

    def wrapping_text(self, text: str, newline_indicator: str = "｜") -> h.Element:
        """
        Let text wrap, but show "indicator" for explicit newlines.
        Useful for content that was typed into a textarea, or anything else that might have explicit newlines.

        Default newline indicator is "fullwidth vertical line", which has a little space to either side, unlike plain pipe/bar character.

        Uses fairly new -webkit-line-clamp.
        Works fairly well IFF the column width is wider than most content words.

        If a single word is wider than column, it gets broken accross multiple lines (often without hyphenation).
        We use the CSS "hyphens" property to _try_ to force hyphens when breaking words, but that seems to rely on a "hyphenation dictionary", and only works when breaking certain words.
        If last line in cell is a single overflowing word (without hyphenation), there is no visual indicator for overflow at all.
        """
        wrapped_content = h.Div(
            newline_indicator.join(text.splitlines()),
            class_="django-data-tables-wrapping-content",
            style=f"-webkit-line-clamp: {self.max_lines}",
        )
        # We need another wrapper element to be used as the cell.
        # You should not use padding on any element which uses -webkit-line-clamp, the padding should go on a wrapper element. Otherwise, truncated text will actually be visible in the padding area.
        return h.Div(wrapped_content)

    def wrapping_content(self, content: InlineHtmlGeneratorsContent) -> h.Element:
        """
        Similar to wrapping_text, but does NOT show "newline indicators".

        We recommend using wrapping_text for most use cases.
        Use this only if you need to pass html content (formatting), not just plain text.

        Really intended only basic phrasing content.
        Things like email addresses tend to look better if left on one line (with overflow indicator).
        """
        wrapped_content = h.Div(
            content,
            class_="django-data-tables-wrapping-content",
            style=f"-webkit-line-clamp: {self.max_lines}",
        )
        # We need another wrapper element to be used as the cell.
        # You should not use padding on any element which uses -webkit-line-clamp, the padding should go on a wrapper element. Otherwise, truncated text will actually be visible in the padding area.
        return h.Div(wrapped_content)

    def preserving_text(self, text: str) -> h.Element:
        """
        White space is preserved.
        Each line will show an ellipsis if it overflows.
        The last line will simply show a mid-line ellipsis if there are more lines than max_lines.
        """
        return h.Div(
            self._unwrapped_line_items(
                text.splitlines(),
                lambda total, overflow_count: "⋯",
            ),
            style="white-space: pre;",
        )

    # Note - we _might_ also want to support prewrap, and/or a variation thereof (preserving line breaks, but collapsing/trimming spaces)


class NotResponsible(Exception):
    pass


class DataError(Exception):
    pass


def make_sort_key(column_key: str, reverse: bool):
    """
    Used by TableManager when interpreting the sort_key passed by the front-end.
    May be useful when configuring a default sort key on your front-end.
    """
    if reverse:
        return f"_column_reverse_{column_key}"
    return f"_column_forward_{column_key}"


@dataclass(kw_only=True)
class TableManager(Generic[ModelType]):
    """
    Implements the back-end of the "QNC Data Table API V1".

    Note that while we only implement the back-end, we _collect_ some information that is only needed by the front-end. This makes it easy for consumers to write a function which accepts a TableManager instance and create whatever HTML/JS is needed by your front-end.

    queryset:
    - all of the objects that _may_ be shown in the table
    - if filter_function is used, the displayed result set may be a subset of this

    filter_function:
    - a function to be called

    columns:
    - the available columns

    extra_sort_functions:
    - collection of (key, display, sort_function) tuples
    - if non-None, the front-end should render a "sort widget" somewhere, with these as options

    fallback_sort_by_pk:
        If the front-end has not specified any sort order, sort queryset by pk.
        Default is True (ensures that we always use a specified/consistent ordering)
        Set to False if queryset is already ordered, and you want to retain that ordering when front-end does not specify ordering.
        Note: we _may_ drop/ignore this is in the future. It would probably be better to just always "post order" the queryset by pk (ie, _append_ "pk" to current ordering), even if front-end specifies sorting (in case column's sort function doesn't guarantee unique sorting). Unfortunately, this isn't possible without using undocumented parts of Django.
    """

    queryset: "QuerySet[ModelType]"

    filter_function: "FilterFunction[ModelType]" = (
        lambda query_dict, query_set: query_set
    )

    columns: Mapping[str, Column[ModelType]]

    extra_sort_functions: Collection[
        tuple[str, InlineHtmlGeneratorsContent, "SortFunction[ModelType]"]
    ] = ()

    fallback_sort_by_pk: bool = True

    page_limit: int = 100
    table_limit: int = 1000
    key_prefix: str = "table-manager"

    def handle(self, post_data: QueryDict) -> HttpResponse:
        """
        Return whatever API response django_data_tables.js called for.
        If the request wasn't actually directed at us, return HttpResponseBadRequest.
        """
        try:
            return self.handle_raising(post_data)
        except NotResponsible as e:
            log.warning(e)
            print("not responsible")
            return HttpResponseBadRequest()
        except DataError as e:
            log.warning(e)
            print("data error")

            return HttpResponseBadRequest(str(e))

    def handle_if_responsible(self, post_data: QueryDict) -> HttpResponse | None:
        """
        Return whatever API response django_data_tables.js called for, or None if the request wasn't directed at us.

        Useful on endpoints that handle multiple data tables (ie. multiple TableManagers with different ids). Eg:
        `return table_manager_1.handle_if_responsible(request.POST) or table_manager_2.handle(request.POST)`
        """
        try:
            return self.handle_raising(post_data)
        except NotResponsible:
            return None
        except DataError as e:
            log.warning(e)
            return HttpResponseBadRequest(str(e))

    def handle_raising(self, post_data: QueryDict) -> HttpResponse:
        """
        Return whatever API response django_data_tables.js called for.
        If the request wasn't actually directed at us, raise NotResponsible.
        If the request is directed at us but doesn't comply with the "data tables API" or contains unexpected column/sort keys, raise DataError.

        For simple data table pages, handle (and/or handle_if_responsible) should be sufficient.
        """
        action = post_data.get(f"{self.key_prefix}_action")

        if action == "get_result_count":
            return JsonResponse(
                dict(
                    count=self.filter_function(post_data, self.queryset).count(),
                    filter_data_understood=True,
                )
            )
        if action == "get_ids":
            qs = self.filter_function(post_data, self.queryset)
            sort_key = post_data.get(f"{self.key_prefix}_sort_key", None)
            qs, sort_key_understood = self._sort(qs, sort_key)

            return JsonResponse(
                dict(
                    filter_data_understood=True,
                    sort_key_understood=sort_key_understood,
                    ids=list(qs.values_list("pk", flat=True)),
                ),
            )
        if action == "get_table_data":
            ids, ids_understood = self._parse_pks(
                post_data.get(f"{self.key_prefix}_ids", "")
            )
            columns, columns_understood = self._parse_columns(
                post_data.get(f"{self.key_prefix}_columns", "")
            )

            return JsonResponse(
                dict(
                    column_keys_understood=columns_understood,
                    ids_understood=ids_understood,
                    rows=list(self._get_rows(ids, columns))
                    if ids_understood and columns_understood
                    else [],
                )
            )

        raise NotResponsible()

    def _sort(
        self,
        qs: "QuerySet[ModelType]",
        sort_key: str | None,
    ) -> tuple["QuerySet[ModelType]", bool]:
        """
        Return value is (sorted query set, "sort key was understood")
        """
        if sort_key is None:
            if self.fallback_sort_by_pk:
                qs = qs.order_by("pk")
            return qs, True

        for key, display_name, sort_function in self.extra_sort_functions:
            del display_name  # don't need this
            if key == sort_key:
                return sort_function(qs), True

        for column_key, column in self.columns.items():
            if column.sort_function:
                if sort_key == make_sort_key(column_key, False):
                    return column.sort_function(qs), True
                if sort_key == make_sort_key(column_key, True):
                    return column.sort_function(qs).reverse(), True

        return qs, False

    def _parse_pks(self, pks: str) -> tuple[list[Any], bool]:
        try:
            data = json.loads(pks)
        except json.JSONDecodeError:
            return [], False

        if not isinstance(data, list):
            return [], False

        return cast(list[Any], data), True

    def _parse_columns(
        self, columns: str
    ) -> tuple[Mapping[str, Column[ModelType]], bool]:
        try :
            data = json.loads(columns)
        except json.JSONDecodeError :
            return {}, False
        
        if not isinstance(data, list):
            return {}, False
        
        result = dict[str, Column[ModelType]]()

        for column in data : # type: ignore
            if column not in self.columns :
                return {}, False
            result[column] = self.columns[column]

        return result, True


    def _get_rows(self, ids: list[Any], columns: Mapping[str, Column[ModelType]]) -> Sequence[
        tuple[PK, Mapping[str, str]]
    ]:
        pk_order_map = dict((id, index) for index, id in enumerate(ids))

        qs = self.queryset.filter(pk__in=ids)

        for column in columns.values():
            qs = column.prepare(qs)

        simple_formatters: "dict[str, Callable[[ModelType], HtmlGeneratorsContent]]" = (
            dict()
        )

        for key, column in columns.items():
            simple_formatters[key] = (
                column.formatter.make_simple_formatter(qs)  # type: ignore  ; no idea why I VSCode thinks there is a type error here ; even without this "ignore comment", pyright does not complain when running manually
                if isinstance(column.formatter, ColumnFormatter)
                else column.formatter
            )

        rows = [
            (
                row.pk,
                {
                    key: str(h.Fragment(formatter(row)))
                    for key, formatter in simple_formatters.items()
                },
            )
            for row in qs
        ]
        rows.sort(key=lambda row: pk_order_map[row[0]])
        return rows
