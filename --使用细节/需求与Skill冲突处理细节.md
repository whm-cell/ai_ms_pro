# 需求与 Skill 冲突处理细节

更新时间：2026-05-04

## 适用场景

当 PRD、REQ、WS 或实现过程中发现某个 repo-local skill 的建议不符合当前需求预期时，使用本文件。

典型例子：

- Godot 2D 游戏已有 `collision` / 碰撞实现模式 skill，但当前 PRD 需要新的碰撞体验。
- skill 建议使用通用 `Area2D` hitbox / hurtbox 模式，但当前关卡需要像素级碰撞、斜坡、单向平台或特殊攻击判定。
- skill 中的默认技术路线和当前验收标准冲突。

## 优先级

冲突时按以下顺序判断：

1. 当前 PRD / REQ / WS 验收真相优先。
2. 已采纳 ADR / status 中的长期决策其次。
3. skill 只是可复用方法建议，不拥有需求真相。

不要为了匹配 skill 去改写需求，也不要把当前需求状态藏进 skill。

## 处理流程

### 1. 先记录差异

把差异写回当前 `REQ/WS` 或任务技术方案：

- 当前需求需要什么行为。
- skill 建议是什么。
- 哪一条不符合当前验收标准。
- 本次偏离是否影响架构、测试或后续关卡。

### 2. 判断偏离类型

- 一次性偏离：留在当前 `REQ/WS` 或 handoff，不改 skill。
- 稳定新模式：用 `$prd-to-project-skills` 提炼为 Candidate skill 修订。
- 长期架构决策：提升到 ADR / status，例如“本项目采用 hitbox / hurtbox 分离模型”。
- 可验证规则：补检查脚本或 checklist，而不是只写进说明。

### 3. 实现前重跑方案 gate

如果冲突发生在非平凡功能开发中，使用 `$progressive-feature-development` 重跑技术方案 gate。

技术方案至少说明：

- 原 skill 哪条不适用。
- 为什么不适用。
- 本次采用的实现边界。
- `NOT Building`。
- 验证命令或人工验收方法。
- 是否需要更新 requirements、handoff、status、ADR、check 或 skill。

### 4. 修订 skill 时保留证据

如果确实要改 skill，先保持 Candidate 状态，并在 `docs/ai/skill-usage-samples.md` 记录 with/without eval。

有效样本必须说明：

- `baseline_without_skill`
- `run_with_skill`
- `delta`
- `acceptance`
- `verification`

没有真实样本时，不应把新规则升级为 always-on。

## Godot 碰撞示例

如果 PRD 写明“玩家攻击判定需要独立于受击判定，并且敌人弱点区域可单独受击”，而旧 skill 只建议单一 `CollisionShape2D`：

- `REQ/WS` 记录验收真相：攻击判定、受击判定、弱点区域的行为和验收方式。
- ADR 或 status 判断是否采纳长期模型：hitbox / hurtbox / weakpoint 分离。
- skill 只沉淀可复用实现方法：节点组织、signal 约定、测试 checklist。
- 技术方案写清楚旧 skill 的偏离原因和新的验证方法。

## 不应做的事

- 不要把“第一关的碰撞参数”写进 skill。
- 不要把“当前做到哪个碰撞任务”写进 skill。
- 不要因为 skill 已存在就忽略 PRD 的新验收标准。
- 不要在没有 eval 的情况下把新碰撞模式升级为默认 always-on 流程。

## 复查命令

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py
.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```
