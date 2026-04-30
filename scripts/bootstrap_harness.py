#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

from hook_config_lib import render_hooks_config as render_platform_hooks_config


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VENV_DIR = ROOT / ".codex" / ".venv"
DEFAULT_REQUIREMENTS_PATH = ROOT / ".codex" / "requirements.txt"


def is_windows_host() -> bool:
    return os.name == "nt"


def python_candidates(prefix: Path) -> list[Path]:
    candidates: list[Path] = []
    if is_windows_host():
        candidates.extend(
            [
                prefix / "Scripts" / "python.exe",
                prefix / "Scripts" / "python",
            ]
        )
    candidates.extend(
        [
            prefix / "bin" / "python",
            prefix / "bin" / "python3",
            prefix / "python.exe",
            prefix / "python",
        ]
    )
    return candidates


def resolve_existing_python(prefix: Path) -> Path | None:
    for candidate in python_candidates(prefix):
        if candidate.exists():
            return candidate
    return None


def common_windows_python_candidates() -> list[Path]:
    if not is_windows_host():
        return []

    roots: list[Path] = []
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        roots.append(Path(local_appdata) / "Programs" / "Python")

    candidates: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for prefix in sorted(root.glob("Python*"), reverse=True):
            candidate = prefix / "python.exe"
            if candidate.exists():
                candidates.append(candidate)
    return candidates


def is_runnable_python(command: list[str]) -> bool:
    return python_version(command) is not None


