# Trace Remote Interop Report

更新时间：2026-06-03
状态：bounded pilot evidence

## Purpose

`trace-remote-interop-report/v1` 用来记录一次 bounded OTLP probe 的结果，
并明确区分：

- `local-only`
- `pilot-remote`
- `verified-remote`

它的作用是让仓库能机器可读地表达“这次是否真的发起了 remote probe，以及 claim 到哪一级”，而不是把 local adapter、localhost capture 或单次 pilot 混写成“已完成远端互通”。

## Files

- sample: `docs/ai/standards/trace-remote-interop-report.sample.json`
- probe script: `scripts/verify_remote_trace_interop.py`
- validator: `scripts/check_remote_trace_interop_report.py`
- tests: `tests/test_remote_trace_interop.py`

## Capability Levels

- `local-only`
  - 不发网络请求
  - 只证明本地 adapter/export shape
- `pilot-remote`
  - 发起一次 bounded remote probe
  - 记录 endpoint scope、HTTP status、trace mapping、failure mode 和 withheld payload class
  - 不自动声明广义 external interoperability
- `verified-remote`
  - 仅在成功 probe 之后，且经额外 operator review 时使用
  - 仍只证明该 endpoint scope 的 bounded remote evidence
  - 不自动外推到 OpenAI hosted trace、MCP、A2A 或所有 collector

## Structured Evidence

Report 同时保留顶层兼容字段，并新增 4 个结构化 evidence 面：

- `export_attempt`：记录是否显式 `--send`、是否发生 network export、timeout 和 export format。
- `endpoint_evidence`：记录 endpoint scope、endpoint 是否配置、是否 localhost、failure mode。
- `claim_evidence`：记录是否需要 / 已确认 operator review，以及 claim boundary。
- `withheld_payloads`：记录被刻意 withheld 的 payload class，例如 raw trace payload、request body、response body、prompt、transcript 和 secret。

## Boundary

- report 不记录 raw trace payload、request/response body、prompt、transcript、secret 或 raw runtime path。
- local capture server 不能被标为 `verified-remote`。
- `verified-remote` 必须同时具备 `network_exported=true`、`remote_status.ok=true`、非 local capture endpoint scope 和 `claim_evidence.operator_review_confirmed=true`。
- 该 report 是 bounded interop evidence，不是 capability completion certificate。

## Validation

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_remote_trace_interop_report.py
python3 tests/test_remote_trace_interop.py
```
