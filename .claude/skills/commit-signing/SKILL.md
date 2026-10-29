---
name: commit-signing
description: AI 助手在本仓库提交 git 时必须遵守的署名规范：提交说明里写明由哪个 AI 工具完成，并在末尾加 Co-Authored-By 尾注。凡是由 AI 编写或修改代码并执行 git commit 时都要使用。
---

# AI 提交署名规范

凡是由 AI 助手（Claude Code、Codex、Cursor、Copilot、Gemini 等）完成修改并执行 `git commit` 的提交，都必须在提交说明里署名。目的是让 `git log` 和 GitHub 能看出哪些改动由哪个 AI 完成。

## 两处署名

1. **正文里的声明句**，单独一行，写明是哪个工具完成的：

   ```
   Fix made by <工具名>.
   ```

   修复用 `Fix made by`，新功能或其他改动用 `Change made by`。`<工具名>` 写产品名，例如 `Claude Code`、`Codex CLI`、`Cursor`。

2. **末尾的 Co-Authored-By 尾注**（git trailer），写明具体模型：

   ```
   Co-Authored-By: <模型名> <邮箱>
   ```

   - 模型名写实际使用的模型和版本，例如 `Claude Opus 5.5`，不要笼统写 "AI"。
   - 邮箱用该工具官方文档给出的 noreply 地址（Claude Code 使用 `noreply@anthropic.com`）。工具没有官方地址时，不要编造厂商邮箱，改用 `<模型名去空格小写>@noreply.invalid`，例如 `gpt-5@noreply.invalid`。
   - GitHub 只有在邮箱关联到账号时才会显示头像，用 `.invalid` 地址不会关联任何人，这是预期行为。

## 格式要求

尾注只有满足以下格式，git 和 GitHub 才会把它识别为 trailer：

- 尾注必须位于提交说明的**最后一段**，与前面正文之间**空一行**。
- 尾注段里只能是 `Key: value` 形式的行，声明句不能放在这一段。
- 键名固定写 `Co-Authored-By`，冒号后加一个空格。

完整示例（本仓库提交 `a305ab8` 的实际说明）：

```
Reject a missing IA_LEARNING_CONFIG_PATH instead of falling back

A set but mistyped IA_LEARNING_CONFIG_PATH used to fall through to the
user or repository credential file, silently using another key. It is
now binding: a missing file raises an error naming the variable.

Fix made by Claude Code.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

结构依次是：标题行（英文祈使句，约 50 字符以内）、空行、正文（说明为什么改、改了什么）、空行、声明句、空行、尾注。

## 提交命令

多行说明不要用多个 `-m` 拼接，改为从标准输入或文件读取，避免换行和引号出错。

Git Bash / Linux / macOS：

```bash
git add <具体文件>
git commit -F - <<'EOF'
<标题行>

<正文>

Fix made by <工具名>.

Co-Authored-By: <模型名> <邮箱>
EOF
```

PowerShell：先把说明写入临时文件（UTF-8），再执行：

```powershell
git commit -F $env:TEMP\commit-msg.txt
```

## 不要做的事

- **不要修改作者和提交者。** 不要用 `--author`，也不要改 `git config user.name/user.email`；作者仍是仓库所有者，AI 只出现在尾注里。
- 不要用 `git add -A` 或 `git add .`，只暂存本次改动的文件。
- 不要 `--amend` 或改写已有提交来补签名，除非用户明确要求。
- 用户没要求时不要推送（`git push`）。
- 不要冒用其他工具或模型的名字；用的是哪个就写哪个。

## 提交后自查

```bash
git log -1 --format=%B                                # 查看完整说明
git log -1 --format=%B | git interpret-trailers --parse   # 应输出 Co-Authored-By 那一行
git log -1 --format='%an <%ae>'                        # 作者应仍是仓库所有者
```

第二条命令没有输出，说明尾注格式不对（通常是缺少空行，或尾注段里混入了别的文字），需要修正。
