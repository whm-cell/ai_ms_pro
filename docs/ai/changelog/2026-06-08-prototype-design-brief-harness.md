# Prototype Design Brief Harness

更新时间：2026-06-08
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 opt-in `[prototype_design_brief]` harness 配置，默认关闭。
- 新增 `scripts/check_prototype_design_brief.py`，用于检查 Prototype Design Brief 的必填章节、关键语义门槛、Source Truth 绑定、REQ/WS/ADR 漂移和本地链接。
- 新增 `scripts/check_prototype_artifact_review.py`，用于检查配置的 prototype artifact package、prototype route/source file、required states、truth boundary、surface identity、non-production boundary 和工具无关性。
- 新增通用 [Prototype Design Brief 模板](../templates/prototype-design-brief.md)。

## 修复问题

- 将外部项目中已经验证过的原型设计投影闭环抽取为通用 harness 机制，避免后续原型工作只靠 prompt 或 runtime session 记忆。
- 保持机制层和项目真相层分离：不复制 `demo_txt_t_proto` 的小红书业务需求、原型页面、fixture、runtime session 或 accepted evidence。

## 行为变化

- `check_ai_governance.py` 会在 `[prototype_design_brief].enabled = true` 时追加 brief child check，在 `artifact_review_enabled = true` 时追加 artifact child check。
- `check_change_triggered_followups.py` 现在会把 prototype brief/template/artifact/checker 变更路由到 prototype follow-up。
- 当前 repo 的 `.codex/harness.toml` 显式登记该 feature，但保持 disabled。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_config.py`
- `python3 tests/test_prototype_design_brief.py`
- `python3 tests/test_prototype_artifact_review.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_prototype_design_brief.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_prototype_artifact_review.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## 关联文档

- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Check Registry](../check-registry.md)
- [AI 文档入口索引](../index.md)
