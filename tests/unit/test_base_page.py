from unittest.mock import Mock

import pytest

from base.base_page import BasePage


@pytest.fixture
def page():
    instance = BasePage.__new__(BasePage)
    instance.driver = Mock(current_url="https://example.test/inventory.html")
    instance.wait = Mock()
    return instance


@pytest.mark.parametrize(
    ("method_name", "condition_name", "argument"),
    [
        ("wait_for_presence", "presence_of_element_located", ("id", "status")),
        ("wait_for_visibility", "visibility_of_element_located", ("id", "status")),
        ("wait_for_clickable", "element_to_be_clickable", ("id", "submit")),
        ("wait_for_invisibility", "invisibility_of_element_located", ("id", "spinner")),
        (
            "wait_for_all_visible",
            "visibility_of_all_elements_located",
            ("css selector", "[data-test='item']"),
        ),
        ("wait_for_url_contains", "url_contains", "inventory.html"),
    ],
)
def test_wait_method_uses_matching_expected_condition(
    monkeypatch, page, method_name, condition_name, argument
):
    condition = object()
    condition_factory = Mock(return_value=condition)
    expected_result = object()
    page.wait.until.return_value = expected_result
    monkeypatch.setattr(
        f"base.base_page.EC.{condition_name}",
        condition_factory,
    )

    result = getattr(page, method_name)(argument)

    condition_factory.assert_called_once_with(argument)
    page.wait.until.assert_called_once_with(condition)
    assert result is expected_result


def test_find_delegates_to_visibility_wait(page):
    locator = ("id", "username")
    element = object()
    page.wait_for_visibility = Mock(return_value=element)

    assert page.find(locator) is element
    page.wait_for_visibility.assert_called_once_with(locator)


def test_click_waits_until_element_is_clickable(page):
    locator = ("id", "submit")
    element = Mock()
    page.wait_for_clickable = Mock(return_value=element)

    page.click(locator)

    page.wait_for_clickable.assert_called_once_with(locator)
    element.click.assert_called_once_with()


def test_input_text_and_get_text_use_visibility_wait(page):
    input_locator = ("id", "username")
    label_locator = ("id", "message")
    input_element = Mock()
    label_element = Mock(text="Ready")
    page.wait_for_visibility = Mock(side_effect=[input_element, label_element])

    page.input_text(input_locator, "standard_user")
    text = page.get_text(label_locator)

    assert page.wait_for_visibility.call_args_list == [
        ((input_locator,),),
        ((label_locator,),),
    ]
    input_element.clear.assert_called_once_with()
    input_element.send_keys.assert_called_once_with("standard_user")
    assert text == "Ready"


def test_current_url_returns_driver_url(page):
    assert page.current_url() == "https://example.test/inventory.html"
