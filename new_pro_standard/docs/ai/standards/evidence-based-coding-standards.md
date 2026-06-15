# Evidence-Based Coding Standards

更新时间：2026-06-12
状态：review-required

## 作用

本标准用于非平凡实现、review 和 refactor 时判断魔法值、复杂度、重复、命名和公共抽象边界。它补充 `check_code_shape.py` 的体量预算，但不替代现有 Ruff `E9/F`、`git diff --check` 或 code-shape gates。

治理原则：以可理解、可修改、可测试为目标；不要把“零魔法值、零重复、必须抽公共类”写成绝对规则。

## 证据边界

- ISO/IEC 25010:2023 定义了产品质量模型，可用于需求、设计目标、测试目标、质量控制和验收标准，本文把编码标准对齐到可维护性相关目标，而不是单一风格偏好。来源：https://www.iso.org/standard/78176.html
- Buse / Weimer 的可读性研究基于人工标注样本建立局部代码特征与可读性的关系，支持把命名、局部结构和信息密度作为 review 信号。来源：https://web.eecs.umich.edu/~weimerw/p/weimer-tse2010-readability-preprint.pdf
- Palomba 等人的 code smell 大规模实证研究把 long / complex code smell 与 change-proneness、fault-proneness 关联起来，但它仍是风险信号，不等于所有 smell 必须机械重写。来源：https://link.springer.com/article/10.1007/s10664-017-9535-z
- code duplication 的 structured review 说明重复代码有害性并非无条件成立；重复是否应抽取要看同步修改风险、语义一致性和耦合成本。来源：https://research.utwente.nl/en/publications/harmfulness-of-code-duplication-a-structured-review-of-the-evidence
- NASA NESC 对 cyclomatic complexity / basis path testing 的研究说明复杂度指标可作为安全关键系统审查信号，但学术证据存在 mixed 结果；因此复杂度先作为 review-required / blocking-candidate，而不是默认阻断。来源：https://ntrs.nasa.gov/citations/20205011566
- Ruff rules 可作为 Python 自动化候选，但本轮只登记候选方向。来源：https://docs.astral.sh/ruff/rules/magic-value-comparison/、https://docs.astral.sh/ruff/rules/complex-structure/、https://docs.astral.sh/ruff/rules/too-many-branches/、https://docs.astral.sh/ruff/rules/too-many-statements/
- ESLint `no-magic-numbers` 可作为未来 JS/TS 自动化候选，但需要忽略配置和误报样本。来源：https://eslint.org/docs/latest/rules/no-magic-numbers
- Google Engineering Practices 的 code review 指南把设计、复杂度、测试、命名、注释、风格和文档列为 review 面，并明确不应追求完美、个人风格建议应标为非阻断。来源：https://google.github.io/eng-practices/review/reviewer/looking-for.html、https://google.github.io/eng-practices/review/reviewer/standard.html
- Conventional Comments 提供 review feedback 标签格式，可用于把 `issue`、`suggestion`、`nitpick` 与 blocking / non-blocking 语义说清楚。来源：https://conventionalcomments.org/

## Review 严重度与处置

- High：影响正确性、安全、权限、金额、协议、数据持久化、发布、用户可见行为，或导致未来 bugfix 需要多处同步修改。默认需要本轮修复或明确记录延期理由。
- Medium：影响核心路径可读性、公开 API / schema 命名、单位语义、职责边界、测试可维护性。默认本轮修复；若延期，需说明风险可控。
- Low：局部可读性、命名偏弱、测试 fixture 字面量、小范围重复或风格 polish。可作为 `nit` / non-blocking 记录，不因 Low alone 阻塞。
- 处置标签：review 结论应归入 `checked`、`fixed`、`deferred with rationale` 或 `no material issue`，避免 `review-required` 退化成不可审计的口头承诺。

## 标准

### 1. 魔法值命名

- 规则：业务阈值、协议码、状态码、重试次数、超时、尺寸、坐标、容量、评分、概率和单位相关数字默认应命名为常量、枚举、配置字段或领域对象；保留字面量时应属于例外或有局部理由。
- 适用范围：生产代码、harness 脚本、smoke/checker、重要测试 helper。
- 例外：`0`、`1`、`-1`、空字符串、布尔式长度判断、短小循环步进、局部测试 fixture 中明显数据、标准库约定值。
- 证据来源：可读性研究、Ruff `PLR2004`、ESLint `no-magic-numbers`。
- 自动化可行性：Python 可先试跑 Ruff `PLR2004`；TS/JS 后续可评估 ESLint `no-magic-numbers`。两者都需要 ignore 配置和误报样本。
- 治理等级：review-required；候选 lint 为 blocking-candidate，不在本轮启用。

