# Structured Test Results Design

## Goal

为现有 Selenium + Pytest 项目建立稳定、按运行批次隔离的测试结果输出，使本地、CI 和后续测试结果分析 Agent 使用同一份数据契约。

## Scope

- 每次标准运行创建 `artifacts/<run_id>/`。
- 输出 `metadata.json`、`results.json`、`junit.xml`、`report.html`、`failures.txt` 和 `screenshots/`。
- 保留现有 4 条测试的步骤、数据和断言。
- 将现有失败截图和失败日志路由到本次运行目录。
- 提供跨平台 Python 运行入口，并让现有 GitHub Actions 使用该入口。

## Non-Goals

- 不修改 Page Object、等待策略或定位器。
- 不引入 Flow、测试数据层、测试标记或新业务用例。
- 不增加 Allure、数据库、PowerBI、Agent、并行执行或自动重试。
- 不修改或提交 `.understand-anything/`。

## Architecture

`scripts/run_tests.py` 是标准运行入口。它创建 `RunContext`，设置本次运行环境变量，并调用 Pytest，同时指定 HTML 和 JUnit XML 的输出位置。

标准入口还将 Pytest 临时目录放在本次运行目录内，运行结束后删除；`pytest.ini` 禁止递归扫描 `artifacts/` 等生成目录，避免历史产物被误收集为测试。

`reporting/run_context.py` 只负责运行 ID、UTC 时间和目录解析。`reporting/result_writer.py` 聚合 Pytest setup/call/teardown 三个阶段，生成一个稳定的测试级结果列表。`conftest.py` 负责把 Pytest report、失败截图和浏览器诊断传给结果收集器。

直接运行 `pytest` 仍然可用，并会生成 JSON 元数据和结果；标准入口额外保证 HTML 与 JUnit XML 同时进入同一运行目录。

## Artifact Layout

```text
artifacts/<run_id>/
  metadata.json
  results.json
  junit.xml
  report.html
  failures.txt
  screenshots/
```

`run_id` 使用 UTC 时间和短随机后缀，格式为 `YYYYMMDDTHHMMSSffffffZ-xxxxxxxx`，避免同一秒内运行冲突。

## Data Contract

`metadata.json` 包含：

- `schema_version`
- `run_id`
- `project`
- `started_at`
- `environment.base_url`
- `environment.browser`
- `environment.headless`
- `environment.selenium_timeout`
- `environment.python`
- `environment.platform`
- `environment.pytest`
- `environment.selenium`
- `git.commit`
- `git.branch`

`results.json` 包含运行时间、退出码、汇总计数和测试列表。每条测试包含：

- `nodeid`
- `name`
- `module`
- `markers`
- `outcome`
- `duration_seconds`
- `failure_phase`
- `failure_message`
- `screenshot`
- `phases`

最终结果优先级为 `error > failed > skipped > passed`。setup 或 teardown 失败记为 `error`，call 断言失败记为 `failed`。

## Error Handling

- 元数据中的 Git 信息无法读取时写入 `null`，不阻断测试。
- 浏览器日志或截图捕获失败时记录失败原因，不覆盖原测试结果。
- JSON 使用 UTF-8、两空格缩进和稳定字段名称。
- 即使没有收集到测试或 fixture setup 失败，也必须写出结果文件。

## Verification

- 单元测试验证运行 ID、目录解析、结果优先级、汇总计数和 UTF-8 JSON。
- 现有 4 条 UI 测试必须保持通过。
- 运行后校验六类产物存在，JSON 可解析，汇总为 4 passed。
- GitHub Actions 继续使用 Edge Headless，且上传整个 `artifacts/`。
