# Trace Remote Interop Report

更新时间：2026-06-01
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
  - 记录 endpoint scope、HTTP status、trace mapping
  - 不自动声明广义 external interoperability
- `verified-remote`
  - 仅在成功 probe 之后，且经额外 operator review 时使用
  - 仍只证明该 endpoint scope 的 bounded remote evidence
  - 不自动外推到 OpenAI hosted trace、MCP、A2A 或所有 collector

## Boundary

- report 不记录 raw trace payload、request/response body、prompt、transcript、secret 或 raw runtime path。
- local capture server 不能被标为 `verified-remote`。
- 该 report 是 bounded interop evidence，不是 capability completion certificate。

## Validation

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_remote_trace_interop_report.py
python3 tests/test_remote_trace_interop.py
```
