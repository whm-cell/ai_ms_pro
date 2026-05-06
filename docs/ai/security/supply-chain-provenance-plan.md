# Supply Chain And Provenance Plan

更新时间：2026-05-05
状态：已确认

## 作用

本文件定义 Stage-00 之后的供应链证据路线。当前目标是可见性和证据收集，不把 Scorecard、CodeQL、SBOM 或 SLSA provenance 立即升级为 blocking gate。

## 当前策略

- OpenSSF Scorecard：通过 `Security Evidence` workflow 生成 SARIF artifact，先观察分数和建议。
- CodeQL：覆盖 Python 与 JavaScript / TypeScript；当前作为 advisory step 生成 SARIF artifact，使用 `upload: never`，避免 private repo 未启用 code scanning 时把证据层变成红叉。
- SBOM：通过 Syft / Anchore action 生成 CycloneDX JSON artifact，先作为 release 前证据。
- Scorecard、CodeQL、SBOM 在同一个 `security-evidence` job 内顺序执行，避免小型或私有仓库 CI 配额下多个 advisory jobs 排队超时。
- SLSA / provenance：当前还没有正式 release artifact，因此先定义产物证明模型，不强制生成 provenance。

## Provenance 模型

当项目开始发布可交付 artifact 时，每个 artifact 至少记录：

- build entrypoint：构建命令或 workflow job
- source revision：commit SHA 与 tag
- artifact identity：文件名、类型、用途
- artifact digest：SHA-256 或等价 hash
- SBOM location：workflow artifact 或 release attachment
- attestation location：SLSA provenance、GitHub artifact attestation 或签名文件

## 升级条件

- Scorecard / CodeQL / SBOM 至少经过两轮 PR 或 scheduled burn-in。
- 失败能指向明确修复路径，而不是平台权限、code scanning 未启用或仓库可见性限制。
- 若要升级为 blocking，必须新增 ADR，并同步 `check-registry.md`。
