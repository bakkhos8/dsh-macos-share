# Avatar icon / 头像图标

The icons shipped by this project come from **`assets/icon/AppIcon.png`**, a 1024×1024 macOS-grid composition (824×824 squircle artwork on a transparent canvas). The artwork was created for this project by its maintainer; the plugin and marketplace tile are derived from the same composition.

本项目的图标源文件是 **`assets/icon/AppIcon.png`**：按 macOS 图标网格合成的 1024×1024 PNG（824×824 圆角方形画面 + 透明画布），插画由本项目维护者为本项目创作；插件与市场图标由同一份合成图派生。

The artwork is original work made for DSH Share. No third-party material is included, and it is distributed under the same [MIT license](../../../LICENSE) as the code and documentation.

图标为本项目原创，不含第三方素材，随代码与文档一起以 [MIT 许可证](../../../LICENSE) 分发。

`scripts/build-icons.sh` packages the master PNG into every standard macOS icon size; `scripts/build-app.sh` installs the same `.icns` into both the containing app and its Share extension, so the Dock icon and the Share menu entry stay identical. The receiving plugin ships the squircle crop of the same artwork as `plugins/dsh-macos-share/icon.png` for the DeepSeek Harness plugin list and the marketplace tile.
