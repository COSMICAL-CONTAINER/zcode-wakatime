# zcode-wakatime · 让 WakaTime 统计 ZCode 使用时长

[ZCode](https://zcode.z.ai)（Z.ai 的 GLM 氛围编程工具）**没有官方 WakaTime 插件**——你在 ZCode 里干活的时间，WakaTime 完全统计不到（AI 分析页能看到 GLM 的 token 消耗，但那是另一条日志解析管道，不计时长）。

本插件用 ZCode 钩子补上这块：每次提交提示词、每次工具调用后自动发 WakaTime 心跳，使用时长按工作目录归属项目，与 VSCode 插件并存不冲突。单文件、零第三方依赖（仅 Python 标准库）、Windows/Linux/macOS 通用。

## 一键安装（推荐：直接丢给 ZCode 里的 GLM）

把下面整段话复制发给 ZCode 会话，GLM 会自动完成全部安装：

```text
请帮我安装 zcode-wakatime 插件（让 WakaTime 统计你的使用时长），仓库：
https://github.com/COSMICAL-CONTAINER/zcode-wakatime

步骤：
1. 下载仓库里的 zcode_wakatime_hook.py 到固定目录（如 ~/.zcode/zcode-wakatime/）
2. 编辑 ~/.zcode/cli/config.json，在 hooks.events 的 UserPromptSubmit 和 PostToolUse
   两个数组里各追加一个钩子块（保留已有钩子，不要删改别的）：
   {"hooks":[{"type":"process","command":"python",
     "args":["<脚本绝对路径>"],"timeoutMs":5000,"statusMessage":"WakaTime 心跳"}]}
3. 确认 hooks.enabled 为 true，改完校验 JSON 合法
4. 完成后提醒我重启 ZCode 会话生效
```

> **Windows 提示**：如果安装后每次触发钩子会闪黑色命令行框，把钩子里的 `"command": "python"` 换成 `"command": "pythonw"`（或 pythonw.exe 的完整路径）即可——pythonw 是无控制台版本，效果完全相同。

> 前置：本机装过任意 WakaTime 编辑器插件（`~/.wakatime/` 下有 wakatime-cli、`~/.wakatime.cfg` 里有 key）。没装过的话先在 VSCode 里装个 WakaTime 插件并登录一次。

## 方式二：手动安装

见上一节"一键安装"里的步骤 2-3，用编辑器改 `~/.zcode/cli/config.json` 即可；或把 README 直接丢给任何 AI 编码工具照做。

## 工作原理

- 钩子（`hooks/hooks.json`）在 UserPromptSubmit / PostToolUse 触发脚本；脚本读取事件 JSON 里的 `cwd` 作为项目目录
- 同一项目 **120 秒节流**（WakaTime 插件标准行为），状态存于 `~/.wakatime/zcode-wakatime/` 的 marker 文件 mtime，无内容写入
- 以**分离进程**调用 `wakatime-cli --entity ZCode --entity-type app --project <目录名> --category coding`，钩子毫秒级返回，不阻塞会话
- 断网自动走 wakatime-cli 离线队列，联网补发

## 类别说明

心跳类别用 `coding`——实测这是唯一计入编码时长的类别；`ai coding` 类别只进 WakaTime 的 AI 分析页、不产生时长（已实测验证）。想单独归类改脚本里的 `--category` 即可。

## 目录结构

```
zcode_wakatime_hook.py        钩子脚本（单文件，仅 Python 标准库）
hooks/hooks.json              钩子声明
.zcode-plugin/plugin.json     ZCode 插件清单（为将来上架预留）
```

## 隐私

本插件不上传任何代码内容：心跳只含项目名、时间戳和类别；WakaTime API Key 始终留在本机 `~/.wakatime.cfg`，不经过本插件读写。

## 许可

MIT License © 2026 [COSMICAL-CONTAINER](https://github.com/COSMICAL-CONTAINER)

协作：ZCode 智能体（GLM，Z.ai）

## 致谢

- [WakaTime](https://wakatime.com) —— 程序员时长统计
- [ZCode](https://zcode.z.ai) —— GLM 氛围编程工具
