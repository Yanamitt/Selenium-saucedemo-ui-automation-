from dataclasses import dataclass


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


@dataclass(frozen=True)
class CheckoutDetails:
    first_name: str
    last_name: str
    postal_code: str


@dataclass(frozen=True)
class ShoppingFlowResult:
    inventory_url: str
    page_title: str
    product_name: str
    product_price: str
    cart_count: str
    cart_url: str
    cart_item_name: str
    cart_item_price: str
    checkout_information_url: str
    overview_url: str
    overview_item_name: str
    overview_item_price: str
    complete_url: str
    success_message: str


@dataclass(frozen=True)
class LoginSuccessResult:
    inventory_url: str
    page_title: str


@dataclass(frozen=True)
class InventorySortResult:
    product_names: tuple[str, ...]
    product_prices: tuple[str, ...]


@dataclass(frozen=True)
class CartToggleResult:
    added_count: str
    badge_removed: bool


@dataclass(frozen=True)
class CheckoutValidationResult:
    checkout_url: str
    error_message: str
