# zcode-wakatime · 让 WakaTime 统计 ZCode 使用时长

[ZCode](https://zcode.z.ai)（Z.ai 的 GLM 氛围编程工具）没有官方 WakaTime 插件——你在 ZCode 里干活的时长，WakaTime 完全统计不到（AI 分析页能看到 GLM 的 token/成本，那是另一条日志解析管道，不计时）。

这个项目用 **ZCode 钩子** 补上这块：每次提交提示词、每次工具调用后，自动向 WakaTime 发一条心跳，让 ZCode 的使用时长以项目为单位计入 WakaTime。

## 效果

- WakaTime 的"编辑器"维度会多出一个来源 `zcode-wakatime`，项目按你 ZCode 的工作目录自动归属
- 与 VSCode 插件并存不冲突：VSCode 记 VSCode 的，ZCode 记 ZCode 的
- 免费 WakaTime 账号即可

## 安装

前置：Python 3；本机装过任意 WakaTime 编辑器插件（`~/.wakatime/` 下有 `wakatime-cli` 和 `~/.wakatime.cfg`）。

1. 把本目录放到任意固定位置（下面配置里的路径要对应改）
2. 编辑 `~/.zcode/cli/config.json`，在 `hooks.events` 的 `UserPromptSubmit` 和 `PostToolUse` 数组里各追加一段（若已有其他钩子，追加进外层数组即可）：

```json
{
  "hooks": [
    {
      "type": "process",
      "command": "python",
      "args": ["C:\\path\\to\\zcode-wakatime\\zcode_wakatime_hook.py"],
      "timeoutMs": 5000,
      "statusMessage": "WakaTime 心跳"
    }
  ]
}
```

3. 若 `hooks.enabled` 不是 `true`，改为 `true`。重启 ZCode 会话生效。

## 工作原理

- 钩子每次触发时把事件 JSON 里的 `cwd` 作为项目目录，以**分离进程**调用 `wakatime-cli --entity ZCode --entity-type app --project <目录名> --category coding`，钩子本身毫秒级返回，不阻塞会话
- 同一项目 120 秒内只发一条心跳（WakaTime 插件标准节流），状态存在 `~/.wakatime/zcode-wakatime/` 的 marker 文件 mtime 里，无额外写入
- `wakatime-cli` 自带离线队列，断网时本地暂存、联网自动补发

## 类别说明

默认发 `coding` 类别——实测这是唯一计入编码时长的类别；`ai coding` 类别的心跳只进 WakaTime 的 AI 分析页、**不产生时长**（实测验证）。想让 ZCode 时间单独归类的话改脚本里的 `--category` 即可。

## 文件

```
zcode_wakatime_hook.py   钩子脚本（单文件，仅 Python 标准库，Windows/Linux/macOS 通用）
```
