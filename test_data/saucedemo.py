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


@dataclass(frozen=True)
class LoginSuccessExpectation:
    inventory_url_fragment: str
    page_title: str


@dataclass(frozen=True)
class InventorySortCase:
    case_id: str
    sort_value: str
    field: str
    reverse: bool


@dataclass(frozen=True)
class CheckoutValidationCase:
    case_id: str
    details: CheckoutDetails
    expected_error: str


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
    LoginFailureCase(
        case_id="missing-username",
        credentials=Credentials("", "secret_sauce"),
        expected_error="Epic sadface: Username is required",
    ),
    LoginFailureCase(
        case_id="missing-password",
        credentials=Credentials("standard_user", ""),
        expected_error="Epic sadface: Password is required",
    ),
    LoginFailureCase(
        case_id="unknown-user",
        credentials=Credentials("unknown_user", "secret_sauce"),
        expected_error=(
            "Epic sadface: Username and password do not match any user in this service"
        ),
    ),
)

STANDARD_LOGIN_EXPECTATION = LoginSuccessExpectation(
    inventory_url_fragment="inventory.html",
    page_title="Products",
)

INVENTORY_SORT_CASES = (
    InventorySortCase("name-a-to-z", "az", "name", False),
    InventorySortCase("name-z-to-a", "za", "name", True),
    InventorySortCase("price-low-to-high", "lohi", "price", False),
    InventorySortCase("price-high-to-low", "hilo", "price", True),
)

EXPECTED_INVENTORY_PRODUCT_NAMES = frozenset(
    {
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Bolt T-Shirt",
        "Sauce Labs Fleece Jacket",
        "Sauce Labs Onesie",
        "Test.allTheThings() T-Shirt (Red)",
    }
)

CART_EXPECTED_ADDED_COUNT = "1"
CHECKOUT_INFORMATION_URL_FRAGMENT = "checkout-step-one.html"

CHECKOUT_VALIDATION_CASES = (
    CheckoutValidationCase(
        case_id="first-name-required",
        details=CheckoutDetails("", "", ""),
        expected_error="Error: First Name is required",
    ),
    CheckoutValidationCase(
        case_id="last-name-required",
        details=CheckoutDetails("Test", "", ""),
        expected_error="Error: Last Name is required",
    ),
    CheckoutValidationCase(
        case_id="postal-code-required",
        details=CheckoutDetails("Test", "User", ""),
        expected_error="Error: Postal Code is required",
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