def python_version(command: list[str]) -> tuple[int, int, int] | None:
    try:
        result = subprocess.run(
            [
                *command,
                "-c",
                "import sys; print('%d.%d.%d' % sys.version_info[:3])",
            ],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    parts = result.stdout.strip().split(".")
    if len(parts) != 3:
        return None
    try:
        return tuple(int(part) for part in parts)  # type: ignore[return-value]
    except ValueError:
        return None


def all_commands_on_path(name: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()
    candidate_names = path_candidate_names(name)
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        for candidate_name in candidate_names:
            candidate = Path(directory) / candidate_name
            rendered = str(candidate)
            if rendered in seen:
                continue
            if candidate.is_file() and is_executable_command(candidate):
                candidates.append(rendered)
                seen.add(rendered)
    return candidates


def path_candidate_names(name: str) -> list[str]:
    if not is_windows_host() or command_name_has_suffix(name):
        return [name]

    extensions = [".exe", ".cmd", ".bat", ".com"]
    raw_pathext = os.environ.get("PATHEXT", "")
    for extension in raw_pathext.replace(";", os.pathsep).split(os.pathsep):
        normalized = extension.strip().lower()
        if normalized and normalized not in extensions:
            extensions.append(normalized)

    return [name, *[f"{name}{extension}" for extension in extensions]]


def command_name_has_suffix(name: str) -> bool:
    basename = name.replace("\\", "/").rsplit("/", 1)[-1]
    return "." in basename


def is_executable_command(candidate: Path) -> bool:
    if is_windows_host():
        return candidate.is_file()
    return candidate.is_file() and os.access(candidate, os.X_OK)


def best_python_command(commands: list[list[str]]) -> list[str] | None:
    runnable: list[tuple[int, tuple[int, int, int], list[str]]] = []
    for index, command in enumerate(commands):
        version = python_version(command)
        if version is not None:
            runnable.append((index, version, command))
    if not runnable:
        return None
    preferred = [item for item in runnable if item[1] >= (3, 11, 0)]
    pool = preferred or runnable
    _, _, command = max(pool, key=lambda item: (item[1], -item[0]))
    return command


def expected_repo_venv_python() -> Path:
    return python_candidates(DEFAULT_VENV_DIR)[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap a minimal Codex-first harness control plane for a new repository.",
    )
    parser.add_argument(
        "--project-name",
        default="New Project",
        help="Project name used in starter documents. Default: New Project.",
    )
    parser.add_argument(
        "--stage-label",
        default="STAGE-00",
        help="Initial stage label for starter docs. Default: STAGE-00.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing starter files if they already exist.",
    )
    parser.add_argument(
        "--skip-venv",
        action="store_true",
        help="Skip creating or refreshing the repo-local Python virtual environment.",
    )
    parser.add_argument(
        "--python",
        help="Explicit Python executable to use for creating the repo-local virtual environment.",
    )
    parser.add_argument(
        "--strict-python-deps",
        action="store_true",
        help="Fail bootstrap when Python dependency installation fails. Default behavior is best-effort.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_directories()

    files = {
        ROOT / ".codex" / "harness.toml": render_harness_config(),
        ROOT / ".codex" / "requirements.txt": render_requirements_txt(),
        ROOT / ".codex" / "hooks.json": render_hooks_config(),
        ROOT / "docs" / "ai" / "index.md": render_ai_index(args.project_name, args.stage_label),
        ROOT / "docs" / "ai" / "plan.md": render_plan(args.project_name, args.stage_label),
        ROOT / "docs" / "ai" / "working-context.md": render_working_context(args.project_name, args.stage_label),
        ROOT / "docs" / "requirements" / "index.md": render_requirements_index(),
        ROOT / "docs" / "requirements" / "traceability-matrix.md": render_traceability_matrix(),
    }
    bootstrap_prerequisites = [
        ROOT / ".codex" / "harness.toml",
        ROOT / ".codex" / "requirements.txt",
    ]

    for path in bootstrap_prerequisites:
        content = files[path]
        if path.exists() and not args.force:
            continue
        path.write_text(content, encoding="utf-8")

    if not args.skip_venv:
        bootstrap_python_environment(
            explicit_python=args.python,
            strict_dependency_install=args.strict_python_deps,
        )

    hooks_config_path = ROOT / ".codex" / "hooks.json"
    hooks_config_path.write_text(files[hooks_config_path], encoding="utf-8")

    written = []
    skipped = []

    for path, content in files.items():
        if path.exists() and not args.force:
            skipped.append(path)
            continue
        path.write_text(content, encoding="utf-8")
        written.append(path)

    if written:
        print("Bootstrapped harness starter files:")
        for path in written:
            print(f"- {path.relative_to(ROOT)}")
    if skipped:
        print("Skipped existing files:")
        for path in skipped:
            print(f"- {path.relative_to(ROOT)}")

    return 0


def ensure_directories() -> None:
    directories = [
        ROOT / ".codex",
        ROOT / ".githooks",
        ROOT / ".codex" / "runtime",
        ROOT / ".codex" / "runtime" / "sessions",
        ROOT / ".codex" / "runtime" / "observations",
        ROOT / "docs" / "ai",
        ROOT / "docs" / "ai" / "handoffs" / "active",
        ROOT / "docs" / "ai" / "handoffs" / "archive",
        ROOT / "docs" / "ai" / "status",
        ROOT / "docs" / "ai" / "changelog",
        ROOT / "docs" / "ai" / "adr",
        ROOT / "docs" / "ai" / "archive",
        ROOT / "docs" / "requirements",
        ROOT / "docs" / "requirements" / "source",
        ROOT / "docs" / "requirements" / "normalized",
        ROOT / "docs" / "requirements" / "workstreams",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def render_harness_config() -> str:
    return textwrap.dedent(
        """\
        [checks]
        required_ai_docs = [
          "AGENTS.md",
          "docs/ai/plan.md",
          "docs/ai/working-context.md",
        ]
        required_requirements_docs = [
          "docs/requirements/traceability-matrix.md",
        ]
        """
    )


def render_requirements_txt() -> str:
    return textwrap.dedent(
        """\
        # Optional compatibility dependency for Python < 3.11.
        # Bootstrap treats dependency installation as best-effort by default
        # so offline repos can still finish initialization.
        tomli>=2,<3; python_version < "3.11"
        """
    )


def render_hooks_config() -> str:
    return render_platform_hooks_config(root=ROOT)


def bootstrap_python_environment(
    *,
    explicit_python: str | None,
    strict_dependency_install: bool,
) -> None:
    python_cmd = resolve_bootstrap_python(explicit_python)
    refresh_existing_venv = resolve_runnable_repo_python_command() is None

    if not DEFAULT_VENV_DIR.exists() or refresh_existing_venv:
        create_args = [*python_cmd, "-m", "venv"]
        if DEFAULT_VENV_DIR.exists():
            create_args.append("--clear")
        subprocess.run(
            [*create_args, str(DEFAULT_VENV_DIR)],
            cwd=str(ROOT),
            check=True,
        )

    repo_python_cmd = resolve_runnable_repo_python_command()
    venv_python = resolve_existing_python(DEFAULT_VENV_DIR) or expected_repo_venv_python()
    if not venv_python.exists() or repo_python_cmd is None:
        raise SystemExit(f"ERROR: expected venv python at {venv_python}")

    if DEFAULT_REQUIREMENTS_PATH.exists():
        install_optional_requirements(
            venv_python=venv_python,
            strict_dependency_install=strict_dependency_install,
        )

    print(f"Python environment ready: {venv_python}")


def install_optional_requirements(
    *,
    venv_python: Path,
    strict_dependency_install: bool,
) -> None:
    try:
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(DEFAULT_REQUIREMENTS_PATH)],
            cwd=str(ROOT),
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        message = (
            "WARN: Python dependency install failed; continuing because bootstrap only "
            "requires a repo-local venv to finish initialization. "
            f"Re-run `{venv_python} -m pip install -r {DEFAULT_REQUIREMENTS_PATH}` later if needed."
        )
        if strict_dependency_install:
            raise SystemExit(
                f"ERROR: {message[6:]}"
            ) from exc
        print(message)


def resolve_bootstrap_python(explicit_python: str | None) -> list[str]:
    if explicit_python:
        command = [explicit_python]
        if is_runnable_python(command):
            return command
        raise SystemExit(f"ERROR: explicit Python is not runnable: {explicit_python}")

    prefix_commands: list[list[str]] = []
    if os.environ.get("VIRTUAL_ENV"):
        env_python = resolve_existing_python(Path(os.environ["VIRTUAL_ENV"]))
        if env_python is not None:
            prefix_commands.append([str(env_python)])

    if os.environ.get("CONDA_PREFIX"):
        env_python = resolve_existing_python(Path(os.environ["CONDA_PREFIX"]))
        if env_python is not None:
            prefix_commands.append([str(env_python)])

    for command in prefix_commands:
        if is_runnable_python(command):
            return command

    env_python = os.environ.get("CODEX_HARNESS_PYTHON", "").strip()
    if env_python:
        command = [env_python]
        if is_runnable_python(command):
            return command

    path_commands: list[list[str]] = []
    for name in ("python3", "python"):
        for python_path in all_commands_on_path(name):
            command = [python_path]
            if command not in path_commands:
                path_commands.append(command)

    path_command = best_python_command(path_commands)
    if path_command is not None:
        return path_command

    if is_windows_host():
        py_launcher = shutil.which("py")
        if py_launcher:
            command = [py_launcher, "-3"]
            if is_runnable_python(command):
                return command

    for candidate in common_windows_python_candidates():
        command = [str(candidate)]
        if is_runnable_python(command):
            return command

    if sys.executable:
        command = [sys.executable]
        if is_runnable_python(command):
            return command

    raise SystemExit("ERROR: could not determine a Python executable for bootstrap")


def resolve_runnable_repo_python_command() -> list[str] | None:
    repo_python = resolve_existing_python(DEFAULT_VENV_DIR)
    if repo_python is None:
        return None
    command = [str(repo_python)]
    if is_runnable_python(command):
        return command
    return None


def render_ai_index(project_name: str, stage_label: str) -> str:
    return textwrap.dedent(
        f"""\
        # AI 文档入口索引

        更新时间：YYYY-MM-DD
        当前状态：待导入首个真实场景
        当前阶段：{stage_label}

        ## 入口说明

        本文件是 `docs/ai/` 的稳定路由层，面向 AI 与人类执行者。

        这里只保留共享治理控制面的默认入口，不在这里重复展开完整阶段目录。

        `.codex/runtime/` 下的 session 与 observation 文件属于本地 runtime harness，不纳入默认共享阅读面，也不作为项目共享真相。

        ## 默认阅读顺序

        1. [项目规则 AGENTS.md](../../AGENTS.md)
        2. [当前工作上下文](./working-context.md)
        3. [需求文档入口索引](../requirements/index.md)
        4. [项目计划](./plan.md)
        5. [Harness 可迁移清单](./harness-portability-guide.md)
        6. [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)
        7. [传统项目接入 Harness 的标准起手式](./traditional-project-harness-kickoff.md)

        ## 默认治理控制面

        - [项目规则 AGENTS.md](../../AGENTS.md)
        - [当前工作上下文](./working-context.md)
        - [需求文档入口索引](../requirements/index.md)
        - [项目计划](./plan.md)
        - [Harness 可迁移清单](./harness-portability-guide.md)
        - [handoffs/active](./handoffs/active)
        - [status](./status)
        - [changelog](./changelog)
        - [adr](./adr)
        - 默认 active handoff 预算：`<=5`。超过预算时优先压缩到 `status` 或归档，而不是继续扩张默认恢复面。

        ## 当前阶段占位

        - 暂无阶段 `status`
        - 暂无活跃 `handoff`
        - 暂无阶段 `changelog`
        - 暂无正式 `adr`

        ## 活跃目录

        - [handoffs/active](./handoffs/active)
        - [status](./status)
        - [changelog](./changelog)
        - [adr](./adr)

        ## 归档入口

        - [handoffs/archive](./handoffs/archive)
        - [archive](./archive)

        ## 维护规则

        - 本文件只做稳定路由，不维护第二套“当前阶段总表”或“下一次会话先读”的完整展开版。
        - 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，更新这里的稳定入口与占位状态。
        - 当某个完成型 `handoff` 已被 `status` 或 `adr` 吸收且不再有默认恢复价值时，将其移入 `handoffs/archive`。
        - 本地 runtime harness 文件不应加入本索引。
        """
    )


def render_plan(project_name: str, stage_label: str) -> str:
    return textwrap.dedent(
        f"""\
        # 项目计划

        更新时间：YYYY-MM-DD
        文档定位：阶段规划与范围控制视图

        ## 使用边界

        - 本文件只承载阶段目标、范围、模块划分和阶段验收口径。
        - 当前完成度、最新验证结论和执行证据以 `working-context`、`status`、`handoff` 与 `docs/requirements/traceability-matrix.md` 为准。
        - 若阶段目标或范围变化，更新本文件；若只是完成度或验证结果变化，优先更新主真相文档。

        ## 项目目标

        - 为 `{project_name}` 建立最小可用的 Codex-first harness 控制面
        - 导入首个真实需求场景并形成第一个垂直切片
        - 跑通 `requirements -> implementation -> runtime memory -> handoff/status` 的最小闭环

        ## 范围定义

        ### 当前范围

        - 初始化 `docs/ai/` 与 `docs/requirements/` 控制面
        - 导入首个真实 `REQDOC / REQ / WS`
        - 落地第一个可验证的垂直场景

        ### 暂不纳入范围

        - 多 workstream 并行治理
        - CI 强校验接入
        - 完整发布或部署体系

        ## 业务线索与模块划分

        ### 核心业务线索

        - 首个真实需求导入与 traceability
        - 第一个垂直切片实现与验证
        - runtime observation / reducer / handoff / status 压缩验证

        ### 模块划分

        - `docs/requirements/`：原始需求、标准化需求、工作流和追踪矩阵
        - `docs/ai/`：执行计划、handoff、status、ADR 和 working context
        - `apps/`：垂直切片实现
        - `.codex/runtime/`：session、observation 和 reducer 原料

        ## 阶段规划

        ### 第 0 阶段：初始化与首个垂直切片

        - 目标：建立控制面、导入首个真实场景并完成最小闭环
        - 验收：至少一个真实 workstream 能稳定走通 requirements -> implementation -> handoff/status

        ### 第 1 阶段：治理收紧

        - 目标：补更强的一致性校验与阶段压缩规则
        - 验收：metadata、traceability 与主真相面的同步规则稳定

        ### 第 2 阶段：多场景复用

        - 目标：把已验证的 harness 复用到更多真实切片
        - 验收：不止一个 workstream 能稳定复用同一套治理链路

        ## 技术与架构决策

        - runtime / governance / verification 三层 harness 已采纳
        - requirements traceability 采用 `REQDOC -> REQ -> WS -> STAGE` 结构
        - 首个垂直场景优先验证 harness 与可用性，而不是先追求完整工程化

        ## 风险与约束

        - 若首个场景过轻，可能不足以验证真实 traceability 链路
        - 若共享文档与实现不同步，容易出现 canonical mapping 漂移
        - 初始阶段的自动化能力应保持轻量，不依赖过强的 hook 语义判断

        ## 文档治理约定

        - 子任务完成后生成 `handoff`
        - 阶段结束后生成 `status`
        - 准备联调、合并或发版前生成 `changelog`
        - 长期有效决策写入 `adr`
        - 阶段文档更新后检查 [AI 文档入口索引](./index.md)
        """
    )


def render_working_context(project_name: str, stage_label: str) -> str:
    return textwrap.dedent(
        f"""\
        # 当前工作上下文

        更新时间：YYYY-MM-DD
        当前阶段：{stage_label}
        当前模式：Codex-first harness engineering

        ## 作用

        本文件只保留当前开发阶段最需要被下一次会话立即继承的增量真相。

        它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

        ## 同步元数据

        - Current Stage: {stage_label}
        - Active Status Source: 未绑定
        - Active Handoff Sources: 未绑定
        - Requirement IDs: 未绑定
        - Workstream IDs: 未绑定
        - Last Synced From: bootstrap
        - Last Synced At: YYYY-MM-DD

        ## 当前主目标

        - 为 `{project_name}` 建立最小可用的共享治理控制面
        - 导入首个真实需求并形成第一个 workstream
        - 让第一条垂直切片跑通 `requirements -> implementation -> runtime memory -> handoff/status`

        ## 当前活跃队列

        1. 初始化 `docs/ai/` 和 `docs/requirements/` 控制面
        2. 导入首个 `REQDOC / REQ / WS`
        3. 实现第一个可验证的垂直切片
        4. 跑通 runtime observation / session / reducer / handoff-status 链路
        5. 默认将共享恢复面保持在 `index -> working-context -> status -> <=5 active handoff`

        ## 当前风险与阻塞

        - 首个真实场景尚未导入，当前还不能证明 traceability 链路可用
        - 若把旧项目共享真相直接复制过来，会污染新项目控制面
        - 若未先初始化 index / plan / working-context / traceability-matrix，Stop hook 可能在首轮工作后直接给出治理失败
        - active handoff 默认预算应保持在 `<=5`；被 `status` 吸收后的完成型 handoff 应进入 `archive`，否则默认恢复面会再次膨胀

        ## 下一次会话先读

        1. [AI 文档入口索引](./index.md)
        2. [当前工作上下文](./working-context.md)
        3. [需求文档入口索引](../requirements/index.md)
        4. [项目计划](./plan.md)
        5. [Harness 可迁移清单](./harness-portability-guide.md)
        6. [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)

        ## 最近已固化的决策

        - 项目采用 `AGENTS.md + Codex Stop hook + 校验脚本` 的治理方式
        - 项目采用 `docs/requirements/` 与 `docs/ai/` 分层管理需求与执行上下文
        - `.codex/runtime/` 只保存本地 session/observation 原料，不替代 `docs/ai/` 共享治理文档
        - 默认共享恢复面保持轻量：`index -> working-context -> status -> <=5 active handoff`
        - `plan` 与 `workstream` 属于 projection surface，不应重复承载快速变化的当前状态
        - `.codex/skills/repo-governed-coding/` 是可选行为护栏，默认显式调用，不替代 `AGENTS.md`、共享治理文档或检查脚本

        ## 更新规则

        - 只保留当前阶段仍然有效的增量真相
        - 当阶段切换、主目标变化或 `status/handoff` 完成压缩后优先更新本文件
        - 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在默认恢复面里
        """
    )


def render_requirements_index() -> str:
    return textwrap.dedent(
        """\
        # 需求文档入口索引

        更新时间：YYYY-MM-DD
        当前状态：待导入首个真实验证场景

        ## 目的

        本目录用于管理项目的需求来源、需求标准化结果、工作流拆解和需求追踪关系。

        它回答四个问题：

        - 原始需求文档有哪些
        - 每份需求文档标准化后是什么
        - 这些需求被拆成了哪些可执行工作流
        - 当前开发阶段正在响应哪些需求

        ## 建议阅读顺序

        1. [需求追踪矩阵](./traceability-matrix.md)
        2. [标准化需求目录](./normalized)
        3. [工作流目录](./workstreams)
        4. [原始需求目录](./source)

        ## 目录结构

        - [source](./source)
        - [normalized](./normalized)
        - [workstreams](./workstreams)
        - [traceability-matrix.md](./traceability-matrix.md)

        ## 使用规则

        - `source/` 只保存原始需求文档或原始需求转录稿
        - `normalized/` 将原始需求统一整理成一致结构
        - `workstreams/` 将多个需求映射成可开发的业务工作流
        - `traceability-matrix.md` 负责串联 `需求 -> 工作流 -> 阶段 -> 实现/测试`
        - 当 `docs/ai/` 下的 `handoff`、`status` 或 reducer 草稿已经绑定需求时，应显式写出 `Requirement IDs` / `Workstream IDs`，并与本目录中的追踪关系保持一致

        ## 当前活跃内容

        - 暂无 source 文档
        - 暂无 normalized 文档
        - 暂无 workstream 文档
        - 追踪关系将在 [traceability-matrix.md](./traceability-matrix.md) 中初始化
        """
    )


def render_traceability_matrix() -> str:
    return textwrap.dedent(
        """\
        # 需求追踪矩阵

        更新时间：YYYY-MM-DD
        当前状态：待建立首个真实场景追踪

        ## 目的

        本文件用于把原始需求文档、标准化需求、工作流、开发阶段和验证信息串联起来。

        ## 使用说明

        - 每个原始需求文档应先有 `REQDOC-XX`
        - 标准化后拆成 `REQ-XXX`
        - 开发侧按 `WS-XX` 工作流组织
        - 阶段执行按 `STAGE-XX` 推进
        - `docs/ai/` 下的 `handoff`、`status`、runtime reducer 草稿若引用了 `REQ-XXX` / `WS-XX`，应与本矩阵保持一致

        ## 矩阵

        | 原始文档 | 标准化需求 | 工作流 | 开发阶段 | 当前状态 | 验收/测试 |
        | --- | --- | --- | --- | --- | --- |
        | 待补充 | 待补充 | 待补充 | 待补充 | 待开始 | 待补充 |
        """
    )


if __name__ == "__main__":
    raise SystemExit(main())
