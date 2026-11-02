# Changelog / 更新记录

## 0.2.0 — 2026-11-02

First public release.

- macOS Share menu target (`DSHShare.app` + sandboxed Share Extension) for DeepSeek Harness, shipped as a Universal 2 (arm64 + x86_64) DMG.
- Shares append attachments to the **current thread’s input area** in Harness; the receiver never creates a session, submits a prompt or starts an agent. Text and links are delivered as a `分享内容.txt` attachment.
- Receiving plugin `dsh-macos-share` for the desktop profile, with an exclusive native inbox lock, bounded streaming transfer and immediate cleanup after confirmed draft admission.
- Four-step setup assistant (prepare → install → enable sharing → test) that connects to Harness desktop automatically and needs no Terminal, Python or standalone Node.js.
- New application icon.
- Documentation: [design](docs/design.md), [signing and diagnostics](docs/signing.md), [compatibility and verification](docs/validation.md), [known issues](KNOWN-ISSUES.md), [marketplace listing](docs/market/README.md).

Install: `DSHShare-0.2.0-universal2.dmg` from the [latest release](https://github.com/bakkhos8/dsh-macos-share/releases/latest). The DMG is ad-hoc signed and not notarized; see [signing](docs/signing.md).

---

## 0.2.0 — 2026-11-02

首个公开版本。

- 为 DeepSeek Harness 提供 macOS 分享菜单入口（`DSHShare.app` + 沙盒 Share Extension），以 Universal 2（arm64 + x86_64）DMG 分发。
- 分享内容作为附件追加到 Harness **当前会话的输入区**；接收端不新建会话、不提交提示词、不自动启动 Agent。文本和链接以 `分享内容.txt` 附件交付。
- 桌面 profile 接收插件 `dsh-macos-share`：原生独占收件箱锁、有界流式传输、草稿确认后立即清理。
- 四步设置助手（准备 → 安装 → 启用共享 → 测试分享），自动连接 Harness 桌面版，无需终端、Python 或单独的 Node.js。
- 新的应用图标。
- 文档：[架构](docs/design.md)、[签名与诊断](docs/signing.md)、[兼容性与验证](docs/validation.md)、[已知限制](KNOWN-ISSUES.md)、[市场收录](docs/market/README.md)。

安装：从[最新发布](https://github.com/bakkhos8/dsh-macos-share/releases/latest)下载 `DSHShare-0.2.0-universal2.dmg`。DMG 使用 ad-hoc 签名、未经 Apple 公证，详见[签名说明](docs/signing.md)。
