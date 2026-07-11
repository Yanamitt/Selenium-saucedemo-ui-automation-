from dataclasses import dataclass

from flows.models import CheckoutDetails, Credentials


@dataclass(frozen=True)
class LoginFailureCase:
    case_id: str
    credentials: Credentials
    expected_error: str


@dataclass(frozen=True)
class ShoppingExpectation:
    inventory_url_fragment: str
    page_title: str
    product_name: str
    product_price: str
    cart_count: str
    cart_url_fragment: str
    checkout_information_url_fragment: str
    overview_url_fragment: str
    complete_url_fragment: str
    success_message: str


STANDARD_USER = Credentials("standard_user", "secret_sauce")
DEFAULT_CHECKOUT_DETAILS = CheckoutDetails("Test", "User", "12345")

LOGIN_FAILURE_CASES = (
    LoginFailureCase(
        case_id="locked-out-user",
        credentials=Credentials("locked_out_user", "secret_sauce"),
        expected_error="Epic sadface: Sorry, this user has been locked out.",
    ),
    LoginFailureCase(
        case_id="wrong-password",
        credentials=Credentials("standard_user", "wrong_pwd"),
        expected_error=(
            "Epic sadface: Username and password do not match any user in this service"
        ),
    ),
    LoginFailureCase(
        case_id="empty-username",
        credentials=Credentials("", ""),
        expected_error="Epic sadface: Username is required",
    ),
)

BACKPACK_ORDER_EXPECTATION = ShoppingExpectation(
    inventory_url_fragment="inventory.html",
    page_title="Products",
    product_name="Sauce Labs Backpack",
    product_price="$29.99",
    cart_count="1",
    cart_url_fragment="cart.html",
    checkout_information_url_fragment="checkout-step-one.html",
    overview_url_fragment="checkout-step-two.html",
    complete_url_fragment="checkout-complete.html",
    success_message="Thank you for your order!",
)
