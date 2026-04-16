# 项目计划

更新时间：2026-04-16
项目状态：进入真实场景验证

## 项目目标

- 用真实业务场景验证当前 Codex-first harness 的可行性
- 落地一个可运行的 Three.js 贪吃蛇 MVP
- 跑通 `requirements -> implementation -> runtime memory -> handoff/status` 的最小闭环

## 范围定义

### 当前范围

- 导入首个真实需求场景 `REQDOC-001 / WS-01`
- 实现一个桌面浏览器可玩的 Three.js 贪吃蛇
- 继续强化 runtime harness、governance harness 和 requirements traceability 的协同

### 暂不纳入范围

- 多人模式、联网、排行榜
- 部署上线、域名和正式运营能力
- 音效、复杂特效、移动端深度适配

## 业务线索与模块划分

### 核心业务线索

- 真实需求导入与 traceability
- Three.js 贪吃蛇 MVP 实现
- runtime observation / reducer / handoff / status 压缩验证

### 模块划分

- `docs/requirements/`：原始需求、标准化需求、工作流和追踪矩阵
- `docs/ai/`：执行计划、handoff、status、ADR 和 working context
- `apps/threejs-snake/`：Three.js 贪吃蛇应用实现
- `.codex/runtime/`：session、observation 和 reducer 原料

## 阶段规划

### 第 0 阶段：规划与骨架

- 目标：完成 harness 骨架、引入首个真实需求场景并落下最小可运行垂直切片
- 验收：形成 requirements 体系、首批 ADR、首个阶段 status 和可运行场景

### 第 1 阶段：核心基础设施

- 目标：基于真实样本收紧 traceability、一致性校验和 reducer 压缩策略
- 验收：metadata 与 traceability matrix 的同步规则稳定，治理脚本可继续增强

### 第 2 阶段：核心业务流程

- 目标：在更多真实功能切片上复用已验证的 harness 流程
- 验收：不止一个 workstream 能稳定走通 requirements -> implementation -> status/adr

### 第 3 阶段：测试、优化与上线准备

- 目标：接入 CI、补齐更强校验和必要的发布准备
- 验收：文档漂移与 traceability 漏更能在合并前被拦下

## 技术与架构决策

- runtime / governance / verification 三层 harness 已采纳
- requirements traceability 采用 `REQDOC -> REQ -> WS -> STAGE` 结构
- 首个真实前端场景采用轻量方式接入，用于验证 harness，而不是先追求完整工程化

## 风险与约束

- 当前仓库没有既有应用工程，真实场景接入路径仍需在本轮验证
- requirement/workstream metadata 规则已建立，但还缺真实任务样本验证
- reducer 目前以 handoff-first 为主，status/ADR 压缩阈值仍需用真实 observation 数据校正

## 文档治理约定

- 子任务完成后生成 `handoff`
- 阶段结束后生成 `status`
- 准备联调、合并或发版前生成 `changelog`
- 长期有效决策写入 `adr`
- 阶段文档更新后检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