### 2. 复杂度控制

- 规则：新增或修改函数出现深层嵌套、长 `if/elif` 链、过多 `match/case`、多层异常分支或难以覆盖的路径时，优先用数据表、早返回、小函数、策略对象或边界拆分降低理解成本。
- 适用范围：Python、TS/TSX、Rust、SQL 生成/迁移脚本和 harness checker。
- 例外：小型解析器、明确枚举协议映射、性能关键热路径或测试矩阵；例外应有局部注释或 review 说明。
- 证据来源：code smell 实证研究、NASA complexity study、Ruff `C901` / `PLR0912` / `PLR0915`。
- 自动化可行性：Python 可把 `C901`、`PLR0912`、`PLR0915` 作为 dry-run / advisory 样本收集；阈值需按本 repo 误报率校准。
- 治理等级：review-required；复杂度 lint 为 blocking-candidate。

### 3. 长函数和大类职责

- 规则：超过 code-shape warning 的函数、方法或类必须检查职责是否混杂；I/O、解析、业务规则、验证、渲染、持久化和 reporting 不应无界堆在同一函数或类。
- 适用范围：所有 `.codex/code_shape.toml` 覆盖的代码面。
- 例外：legacy 大文件可作为独立技术债处理；当前任务不得顺手重写无关 legacy。
- 证据来源：现有 code-shape budget、code smell 实证研究。
- 自动化可行性：现有 `check_code_shape.py` 已覆盖文件、Python 函数和 Python 类行数；TS/TSX、JS/JSX/MJS/CJS、CSS/SCSS、SQL、Rust、shell 和 PowerShell 当前主要按文件行数检查。职责混杂仍由 review 判断。
- 治理等级：code-shape 等级跟随 `docs/ai/check-registry.md` 的当前登记；职责混杂 review 为 review-required。

### 4. 重复代码风险分级

- 规则：重复片段只有在同一领域概念、未来变化方向一致、bugfix 需要同步修改、抽取后依赖更清晰时，才应抽取为共享函数、常量、类型或类。
- 适用范围：业务逻辑、协议处理、checker 规则、schema/contract 解析和测试 helper。
- 例外：语义不同但结构相似、隔离不同外部协议、一次性迁移、短期实验、降低跨模块耦合的 intentional duplication。
- 证据来源：code duplication structured review 和 clone patterns 研究均提示重复代码不应机械消除。
- 自动化可行性：不启用通用 clone blocker；可在后续用局部脚本检查特定 registry / enum / warning-code 对齐。
- 治理等级：review-required。

### 5. 命名清晰度

- 规则：变量、函数、类、常量和文件名要表达领域意图；数值和时间相关名称必须带单位或维度，例如 `_ms`、`_px`、`max_`、`min_`、`count`。
- 适用范围：新增公开 API、配置、schema 字段、checker 输出、测试 fixture 名称。
- 例外：短小局部 lambda、标准循环变量、数学公式中通用符号。
- 证据来源：可读性研究把局部代码特征与人工可读性判断关联起来；命名是 review 中可稳定判断的低成本信号。
- 自动化可行性：只做 review；暂不引入命名 lint。
- 治理等级：review-required。

### 6. 公共抽象触发条件

- 规则：公共函数、公共类或 helper 的抽取至少满足两个真实调用点、同一领域概念、变化方向一致、抽取后分支更少或依赖更清晰，并且有相应测试或 smoke 覆盖。
- 适用范围：跨模块 helper、公共 checker 工具、shared constants、service / adapter 抽象。
- 例外：当前只有一个调用点、抽取后需要大量 flags、名字退化为 `common` / `util` / `helper` / `manager`、或会把不同边界强行耦合。外部 API、schema contract、framework lifecycle hook、跨进程协议边界可以早于两个调用点抽象，但必须说明来源边界和测试证据。
- 证据来源：重复代码证据边界和现有 repo-governed-coding 的 simplicity / surgical change 原则。
- 自动化可行性：不做机械检查；review 时必须说明抽取理由或保留局部实现的理由。
- 治理等级：review-required。

## 落地规则

- 非平凡实现、review、refactor 或 harness checker 变更时，使用 `$repo-governed-coding` 并读取其 evidence-based checklist。
- 本轮不修改 `pyproject.toml`、ESLint 配置或 CI workflow 来启用新 lint。
- 若后续要把候选 lint 升级为 blocking，必须先进入 `docs/ai/check-registry.md` 和 burn-in ledger，记录至少两次真实样本、误报率、修复路径、CI 成本和 reviewer 负担。
- 若标准与当前业务需求冲突，按任务局部说明；若冲突会长期存在，写入 status 或 ADR。
