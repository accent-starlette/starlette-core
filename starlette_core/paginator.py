import collections.abc
import inspect
from math import ceil

from .exceptions import EmptyPage, InvalidPage, PageNotAnInteger
from .utils import method_has_no_args


class Paginator:
    def __init__(self, object_list, per_page):
        self.object_list = object_list
        self.per_page = int(per_page)
        self._count = None

    def validate_number(self, number):
        """Validate the given 1-based page number."""

        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger("That page number is not an integer")

        if number < 1:
            raise EmptyPage("That page number is less than 1")
        if number > self.num_pages and number != 1:
            raise EmptyPage("That page contains no results")

        return number

    def get_page(self, number):
        """
        Return a valid page, even if the page argument isn't a number or isn't
        in range.
        """

        try:
            number = self.validate_number(number)
        except PageNotAnInteger:
            number = 1
        except EmptyPage:
            number = self.num_pages
        return self.page(number)

    def page(self, number):
        """Return a Page object for the given 1-based page number."""

        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        return self._get_page(self.object_list[bottom:top], number, self)

    def _get_page(self, *args, **kwargs):
        """
        Return an instance of a single page.
        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """

        return Page(*args, **kwargs)

    @property
    def count(self):
        """Return the total number of objects, across all pages."""

        if self._count:
            return self._count

        c = getattr(self.object_list, "count", None)
        if callable(c) and not inspect.isbuiltin(c) and method_has_no_args(c):
            self._count = c()
        else:
            self._count = len(self.object_list)

        return self._count

    @property
    def num_pages(self):
        """Return the total number of pages."""

        hits = max(1, self.count)
        return ceil(hits / self.per_page)


class Page(collections.abc.Sequence):
    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def __repr__(self):
        return f"<Page {self.number} of {self.paginator.num_pages}>"

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        if not isinstance(index, (int, slice)):
            raise TypeError
        # The object_list is converted to a list so that if it was a QuerySet
        # it won't be a database hit per __getitem__.
        if not isinstance(self.object_list, list):
            self.object_list = list(self.object_list)
        return self.object_list[index]

    @property
    def has_next(self):
        return self.number < self.paginator.num_pages

    @property
    def next_page_number(self):
        return self.paginator.validate_number(self.number + 1)

    @property
    def has_previous(self):
        return self.number > 1

    @property
    def previous_page_number(self):
        return self.paginator.validate_number(self.number - 1)

    @property
    def has_other_pages(self):
        return self.has_previous or self.has_next
