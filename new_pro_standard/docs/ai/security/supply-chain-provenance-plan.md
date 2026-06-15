# Supply Chain And Provenance Plan

更新时间：2026-05-09
状态：已确认

## 作用

本文件定义 Stage-00 之后的供应链证据路线。当前目标是可见性和证据收集，不把 Scorecard、CodeQL、SBOM、GitHub artifact attestation 或 SLSA provenance 立即升级为 blocking gate。

## 当前策略

- OpenSSF Scorecard：通过 `Security Evidence` workflow 生成 SARIF artifact，先观察分数和建议。
- CodeQL：覆盖 Python 与 JavaScript / TypeScript；当前作为 advisory step 生成 SARIF artifact，使用 `upload: never`，并把 private repo 未启用 code scanning 时产生的上传注解登记到 triage，而不是把证据层变成 required gate 失败。
- SBOM：通过 Syft / Anchore action 生成 CycloneDX JSON artifact，先作为 release 前证据。
- Scorecard、CodeQL、SBOM 在同一个 `security-evidence` job 内顺序执行，避免小型或私有仓库 CI 配额下多个 advisory jobs 排队超时。
- SLSA / provenance：当前还没有正式 release artifact，因此先定义产物证明模型，不强制生成 provenance。
- Evidence triage：审阅节奏、owner 占位、严重度和 issue / blocking 升级规则见 [Security Evidence Triage](./security-evidence-triage.md)。

## Provenance 模型

当项目开始发布可交付 artifact 时，每个 artifact 至少记录：

- build entrypoint：构建命令或 workflow job
- source revision：commit SHA 与 tag
- artifact identity：文件名、类型、用途
- artifact digest：SHA-256 或等价 hash
- SBOM location：workflow artifact 或 release attachment
- attestation location：SLSA provenance、GitHub artifact attestation 或签名文件；当前 Private GitHub Free 下可记录为 `not generated / plan-limited`

## Private GitHub Free Attestation 边界

根据 GitHub Docs，GitHub Free / Pro / Team 下 artifact attestations 只适用于 public repositories；private 或 internal repositories 需要 GitHub Enterprise Cloud。当前仓库是 private 且处于 GitHub Free 边界内，因此：

- GitHub artifact attestation 不作为当前完成条件、required gate 或 release blocker。
- 不能把缺少 attestation 记录为本地工程缺口；它是 plan / visibility 边界。
- 不新增 `actions/attest-build-provenance`、`actions/attest-sbom` 或远端 attestation 验证要求，除非仓库改 public 或升级到支持 private attestation 的计划。
- 如果未来计划或可见性变化，再通过 ADR / status 明确启用条件、验证命令和 required gate 关系。

## Release 前临时 Provenance 记录

在 artifact attestation 可用前，release 准备阶段至少记录：

- source revision：commit SHA、tag、branch 或 PR 链接
- build entrypoint：workflow job、脚本或手动构建命令
- artifact identity：文件名、类型、用途
- artifact digest manifest：每个 artifact 的 SHA-256 或等价 hash
- SBOM location：CycloneDX artifact、release attachment 或重新生成命令
- verification note：说明当前未生成 GitHub artifact attestation 的原因是 Private GitHub Free plan boundary

## 升级条件

- Scorecard / CodeQL / SBOM 至少经过两轮 PR 或 scheduled burn-in。
- 失败能指向明确修复路径，而不是平台权限、code scanning 未启用或仓库可见性限制。
- CodeQL 若继续产生 code scanning / database upload 注解，先按 security evidence triage 记录；只有在启用 code scanning、升级计划或改 public 后，才把远端上传状态纳入升级判断。
- 若要升级为 blocking，必须新增 ADR，并同步 `check-registry.md`。
- 若要把 GitHub artifact attestation 纳入完成条件，必须先确认仓库计划 / 可见性支持 private attestation，并补充 release verification 流程。

## External References

- GitHub Docs: [Using artifact attestations to establish provenance for builds](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
