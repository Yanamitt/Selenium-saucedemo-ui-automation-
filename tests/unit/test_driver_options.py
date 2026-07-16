from conftest import _build_options


def test_chrome_disables_password_manager_ui_that_can_block_page_clicks():
    options = _build_options("chrome", headless=True)

    assert "--disable-features=PasswordLeakDetection" in options.arguments
    assert options.experimental_options["prefs"] == {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    }
