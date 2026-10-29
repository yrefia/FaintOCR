# AI 助手须知

## 提交署名（必须遵守）

任何 AI 助手在本仓库执行 `git commit` 前，都必须先阅读并遵守 [`.claude/skills/commit-signing/SKILL.md`](.claude/skills/commit-signing/SKILL.md)。要点：

- 正文单独一行声明：`Fix made by <工具名>.`（非修复类改动写 `Change made by <工具名>.`）。
- 说明最后一段、前面空一行，写尾注：`Co-Authored-By: <模型名> <邮箱>`。
- 不修改作者和提交者，只暂存本次改动的文件，未经要求不推送。
- 提交后运行 `git log -1 --format=%B | git interpret-trailers --parse`，确认能输出尾注行。
