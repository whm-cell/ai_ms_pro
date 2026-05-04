# Evidence And Boundaries

This skill packages a repo-specific workflow. Public skills can assist adjacent tasks, but the searched ecosystem did not provide a mature, full replacement for this control loop.

## Public Skill Search Result

Searches run with `npx skills find` on 2026-05-04:

- `github workflow`: found mature general workflow skills such as `github/awesome-copilot@create-github-action-workflow-specification` and `github/awesome-copilot@project-workflow-analysis-blueprint-generator`, but these are workflow-authoring aids, not PR touch-conflict governance.
- `pr review`: found code-review skills, but not changed-file overlap, CODEOWNERS, PR template, and merge queue coordination as one mechanism.
- `merge queue`: found queue or merge-adjacent skills, but not GitHub merge queue / `merge_group` required-check governance for PR collision control.
- `pull request conflict` and `merge conflict`: found low-install conflict-resolution skills, mostly for resolving conflicts after they exist.
- `codeowners`: found a low-install CODEOWNERS management skill, not a complete team PR collision control workflow.

Conclusion: use public skills for narrow adjacent tasks if desired, but keep this repo-local skill for the integrated governance behavior.

## External Practice Anchors

- GitHub branch protection and required checks: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub merge queue and `merge_group` event: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- GitHub PR templates: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
- GitHub CODEOWNERS: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- GitHub PR changed-files API: https://docs.github.com/en/rest/pulls/pulls

## Boundaries

- Skill output is guidance and coordination state, not enforcement.
- Enforcement belongs in GitHub branch protection, required checks, CODEOWNERS, PR templates, and scripts.
- Branch protection or ruleset enforcement must be verified remotely before marking it `OK`.
- Current repo truth stays in `docs/ai/*` and `docs/requirements/*`; this skill should not create a parallel project-status system.
