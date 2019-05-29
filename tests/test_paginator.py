import pytest

from starlette_core.paginator import EmptyPage, InvalidPage, PageNotAnInteger, Paginator


def check_paginator(params, output):
    """
    Helper method that instantiates a Paginator object from the passed
    params and then checks that its attributes match the passed output.
    """
    count, num_pages = output
    paginator = Paginator(*params)
    check_attribute("count", paginator, count, params)
    check_attribute("num_pages", paginator, num_pages, params)


def check_attribute(name, paginator, expected, params):
    """
    Helper method that checks a single attribute and gives a nice error
    message upon test failure.
    """
    got = getattr(paginator, name)
    assert expected == got


def test_paginator():
    """
    Tests the paginator attributes using varying inputs.
    """
    nine = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    ten = nine + [10]
    ten + [11]
    tests = (
        # Each item is two tuples:
        #     First tuple is Paginator parameters - object_list, per_page
        #     Second tuple is resulting Paginator attributes - count, num_pages.
        # Ten items.
        ((ten, 1), (10, 10)),
        ((ten, 2), (10, 5)),
        ((ten, 3), (10, 4)),
        ((ten, 4), (10, 3)),
        ((ten, 5), (10, 2)),
        ((ten, 6), (10, 2)),
        ((ten, 7), (10, 2)),
        ((ten, 8), (10, 2)),
        ((ten, 9), (10, 2)),
        ((ten, 10), (10, 1)),
        # One item.
        (([1], 4), (1, 1)),
        # Zero items.
        (([], 4), (0, 1)),
        # Non-integer inputs
        ((ten, "4"), (10, 3)),
    )
    for params, output in tests:
        check_paginator(params, output)


def test_invalid_page_number():
    """
    Invalid page numbers result in the correct exception being raised.
    """
    paginator = Paginator([1, 2, 3], 2)
    with pytest.raises(InvalidPage):
        paginator.page(3)
    with pytest.raises(PageNotAnInteger):
        paginator.validate_number(None)
    with pytest.raises(PageNotAnInteger):
        paginator.validate_number("x")
    with pytest.raises(EmptyPage):
        paginator.validate_number(-1)
    with pytest.raises(EmptyPage):
        paginator.validate_number(3)


def test_float_integer_page():
    paginator = Paginator([1, 2, 3], 2)
    assert paginator.validate_number(1.0) == 1


def test_no_content_allow_empty_first_page():
    # With no content 1 is a valid page number
    paginator = Paginator([], 2)
    assert paginator.validate_number(1) == 1


def test_paginate_misc_classes():
    class CountContainer:
        def count(self):
            return 42

    # Paginator can be passed other objects with a count() method.
    paginator = Paginator(CountContainer(), 10)
    assert 42 == paginator.count
    assert 5 == paginator.num_pages

    # Paginator can be passed other objects that implement __len__.
    class LenContainer:
        def __len__(self):
            return 42

    paginator = Paginator(LenContainer(), 10)
    assert 42 == paginator.count
    assert 5 == paginator.num_pages


def test_count_does_not_silence_attribute_error():
    class AttributeErrorContainer:
        def count(self):
            raise AttributeError("abc")

    with pytest.raises(AttributeError):
        Paginator(AttributeErrorContainer(), 10).count()


def test_count_does_not_silence_type_error():
    class TypeErrorContainer:
        def count(self):
            raise TypeError("abc")

    with pytest.raises(TypeError):
        Paginator(TypeErrorContainer(), 10).count()


def test_get_page():
    """
    Paginator.get_page() returns a valid page even with invalid page
    arguments.
    """
    paginator = Paginator([1, 2, 3], 2)
    page = paginator.get_page(1)
    assert page.number == 1
    assert page.object_list == [1, 2]
    # An empty page returns the last page.
    assert paginator.get_page(3).number == 2
    # Non-integer page returns the first page.
    assert paginator.get_page(None).number == 1


def test_get_page_empty_object_list():
    """Paginator.get_page() with an empty object_list."""
    paginator = Paginator([], 2)
    # An empty page returns the last page.
    assert paginator.get_page(1).number == 1
    assert paginator.get_page(2).number == 1
    # Non-integer page returns the first page.
    assert paginator.get_page(None).number == 1


def test_page_repr():
    paginator = Paginator([1, 2, 3], 2)
    page = paginator.get_page(1)
    assert repr(page) == "<Page 1 of 2>"


def test_page_len():
    paginator = Paginator([1, 2, 3], 2)
    page = paginator.get_page(1)
    assert len(page) == 2


def test_page_getitem():
    paginator = Paginator([1, 2, 3], 2)
    page = paginator.get_page(1)
    assert page[0] == 1
    assert page[slice(0, 2)] == [1, 2]


def test_page_attrs():
    paginator = Paginator([1, 2, 3], 2)
    page = paginator.get_page(1)
    assert page.has_next
    assert page.next_page_number == 2
    assert page.has_previous is False
    assert page.has_other_pages

    with pytest.raises(EmptyPage):
        page.previous_page_number

    page = paginator.get_page(2)
    assert page.has_next is False
    assert page.previous_page_number == 1
    assert page.has_previous
    assert page.has_other_pages

    with pytest.raises(EmptyPage):
        page.next_page_number
