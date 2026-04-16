# Codex环境上下文处理

**User:**   
**Created:** 4/16/2026 10:00:36  
**Updated:** 4/16/2026 11:03:06  
**Exported:** 4/16/2026 11:06:33  
**Link:** [https://chatgpt.com/c/69e042a1-6898-839c-b838-9438fa69e7b2](https://chatgpt.com/c/69e042a1-6898-839c-b838-9438fa69e7b2)  

## Prompt:
2026/4/16 10:00:35

https://github.com/affaan-m/everything-claude-code   根据这个项目来看的话，假设我现在在codex环境下和ai对话，上下文已经超长了，现在最好的处理办法是开一个新的session还是怎么办呢  ？

## Response:
2026/4/16 10:00:36

我先看一下这个仓库里对“长上下文、续接、开新会话”的思路，再结合 Codex 这类 agent 编码环境给你一个实操判断。你如果更关心的是“OpenAI Codex CLI/代理式编码”而不是泛指所有 coding agent，我会按这个方向来落。

我已经把两个方向对上了：这个仓库本质上强调“把稳定上下文放到外部记忆/工作文件里”，而 Codex 官方这边则明确支持 resume、plan、AGENTS.md 这类“把线程从纯聊天搬到工程文件”的做法。结论大概率不是“单纯一直硬扛在同一个超长 session 里”。

> **Searching project repo and Codex session guidelines**
>
> [affaan-m/everything-claude-code: The agent harness ...](https://github.com/affaan-m/everything-claude-code)
> [Best practices for cost-efficient, high-quality context ...](https://community.openai.com/t/best-practices-for-cost-efficient-high-quality-context-management-in-long-ai-chats/1373996)
> [Codex CLI features](https://developers.openai.com/codex/cli/features)
> [Changelog - Everything Claude Code](https://mintlify.com/affaan-m/everything-claude-code/reference/changelog)
> [The context window is so small...how do you all manage it?](https://www.reddit.com/r/codex/comments/1okl3j5/the_context_window_is_so_smallhow_do_you_all/)
> [OpenAI Codex Tutorial #5 - CLI Commands & Resuming ...](https://www.youtube.com/watch?v=htNz7uazonY)
> [plugin everything-claude-code](https://www.claudepluginhub.com/plugins/affaan-m-everything-claude-code)
> [Complete Beginner's Guide to OpenAI's Codex App](https://getpushtoprod.substack.com/p/complete-beginners-guide-to-openais)
> [How to Resume Sessions in Codex CLI](https://inventivehq.com/knowledge-base/openai/how-to-resume-sessions)
> [Everything Claude Code: The Repo That Won Anthropic ...](https://medium.com/%40joe.njenga/everything-claude-code-the-repo-that-won-anthropic-hackathon-33b040ba62f3)
> [Context Management Strategies for OpenAI Codex](https://iceberglakehouse.com/posts/2026-03-context-openai-codex/)
>
> **Looking into repo documentation**
>
> I need to check the repository docs, maybe start with the README and any relevant context documents. Should I look at raw content on GitHub or open it through a web interface? A snippet might be enough, but I want to make sure I have a citation if I refer to it. Let’s open it.
>
> **Inspecting GitHub README and related documentation**
>
> [GitHub - affaan-m/everything-claude-code: The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond. · GitHub](https://github.com/affaan-m/everything-claude-code)
> [Features – Codex CLI | OpenAI Developers](https://developers.openai.com/codex/cli/features)
> [Mintlify - The Intelligent Knowledge Platform](https://mintlify.com/openai/codex/cli/resume)
>
> **Searching Codex documentation for compaction and context**
>
> [Compaction | OpenAI API](https://developers.openai.com/api/docs/guides/compaction)
>
> **Formulating answer and structuring approach**
>
> I need to write an answer with a recommendation on how to handle sessions, focusing on compacting, refreshing, and using external memory. Codex can resume automatically, and I should mention when to start a new session vs. resuming. I'll cite all factual statements and inspect AGENTS guidelines for better understanding. Time to search!
>
> **Searching AGENTS guidelines for task recommendations**
>
> [Custom instructions with AGENTS.md – Codex | OpenAI Developers](https://developers.openai.com/codex/guides/agents-md)
>
> **Looking for memory optimization references**
>
> I need to search the repository for any references to working context or memory optimization. I’ll look through open lines in the code and try to identify any patterns that could help me understand how memory is being handled. Time to dig in and see what I can find!
>
> **Searching repo for working context and optimization patterns**
>
> [GitHub - affaan-m/everything-claude-code: The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond. · GitHub](https://github.com/affaan-m/everything-claude-code)
>
> **Explaining model compaction and session handling**
>
> I’ll highlight that while the "everything-claude-code" is based mainly on Claude, the same patterns for session handling apply. I should mention the benefits of starting a new session when switching tasks or after repeated compaction. I’ll also refer to official documentation on compaction and resumption if needed.
>
> **Recommendation for managing session workflows**
>
> To manage sessions efficiently: 
> 
> 1. Externalize important context (e.g., AGENTS.md, WORKING_CONTEXT.md, PLANS.md) before context gets too large.
> 2. For the same task, use compaction/resume unless the task has drifted.
> 3. Start a new session when topics diverge or too much compaction occurs. Always use structured handoffs for better clarity.
>
> Thought for 1m 5s

结合这个项目的思路来看，你在 **Codex 环境里上下文已经超长** 时，**最优解通常不是死扛当前 session，也不是无脑全靠开新 session**。更实用的判断是：

**先把“长期记忆”搬出对话，再决定是 resume 还是新开。**

原因很直接：

这个仓库本身就不是在鼓励你把一切都塞进聊天历史里，而是在做“外部化上下文”：它强调 skills、memory persistence、strategic compaction，甚至把 `session-start` / `session-end` / `pre-compact` / `suggest-compact` 这类 hook 都做出来了，本质就是把关键状态从会话里抽出来。[GitHub+2GitHub+2](https://github.com/affaan-m/everything-claude-code)

而 Codex 官方这边也不是“只能靠长聊天硬记”。Codex 会监控上下文剩余空间；长任务里会自动 compact，把相关内容总结后保留、丢弃次要细节。Codex 还支持 `codex resume` 延续旧会话，并且会保留原来的 transcript、plan history 和 approvals。[OpenAI开发者+1](https://developers.openai.com/codex/prompting)

所以我给你的结论是：

一句话判断
-----

**如果还是同一个任务链，而且你还依赖前面对话里的细节脉络，就先整理 handoff，再决定 resume。**  
**如果当前线程已经混了太多分支、来回改方向、压缩过很多轮，最好的做法通常是：开一个新 session，但不是裸开，而是带着 handoff 文件开。**

我更推荐的优先级
--------

### 1）最好先做“上下文外置”

把这些东西写进仓库文件，而不是继续堆聊天：

*   `AGENTS.md`：稳定规则、编码偏好、验证要求
*   `WORKING_CONTEXT.md` 或 `SESSION-HANDOFF.md`：当前目标、已完成内容、卡点、下一步
*   `PLANS.md` / ExecPlan：长任务拆解、里程碑、验收标准

这是因为 Codex 会在启动时自动读取 `AGENTS.md`；而官方对长任务也明确推荐 plan mode 和 `PLANS.md` 这类执行计划文件。更关键的是，ExecPlan 的设计目标就是：**只靠当前代码树 + 这份计划文档，也能重新开工，不依赖旧对话记忆。** [OpenAI开发者+3OpenAI开发者+3OpenAI开发者+3](https://developers.openai.com/codex/guides/agents-md)

### 2）什么时候继续当前 session / resume 旧 session

适合这几种情况：

*   你还在做同一件事
*   前面的审批、计划、工具轨迹很重要
*   线程虽然长，但没有明显跑偏
*   你希望 Codex 接着原有思路干

这时用 `codex resume` 是合理的，因为它会保留完整的原始会话历史、计划历史和 approvals。[OpenAI开发者](https://developers.openai.com/codex/cli/features)

### 3）什么时候新开 session 更好

我会建议直接新开，尤其是下面这些情况：

*   一个线程里混进了多个目标：修 bug、重构、查资料、讨论架构全掺在一起
*   你已经感觉模型开始“记混了”或者反复绕圈
*   线程已经 compact 过多次，担心早期细节被压缩掉
*   你准备切到新的子任务、子模块、分支

这里虽然官方文档没有直接说“compact 多次一定变差”，但它明确写了 compact 会“总结相关信息、丢弃不太相关的信息”。所以当你依赖很多细枝末节时，反复 compaction 后的信息损失风险是客观存在的，这是一个合理推断。[OpenAI开发者+1](https://developers.openai.com/codex/prompting)

实操上，我建议你这样做
-----------

### 方案 A：同一任务，线程还没烂透

1.  先让 AI 产出一个 handoff 文档
2.  存成 `WORKING_CONTEXT.md`
3.  再 `codex resume` 继续，或者开新 session 读取这个文件

### 方案 B：线程已经很脏

直接新开 session，然后第一句不是重新口述一大堆，而是：

```
先阅读 AGENTS.md 和 WORKING_CONTEXT.md。
你现在的任务是继续完成“X”。
先复述当前状态、未完成项、风险点，再开始执行。
每完成一个里程碑就更新 WORKING_CONTEXT.md。
```

这个方式通常比“把旧对话复制一大坨进来”稳定得多。

你这个场景下，我的直接建议
-------------

如果你说的是：

*   在 Codex 里已经聊了很久
*   上下文超长
*   你开始担心它忘事、串线、降质

那我建议你 **不要继续硬顶当前 session**。  
**最优先动作是：让它先生成一个 handoff/working-context 文件，然后新开一个干净 session，从文件恢复。**

也就是：

**不是单纯“开新 session”**，而是  
**“先固化状态，再开新 session”**。

这其实和 `everything-claude-code` 的核心哲学是一致的：  
把长期有效的信息放进外部记忆、规则、计划、hooks，而不是完全依赖一次会话的上下文长度。[OpenAI开发者+4GitHub+4GitHub+4](https://github.com/affaan-m/everything-claude-code)

给你一个最小 handoff 模板
-----------------

你可以让 Codex 先生成这个：

```
# WORKING_CONTEXT.md

## 当前目标
一句话说明现在要完成什么

## 已完成
- 已做完的关键改动 1
- 已做完的关键改动 2

## 当前代码影响面
- 涉及文件:
  - path/a.ts
  - path/b.ts

## 关键约束
- 不能改公共接口
- 必须通过 test/lint/typecheck
- 保持向后兼容

## 当前问题 / 风险
- 某模块耦合高
- 某测试不稳定
- 某设计点还未确认

## 下一步
1. 先补测试
2. 再修实现
3. 最后跑验证

## 验证命令
- npm test
- npm run lint
- npm run typecheck

## 决策记录
- 为什么没选方案 A
- 为什么当前用方案 B
```

最后的判断口诀
-------

你可以直接这么记：

*   **还能聚焦**：resume
*   **已经混乱**：new session
*   **无论哪种**：先写 handoff
*   **长期项目**：AGENTS.md + PLANS.md + WORKING\_CONTEXT.md

如果你愿意，我可以直接按 **Codex 场景** 给你整理一套：  
**“长上下文爆掉时的标准切会话工作流”**，包括 prompt 模板、`AGENTS.md` 模板、`WORKING_CONTEXT.md` 模板。

---

**Sources:**

- [GitHub - affaan-m/everything-claude-code: The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond. · GitHub](https://github.com/affaan-m/everything-claude-code)
- [Prompting – Codex | OpenAI Developers](https://developers.openai.com/codex/prompting)

## Prompt:
2026/4/16 10:14:15

我有一个问题 ，对于working-context来说，这个文件不是只存储最近的几次回话吗？ 假设我这次的ssesion会话已经很长了，这个working-context会存储哪些内容？ 会不会漏掉之间的一些关键知识内容 ？ 对于非工作时上下文，假设我现在又开了一个新的session ，那之前的working-context是不是就被重写了 ？ 最老的一个working-context是不是就需要沉淀到一个历史文件中，供ai进行读取，作为一个长时间的记忆 ？ 你帮我捋一下

## Response:
2026/4/16 10:14:16

你这个问题问到点上了：真正难的不是“有没有 working-context”，而是“它到底该承载短期状态，还是长期记忆”。我去把这个仓库里关于 working-context、session persistence、compaction 这一套再对一下，然后给你捋成一个能落地的分层模型。

> **Searching GitHub repo for working-context and session-end**
>
> [affaan-m/everything-claude-code: The agent harness ...](https://github.com/affaan-m/everything-claude-code)
>
> **Searching for longform guide and relevant lines**
>
> [everything-claude-code/the-longform-guide.md at main · affaan-m/everything-claude-code · GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md)
>
> **Exploring memory persistence in longform guide**
>
> I’m thinking I might need to add more detailed sections about memory persistence in the guide. I’ll search for the right places to do that, perhaps in sections where it’s most relevant, and make sure it fits into the larger context smoothly.
>
> **Searching for longform resources on memory persistence**
>
> [everything-claude-code/the-longform-guide.md at main · affaan-m/everything-claude-code · GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md)
>
> **Clarifying the handling of WORKING-CONTEXT and session summaries**
>
> To answer the user's concern, I’ll explain that the WORKING-CONTEXT should not include only recent chats. According to the repository, it reflects the current sprint, blockers, and next actions, with old stuff archived. Each session gets a new file to avoid mixing old context with new work. There are two key patterns: active sprint state, session-specific summaries, and long-term learning in separate docs. Stable rules should be in the AGENTS.md/skills file.
>
> Thought for 42s

你这个理解已经很接近正确做法了。**`working-context` 不应该承担“全部历史记忆”的职责**；它更像“当前作战面板”，负责让 AI 在**这一阶段**继续干活，而不是当完整档案库。这个仓库自己的 `WORKING-CONTEXT.md` 也写得很明确：它应该只对**当前 sprint、blockers、next actions** 保持详细；已经不再影响当前执行的完成内容，要总结到 archive 或 repo docs 里。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/WORKING-CONTEXT.md)

你担心的几个点，我给你拆开说。

1）`working-context` 到底存什么
-------------------------

不是“最近几次对话全文”，而是“当前还会影响执行的最小必要真相”。  
这个仓库在长文档里建议，跨 session 共享记忆时，要保存的是这些东西：

*   哪些方法**已验证有效**
*   哪些方法**试过但无效**
*   哪些方法**还没试**
*   还剩什么要做

它甚至建议：当你快撞到 context limit 时，让 AI 先生成一份当前状态总结文件，审一下，然后下一次直接把这个文件路径给它继续做。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md)

所以，`working-context` 最该放的是：

*   当前目标
*   当前约束
*   已完成到哪一步
*   已证伪/已证实的路线
*   当前卡点
*   下一步动作

而不是把整段长会话原样塞进去。

2）它会不会漏掉中间关键知识
--------------

**会。** 如果你把 `working-context` 当“压缩版聊天记录”，它一定会漏。  
但真正的问题不是“会不会漏”，而是：**哪些东西本来就不该放在 `working-context` 里。**

你可以把信息分成三类：

### A. 只影响当前推进的内容

比如：

*   这个 bug 的根因现在怀疑在连接池
*   A 方案跑过，失败
*   B 方案还没试
*   当前改过哪些文件
*   下一步先补测试再改实现

这些该进 `working-context`。因为它们是“现在就要继续干活”的上下文。[GitHub+1](https://github.com/affaan-m/everything-claude-code/blob/main/WORKING-CONTEXT.md)

### B. 具有复用价值的稳定知识

比如：

*   这个仓库的构建坑
*   某依赖的兼容性约束
*   某模块的长期设计原则
*   你团队固定的测试/提交/验证规范

这些**不该长期堆在 `working-context`**。  
这个仓库的 longform guide 明确建议：反复出现、值得复用的模式，要沉淀成 **skills / rules / 持久规则**，这样下次类似问题会自动被加载，而不是每次靠你重新解释。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md)

### C. 历史过程材料

比如：

*   早期探索过程
*   多轮试错记录
*   旧分支思路
*   旧方案为什么被废弃

这些不适合一直挂在当前 `working-context` 里，但也不能直接丢。  
它们更适合进 **archive / session history / ADR / docs**。仓库本身就说，完成但已不再影响当前执行的内容，要挪到 archive 或 repo docs。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/WORKING-CONTEXT.md)

所以答案是：

**`working-context` 会漏掉历史细节，这不是 bug，而是设计目标。**  
关键是你要把“会被漏掉但以后还重要”的那部分，沉淀到别的层。

3）开了新 session 以后，之前的 `working-context` 会不会被重写
---------------------------------------------

如果你只有**一个** `WORKING-CONTEXT.md`，那答案通常是：**会，它本来就应该被滚动更新。**  
因为它代表的是“当前工作面”，不是“永恒历史库”。这和仓库里的 update rule 是一致的。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/WORKING-CONTEXT.md)

但这个仓库同时又给了另一条关键建议：  
**为每个 session 创建单独的总结文件**，这样第二天可以继续接上；而且要“每个 session 一个新文件”，避免把旧上下文污染到新工作里。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md)

所以更合理的做法不是二选一，而是：

*   `WORKING-CONTEXT.md`：一个，滚动覆盖，表示当前态
*   `sessions/*.md`：多个，每次 session 一个，作为历史切片
*   `docs/adr/*.md` / `skills/` / `AGENTS.md`：沉淀长期知识

4）最老的 `working-context` 要不要沉淀到历史文件里，作为长期记忆
------------------------------------------

**要，但不是“全量长期加载”。**  
应该是“分层沉淀 + 按需读取”。

这个仓库 longform guide 提到两件很关键的事：

第一，它建议使用 session summary 文件跨 session 续接。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md)  
第二，它又建议不要把所有东西都塞到每次都自动加载的全局规则里，而是按场景做更“外科手术式”的动态上下文注入。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md)

这两个点合起来，就是最合理的长期记忆模型：

### 第 1 层：短期工作记忆

`WORKING-CONTEXT.md`

特点：

*   当前任务态
*   高度可变
*   可以覆盖
*   只保留还会影响下一步执行的内容

### 第 2 层：中期会话记忆

`sessions/2026-04-16-auth-refactor.md` 这类文件

特点：

*   一次 session 一个文件
*   记录这次做了什么、试了什么、为什么停下
*   供未来“恢复现场”时按需读取
*   不应默认每次全加载

### 第 3 层：长期稳定记忆

`AGENTS.md`、架构文档、ADR、项目 FAQ、技能文件

特点：

*   不是“这次聊了啥”
*   而是“以后类似问题都成立的规则/知识”
*   应该尽量精炼、稳定、可复用
*   可以默认加载或半默认加载

这个分层，才是你说的“供 AI 进行读取，作为长时间记忆”的正确打开方式。

5）所以非工作时上下文怎么办
--------------

你说的“非工作时上下文”，我理解成两种：

### 一种是同项目但不在当前主线上的探索

比如：

*   你中间顺手研究了一个备选框架
*   查了个性能优化路线
*   做了个未采用的 POC

这类内容不该继续霸占 `WORKING-CONTEXT.md`，但也不该丢。  
放去 `sessions/` 或 `research/`，未来需要时再读。[GitHub+1](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md)

### 另一种是跨项目、跨时间都适用的认知

比如：

*   你习惯先补测试后改代码
*   某类仓库要先跑哪几个验证命令
*   某套架构决策原则

这类内容应该进 `AGENTS.md` 或规则文件，因为 Codex 会在启动时读取 `AGENTS.md`，它天然更适合放“每次开工都该知道的稳定原则”。

6）你可以直接这么理解
-----------

我帮你捋成一句最顺的：

**`working-context` 不是记忆库，它是“当前态”；  
session history 不是当前态，它是“恢复现场”；  
AGENTS/skills/docs 才是“长期知识”。**

7）我给你的推荐落地方案
------------

你可以直接按这个目录来：

```
project/
  AGENTS.md
  WORKING-CONTEXT.md
  docs/
    architecture.md
    decisions/
      ADR-001-auth-design.md
      ADR-002-cache-strategy.md
  .ai-memory/
    sessions/
      2026-04-16-session-01.md
      2026-04-17-session-02.md
    research/
      oauth-options.md
      redis-failure-notes.md
```

然后规则是：

*   `WORKING-CONTEXT.md`：只保留当前任务态
*   每次 session 结束：产出一个 `sessions/*.md`
*   反复出现的经验：提炼进 `AGENTS.md` 或 docs
*   已完成但还有参考价值的过程：进 `research/` 或 ADR
*   新 session 启动时：默认先读 `AGENTS.md` + `WORKING-CONTEXT.md`
*   只有需要恢复旧细节时，才额外读某个 `sessions/*.md`

这样既不会把历史全丢，也不会让 AI 每次都背着全部旧包袱启动。

8）最后给你一个判断标准
------------

某条信息该放哪，看这三个问题：

1.  **它是否直接影响下一步执行？**  
    影响，就放 `working-context`。
2.  **它是否未来会反复复用？**  
    会，就提炼进 `AGENTS.md` / docs / skills。
3.  **它只是这次过程重要，但不该默认加载？**  
    那就进 `session history` / archive。

你现在的思路“最老的一个 `working-context` 需要沉淀到历史文件中，供 AI 读取，作为长时间记忆”——**方向是对的**。  
我只会补一句：

**不是把旧 `working-context` 原封不动堆成永久记忆，而是要把它拆成：当前态、历史切片、长期知识，这三层。**

如果你愿意，我下一条可以直接给你一套可用的：  
**`WORKING-CONTEXT.md` + `SESSION-SUMMARY.md` + `AGENTS.md` 三件套模板**。

---

**Sources:**

- [everything-claude-code/WORKING-CONTEXT.md at main · affaan-m/everything-claude-code · GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/WORKING-CONTEXT.md)

## Prompt:
2026/4/16 10:50:43

我还有个问题 ，对于working-context这个文件，这个机制，是通过什么方式去在每一次回话后调用的呢？ 假设我开了subagent、或者多session在同时执行，那同时完毕调hook后会发生什么 ？  另外关于永久性记忆是何时调用的呢？ 即当working-context被再次出发后，之前的信息是哪个钩子去往永久性记忆里存储的信息 ？

## Response:
2026/4/16 10:50:46

这个问题已经进入“它到底怎么落地”的层面了。我去把 repo 里和 `session-start / session-end / pre-compact / memory-persistence`、以及并发/race condition 相关的说明对一下，再给你一个尽量贴近真实实现的解释。

我已经对到一个关键点了：在这个 repo 里，**“每次回复后保存 working-context” 的主力并不是 `SessionEnd`，而是 `Stop`**。`SessionEnd` 在当前 hooks 里更像一个额外的 lifecycle marker。并发这块也确实不是完全稳的，repo 里已经有公开的 race condition issue。

> **Browsing repo docs for hooks, memory persistence, and race conditions**
>
> [wesammustafa/Claude-Code-Everything-You-Need-to-Know](https://github.com/wesammustafa/Claude-Code-Everything-You-Need-to-Know)
> [Maestro vs Superpowers vs ECC vs Agent Orchestrator ...](https://gist.github.com/jeffscottward/de77a769d9e25a8ccdc92b65291b1c34)
>
> **Searching for open hooks and relevant scripts**
>
> [everything-claude-code/hooks/hooks.json at main · affaan-m/everything-claude-code · GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)
>
> **Searching for patterns in hooks.json entries**
>
> [everything-claude-code/hooks/hooks.json at main · affaan-m/everything-claude-code · GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)
>
> **Searching for SessionStart/End script details**
>
> [everything-claude-code/hooks/hooks.json at main · affaan-m/everything-claude-code · GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)
>
> **Browsing for script path after SessionStart**
>
> [everything-claude-code/hooks/hooks.json at main · affaan-m/everything-claude-code · GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)
>
> **Searching GitHub for session and memory-related issues**
>
> [everything-claude-code/skills/autonomous-agent-harness ...](https://github.com/affaan-m/everything-claude-code/blob/main/skills/autonomous-agent-harness/SKILL.md)
> [Maestro vs Superpowers vs ECC vs Agent Orchestrator ...](https://gist.github.com/jeffscottward/de77a769d9e25a8ccdc92b65291b1c34)
>
> Thought for 1m 56s

你这个问题已经问到“这套机制真实运行时到底怎么串起来”的核心了。  
我先给结论：

**在这个 repo 当前版本里，`working-context` / session state 的主保存链路，核心不是 `SessionEnd`，而是 `Stop`；`SessionStart` 负责读取；`PreCompact` 负责在压缩前兜底保存；`SessionEnd` 在当前 hooks 里更像一个额外的结束标记。** [GitHub+3GitHub+3GitHub+3](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

1）它是通过什么方式在每次会话后调用的
-------------------

从当前 `hooks/hooks.json` 看，相关链路大致是这样的：

*   `SessionStart` → `session-start-bootstrap.js`，描述就是“在新 session 或 resume 时加载之前的上下文”
*   `PreCompact` → `pre-compact.js`，描述就是“在 context compaction 前保存状态”
*   `Stop` → `session-end.js`，描述写得非常直接：**“在每次响应后持久化 session state（Stop carries transcript\_path）”**
*   `Stop` 还会跑 `evaluate-session.js`，用于“评估 session、抽取可复用模式”
*   `SessionEnd` → `session-end-marker.js`，描述是“session end lifecycle marker (non-blocking)”

所以严格说，**“每一次回复后触发保存”** 在这套配置里主要靠的是 `Stop`，不是你想象中的 `SessionEnd`。`SessionEnd` 更像“真正结束时补一个结束事件”，而不是每轮对话都保存主状态。[GitHub+4GitHub+4GitHub+4](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

再往上一层看，repo 的 longform guide 也和这个一致：它明确写了三类 memory hooks——  
`PreCompact`：压缩前保存重要状态；  
`Stop`：session end 时持久化 learnings；  
`SessionStart`：新 session 自动加载之前上下文。

2）如果开了 subagent，或者多 session 同时执行，hook 完会发生什么
--------------------------------------------

这里要分“理想设计”和“当前实现风险”两层看。

### 先说理想设计

如果每个 session 都写自己的文件，或者写 append-only 日志，那并发问题会小很多。repo 自己在 longform guide 里也建议：**每个 session 创建一个新文件**，这样不会把旧上下文污染到新工作。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md)

### 但当前实现层面，并发确实有风险

repo 已经有公开 issue 直接指出：

*   `saveState()` 在文件系统层面是原子的，做法是临时文件 + `renameSync`，所以**通常不会写出损坏文件**
*   但 **read-modify-write 窗口没有保护**
*   而且 **每次 hook 调用都是一个全新的 Node 进程**
*   进程之间**没有共享内存来协调**

这意味着什么？  
意味着如果**多个 session / 多个并发 hook / 多个几乎同时结束的执行流**去更新同一份项目状态，你大概率不会得到“损坏文件”，但可能会得到：

*   最后写入者覆盖前一个写入者
*   某次更新丢失
*   某份 state 比你预期更旧

也就是典型的 **last-write-wins / lost update** 风险。repo 自己已经把这件事作为 race condition 提出来了。[GitHub](https://github.com/affaan-m/everything-claude-code/issues/1441)

### 关于 subagent

我在当前 ECC 的 `hooks.json` 里，针对这条 memory 链路能明确看到的是 `SessionStart` / `PreCompact` / `Stop` / `SessionEnd`。  
**我没有在这份当前 hooks 文件里看到一条单独的 `SubagentStop` 记忆链路配置。** 这意味着，至少在当前 ECC 公开 hooks 配置层，你不能想当然地认为“每个 subagent 完成后都会自动走一套独立的 working-context 持久化流程”。更现实的判断是：**如果 subagent 也会触发共享状态更新，而更新目标又是同一个项目级 state，就更容易撞上上面那个并发窗口问题。** 这个结论是基于我对当前 hooks 文件的检查和上面的 race condition issue 做的推断。[GitHub+3GitHub+3GitHub+3](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

3）“永久性记忆”是什么时候调用的
-----------------

这里最容易混淆。  
在 ECC 这套东西里，**“永久性记忆”并不是单一文件、单一 hook、单一存储。** 它更像一个流水线：

### 第一层：原始观察被持续采集

`continuous-learning-v2` 的 hooks 会在工具调用前后采集观察：

*   `pre:observe:continuous-learning`
*   `post:observe:continuous-learning`

它们的描述就是“Capture tool use observations / results for continuous learning”。而 troubleshooting 文档也给出了实际观测文件位置：  
`~/.claude/homunculus/projects/*/observations.jsonl`。  
这说明长期记忆的“原料”不是等你 session 结束才突然生成，而是在运行过程中持续采样。[GitHub+1](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

### 第二层：在 Stop 阶段做提炼

`Stop` 里有 `evaluate-session.js`，描述是 “Evaluate session for extractable patterns”。  
`continuous-learning` 这个 skill 的描述也写得很明确：它会在 session 结束时自动评估 session，并把可复用模式保存成 learned skills，供以后使用。[GitHub+1](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

### 第三层：新 session 再读回来

真正“把之前的记忆重新喂回来”的是 `SessionStart`，也就是读，不是写。  
longform guide 明确说：`SessionStart Hook` 用来在新 session 自动加载 previous context。[GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

所以你那句：

> 当 working-context 被再次触发后，之前的信息是哪个钩子去往永久性记忆里存储的？

更准确的回答是：

**不是“working-context 再次触发时才顺手存入永久记忆”。**  
真正写入长期记忆的主链路更像是：

*   运行中：`pre/post observe` 记录原始 observations
*   每轮回复后 / stop 阶段：`stop:evaluate-session` 提炼模式
*   每轮回复后：`stop:session-end` 保存当前 session state / working state
*   下次启动：`SessionStart` 读取这些内容

也就是说，**`SessionStart` 是读取钩子；`Stop` 才是核心写入钩子；`PreCompact` 是压缩前兜底；长期记忆不是一把写进去，而是“观察 → 提炼 → 回灌”的链条。** [GitHub+2GitHub+2](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

4）那 working-context 和永久记忆之间到底是什么关系
----------------------------------

你可以这么理解：

*   `working-context`：当前作战面板，偏短期状态
*   `session state`：当前 session 的可恢复状态
*   `observations.jsonl`：长期学习原料
*   `learned skills / rules / docs`：真正更稳定的长期知识

所以 **working-context 不是永久记忆本体**。  
它更像是“当前态缓存”。  
真正往长期层沉淀的，更多是 `continuous-learning` 这条链路抽出来的模式、规则、经验，而不是把旧 `working-context` 原样无脑堆下去。[GitHub+1](https://github.com/affaan-m/everything-claude-code/blob/main/skills/continuous-learning/SKILL.md?utm_source=chatgpt.com)

5）还有一个现实问题：这套 hooks 现在并不一定百分百能跑
-------------------------------

这里我得给你一个很重要的现实提醒：  
repo 里有一个很新的 issue 指出，在某些 Claude Code 2.1.x 环境下，`hooks.json` 里的 27 个 hooks 会因为 schema 校验问题全部加载失败；也就是说，skills/agents/MCP 可能正常，但 **hook-driven automations 直接失效**。[GitHub](https://github.com/affaan-m/everything-claude-code/issues/1454)

所以如果你问“机制上是怎么设计的”，上面那套链路就是答案。  
但如果你问“今天装上就一定这么运行吗”，答案是：**未必，要看你当前运行环境、Claude Code 版本、hook schema 是否兼容。** [GitHub](https://github.com/affaan-m/everything-claude-code/issues/1454)

6）我给你的落地判断
----------

如果你以后自己实现这套东西，我建议你不要把“永久记忆”押宝在一个 hook 上，而是做成下面这套：

*   `Stop`：写当前 working state
*   `PreCompact`：压缩前快照
*   `SessionStart`：读当前 state
*   `PreToolUse/PostToolUse`：写 append-only observations
*   单独 reducer / evaluator：把 observations 提炼成 durable memory
*   durable memory 不直接覆盖，尽量 append + summarize
*   并发时避免多个 session 写同一文件，优先“每 session 一份文件 + 最后汇总”

这样会比“所有 session 都写一个 `WORKING-CONTEXT.md`”稳得多。

如果你愿意，我下一条可以直接给你画一张：  
**`working-context / session-state / observations / long-term-memory` 的钩子流转图**，再顺便给你一份适合 Codex/Claude Code 改造的目录结构。

---

**Sources:**

- [everything-claude-code/hooks/hooks.json at main · affaan-m/everything-claude-code · GitHub](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)