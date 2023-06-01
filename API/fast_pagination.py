from django.core.cache import cache
from django.core.paginator import (
    InvalidPage,
    Paginator,
    Page
)
from rest_framework.exceptions import NotFound

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response

from django.conf import settings

import sys
import hashlib


__all__ = ["FastPageNumberPagination", "FastLimitOffsetPagination"]


def get_show_count_from_request(request) -> bool:
    return request.query_params.get("show_count", "False").lower() == "true"


class FastQuerysetPage(Page):
    def __len__(self):
        return len(self.paginator.pks)


class FastPagePaginator(Paginator):
    """
    Django default Paginator makes a `.count()` call to get the total number of items in the database, which is very
    costly in millions of records. This paginator disables this behaviour by providing the system's maximum number
    as a count, thus avoiding the database query, reducing queries time by +99%. Another performance improvement is the
    use of object id's instead of using SQL queries OFFSET and LIMIT, so that we only retrieve the PAGE_SIZE of objects
    whose id's are contained in the sliced ids list, ex. SELECT .... WHERE "model"."id" IN (...) ...
    (python list slicing is much faster than SQL's OFFSET and LIMIT for large lists)
    """
    TIMEOUT = getattr(settings, "FAST_PAGE_PAGINATION_TIMEOUT", 3600)
    PREFIX = getattr(settings, "FAST_PAGE_PAGINATION_PREFIX", "api_fast_page_pagination")

    def __init__(self, *args, **kwargs) -> None:
        self.request = kwargs.pop("request", None)

        super().__init__(*args, **kwargs)

        raw_query_key = str(hashlib.md5(str(self.object_list.query).encode('utf-8')).hexdigest())

        self.cache_pks_key = f"{self.PREFIX}:pks:{raw_query_key}"
        self.cache_count_key = f"{self.PREFIX}:count:{raw_query_key}"

    @property
    def count(self) -> int:
        """
        If `show_count` query parameter is true, an actual count is performed but only once every TIMEOUT
        (default is 1 hour). Otherwise, (default behavior), we patch the count with `sys.maxsize`.
        """
        show_count: bool = get_show_count_from_request(self.request)

        if show_count:
            result = cache.get(self.cache_count_key)

            if result is None:
                result = self.object_list.count()
                cache.set(self.cache_count_key, result, timeout=self.TIMEOUT)

            return result
        return sys.maxsize

    @property
    def pks(self):
        result = cache.get(self.cache_pks_key)

        if result is None:
            result = list(self.object_list.values_list('pk', flat=True))
            cache.set(self.cache_pks_key, result, timeout=self.TIMEOUT)

        return result

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page

        if top + self.orphans >= self.count:
            top = self.count

        pks = self.pks[bottom:top]
        object_list = self.object_list.filter(pk__in=pks)

        return self._get_page(object_list, number, self)

    def _get_page(self, *args, **kwargs):
        return FastQuerysetPage(*args, **kwargs)


class FastPageNumberPagination(PageNumberPagination):
    """
    Custom Django Rest Pagination class based on user defined settings and uses a custom Django Paginator that avoids
    `COUNT` SQL query on each API response.
    """

    django_paginator_class = FastPagePaginator

    def get_paginated_response(self, data):
        # Check if the response should include counting or not
        show_count: bool = get_show_count_from_request(self.request)

        if show_count:
            response = {"count": self.page.paginator.count}
        else:
            response = {}

        response.update({
            "current_page": self.page.number,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })

        return Response(response)

    def get_html_context(self):
        """Specify the needed context for
        "rest_framework/pagination/previous_and_next.html" template rendering."""
        return {
            "previous_url": self.get_previous_link(),
            "next_url": self.get_next_link(),
        }

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)

        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size, request=request)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(page_number=page_number, message=str(exc))

            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        qs = list(self.page)

        if not qs:
            self.page.has_next = lambda: False
        return qs


class FastLimitOffsetPagination(LimitOffsetPagination):
    """
    Custom Django Rest Pagination class based on user defined settings and uses a custom Django Paginator that avoids
    `COUNT` SQL query on each API response.
    """

    TIMEOUT = getattr(settings, "FAST_LIMIT_OFFSET_PAGINATION_TIMEOUT", 3600)
    PREFIX = getattr(settings, "FAST_LIMIT_OFFSET_PAGINATION_PREFIX", "api_fast_limit_offset_pagination")

    def check_cache_keys(self, queryset):
        if not hasattr(self, 'cache_pks_key'):
            raw_query_key = str(hashlib.md5(str(queryset.query).encode('utf-8')).hexdigest())

            self.cache_pks_key = f"{self.PREFIX}:pks:{raw_query_key}"
            self.cache_count_key = f"{self.PREFIX}:count:{raw_query_key}"

    def pks(self, queryset):
        self.check_cache_keys(queryset)

        result = cache.get(self.cache_pks_key)

        if result is None:
            result = list(queryset.values_list('pk', flat=True))
            cache.set(self.cache_pks_key, result, timeout=self.TIMEOUT)

        return result

    def get_html_context(self):
        """Specify the needed context for
        "rest_framework/pagination/previous_and_next.html" template rendering."""
        return {
            "previous_url": self.get_previous_link(),
            "next_url": self.get_next_link(),
        }

    def get_count(self, queryset):
        self.check_cache_keys(queryset)

        result = cache.get(self.cache_count_key)

        if result is None:
            result = queryset.count()
            cache.set(self.cache_count_key, result, timeout=self.TIMEOUT)

        return result

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)

        if self.limit is None:
            return None

        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)
        self.request = request

        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []

        return list(queryset.filter(pk__in=self.pks(queryset)[self.offset:self.offset + self.limit]))
