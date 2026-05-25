# Godot PRD 技术边界与业务范围

更新时间：2026-05-21
需求编号：REQ-009
来源文档：REQDOC-003
需求标题：Godot PRD 技术边界与业务范围
状态：已完成

## 背景

- REQDOC-003 包含 Godot、素材生成、音频、本地化、测试插件和 CI 导出建议。
- 这些内容中有一部分是产品需求，有一部分是 proposed 工程前提；WS-03 历史 smoke 只验证过薄切片，真实 Godot spike / ADR 采纳前不能写成已采纳架构事实。

## 目标

- 明确首轮实现边界：本轮只验证可追踪的业务切片，不采纳完整 Godot 工程方案。

## 范围

### 包含

- 保留 Godot 4.6.2、Compatibility renderer、GUT、导出 preset 等为 proposed / 待确认；验证方式：后续 Godot engine spike、Godot smoke 与 ADR 采纳。
- 明确首轮切片曾使用 repo-native 浏览器实现服务 harness 验证；当前 active harness capability validation 已回到 WS-01 Three.js Snake。
- 将后续 Godot engine spike、素材管线、存档、本地化和导出流水线排入未来候选范围。

### 不包含

- 创建 Godot 项目目录。
- 引入 Godot 二进制、插件或导出模板。
- 把 REQDOC-003 中的外部工具建议升级成 ADR。

## 验收条件

- REQDOC-003 在 requirements index 中不再是未绑定状态。
- WS-03 文档明确 Godot engine 相关工程前提仍未采纳。
- traceability matrix 对 REQ-009 给出验证方式和当前边界。

## 依赖与前置条件

- 后续是否真正采用 Godot，需要用户确认目标平台、工程位置和可用本地 Godot 版本。

## 风险与待澄清项

- 若后续直接把完整 Godot 业务塞入 root repo，可能干扰 harness 研究目标。
- 推荐在 root repo 保留薄切片验证；完整游戏工程可使用 `new_pro_standard` 机制层另起仓库。

## 关联工作流

- WS-03：Godot Platformer First Slice

## 关联阶段

- STAGE-00：真实场景验证与治理固化
