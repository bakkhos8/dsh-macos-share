# 图标原图 / Icon originals (local only)

这个目录是本地放原图的工作区：png / jpg / webp / heic 都行（svg 请先导出成位图）。除本 README 外整个目录被 `.gitignore` 忽略，**原图本身不进仓库**，避免把未定稿素材和候选图推到公开历史里。

仓库里跟踪的是处理后的产物：

| 产物 | 位置 | 规格 |
|---|---|---|
| 应用图标主文件 | `assets/icon/AppIcon.png` | 1024×1024 透明画布，中间 824×824 圆角方形（Apple 图标网格） |
| 分享菜单小尺寸变体 | `assets/icon/AppIcon-small.png` | 同上，但取原图主体放大，供 16/32/64px 使用 |
| 插件/市场图标 | `plugins/dsh-macos-share/icon.png` | 圆角方形画面本身，256×256 |
| `.icns` 及各尺寸 | `build/`（构建产物） | `scripts/build-icons.sh` 生成 16–512 含 @2x，写入 App 与 appex |

换图流程：把新原图放进本目录并选定一张 → 用同一套网格/超椭圆遮罩重新合成上面三个文件（`assets/icon/AppIcon.png`、`assets/icon/AppIcon-small.png`、`plugins/dsh-macos-share/icon.png`）→ 运行 `./scripts/build-app.sh --install` 重新生成并注册 `.icns` → 重启来源应用（微信请 ⌘Q）刷新缓存的分享菜单图标。Dock 图标缓存可用 `killall Dock` 刷新。

分享菜单里的图标通常只有 16–32px；主体居中、细节少的图在这个尺寸下最清楚。

## 素材授权

图标美术的授权说明见 [`apps/DSHShare/Resources/README.md`](../../apps/DSHShare/Resources/README.md)。原图与合成产物都受同一份说明约束，不因放在本目录而改变。
