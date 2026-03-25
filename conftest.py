import pytest
from selenium import webdriver
import os
from datetime import datetime

@pytest.fixture(scope="function")
def driver():
    # 使用 Edge 浏览器
    options = webdriver.EdgeOptions()
    # options.add_argument("--headless") # 如果不想看到浏览器界面，可以取消注释
    options.add_argument("--start-maximized")
    
    driver = webdriver.Edge(options=options)
    yield driver
    driver.quit() # 测试结束后清理环境

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # 执行测试步骤
    outcome = yield
    report = outcome.get_result()
    
    # 仅在测试用例执行阶段（call）失败时截图
    if report.when == 'call' and report.failed:
        mode = "a" if os.path.exists("failures.txt") else "w"
        with open("failures.txt", mode) as f:
            if "driver" in item.fixturenames:
                web_driver = item.funcargs['driver']
                # 创建 screenshots 文件夹
                if not os.path.exists("screenshots"):
                    os.makedirs("screenshots")
                
                # 以用例名+时间命名图片
                file_name = f"screenshots/{item.name}_{datetime.now().strftime('%H%M%S')}.png"
                web_driver.save_screenshot(file_name)
                
                # 将截图嵌入到 pytest-html 报告中
                if file_name:
                    html = '<div><img src="%s" alt="screenshot" style="width:304px;height:228px;" ' \
                           'onclick="window.open(this.src)" align="right"/></div>' % file_name
                    extra = getattr(report, 'extra', [])
                    extra.append(pytest_html.extras.html(html))
                    report.extra = extra

# 注意：为了让截图嵌入生效，开头需要引入 pytest_html（如果没安装会报错）
try:
    import pytest_html
except ImportError:
    pytest_html = None    