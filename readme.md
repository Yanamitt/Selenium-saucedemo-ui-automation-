# SauceDemo UI 自动化测试

本项目基于 **Python + Selenium + Pytest**，使用 Page Object Model 组织 SauceDemo 电商站点的 UI 自动化测试。项目覆盖登录失败校验和核心购物下单流程，并提供失败截图、失败日志、HTML 报告和 CI 执行入口。

## 技术栈

- Python 3.13
- Selenium WebDriver
- Pytest
- Pytest-HTML
- Page Object Model

## 项目结构

```text
base/                 # 页面对象基类，封装等待、点击、输入、读取文本
pages/                # 具体页面对象
tests/                # Pytest 测试用例
conftest.py           # 浏览器 fixture、失败截图、失败日志、HTML 报告增强
settings.py           # BASE_URL、BROWSER、HEADLESS、SELENIUM_TIMEOUT 配置
pytest.ini            # Pytest 默认运行参数
requirements.txt      # 项目最小依赖
```

## 覆盖场景

| 模块 | 用例 | 关键断言 |
| --- | --- | --- |
| 登录 | 锁定用户登录失败 | 校验 locked out 错误文案 |
| 登录 | 错误密码登录失败 | 校验账号密码不匹配错误文案 |
| 登录 | 空用户名登录失败 | 校验用户名必填错误文案 |
| 购物流程 | 登录、加购、购物车、结算、完成订单 | 校验页面跳转、商品名称、价格、购物车数量和完成订单文案 |

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
```

只运行登录失败用例：

```powershell
pytest tests/test_login.py -q -o addopts=
```

只运行端到端购物流程：

```powershell
pytest tests/test_e2e_flow.py -q -o addopts=
```

## 运行配置

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `BASE_URL` | `https://www.saucedemo.com/` | 被测站点地址 |
| `BROWSER` | `edge` | 支持 `edge`、`chrome`、`firefox` |
| `HEADLESS` | `false` | 设置为 `true` 后使用无头浏览器 |
| `SELENIUM_TIMEOUT` | `10` | 显式等待超时时间，单位秒 |

示例：

```powershell
$env:BROWSER = "chrome"
$env:HEADLESS = "true"
pytest
```

## 测试报告和失败诊断

默认运行 `pytest` 会生成：

- `report.html`：Pytest-HTML 自包含测试报告
- `screenshots/`：失败用例截图
- `failures.txt`：失败用例、失败阶段、当前 URL、截图路径、异常堆栈和浏览器日志

这些产物用于快速定位 UI 自动化失败原因，也可以作为后续“测试结果分析 Agent”的输入数据。

## CI

项目包含 GitHub Actions 配置：`.github/workflows/ui-tests.yml`。CI 会安装依赖并以 `HEADLESS=true` 运行测试，执行结束后上传 HTML 报告、失败截图和失败日志。
