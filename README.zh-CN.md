# DSH Share

<img src="assets/icon/AppIcon.png" alt="DSH Share 图标" width="96" />

DSH Share 是 macOS 本机分享工具，通过系统共享菜单，将**同一台 Mac** 上其他应用的文件、图片、文本和链接发送到 **DeepSeek Harness 桌面版**。分享内容会作为附件放入 **Harness 当前会话的输入区**，由你检查后手动发送。

[English](README.md) | 简体中文

<p align="center">
  <img src="docs/promo/animation/dsh-share-promo-loop.gif" alt="在 macOS 共享菜单里把文件分享进 DeepSeek Harness 草稿" width="420" />
</p>


## 功能

- **Finder：**选中一个或多个普通文件，选择「共享 → DeepSeek Harness」。
- **微信 Mac 版：**在提供该功能的内容上，选择「其他应用 → 选择电脑中的应用 → DeepSeek Harness」。
- 接收来源应用通过系统共享菜单提供的文件、图片、纯文本和链接。**每次最多 128 个文件、合计不超过 256 MiB，不支持文件夹。**
- DeepSeek Harness 未运行时，会尝试打开 DeepSeek Harness；如果打开失败，会向用户报错。分享内容会暂存在本机，待应用和插件启动后继续接收。
- 确认转发成功后，立即删除本工具里的分享副本和转发记录。

DSH Share 提供包含 Apple Silicon 和 Intel 两个架构的 Universal 2 DMG（[下载最新版本](https://github.com/bakkhos8/dsh-macos-share/releases/latest)），设置助手会自动连接 Harness 桌面版。安装及日常使用无需 Python 或单独的 Node.js。也可以选择从源码安装，兼容性范围见[兼容性说明](docs/validation.md)。

## 下载

支持两种安装方式，任选其一即可：

- **方式 A — 直接安装 DMG，适合普通用户**：[最新发布](https://github.com/bakkhos8/dsh-macos-share/releases/latest)，下载 `DSHShare-<version>-universal2.dmg` 及其 `.sha256`；
- **方式 B — 从源码编译安装，适合专业开发者**：克隆本仓库，按[方式 B](#方式-b--从源码编译安装适合专业开发者)操作。

版本变化记录：[CHANGELOG.md](CHANGELOG.md)。

## 使用前准备

需要具备：

- macOS **13 或更高版本**。目前实际验证环境为 **Apple Silicon、macOS 27.0.1**；Intel Mac 和其他系统版本尚未验证。
- 已能正常使用的 DeepSeek Harness 桌面版。本项目使用的插件接口已在 **0.2.1-rc.5** 验证。

两种方式最终装上的都是同样的两个部件：原生分享入口 **DSHShare.app** 与 Harness 接收插件 **dsh-macos-share**；只需按其中一种方式安装，不需要两条都走。

收件箱锁、清理命令和插件配置安装使用随 **DSHShare.app** 打包的原生程序，安装及日常使用均不依赖 Python，也不需要单独安装 Node.js。源码安装时需要编译工具；安装后的应用使用 macOS 自带的运行库。

### 系统权限

DSH Share 只需要你**操作两件事**，另外**三个 entitlement 在安装时由系统直接授予、不弹窗**。除此之外不申请任何权限——完全磁盘访问、文件与文件夹、辅助功能、屏幕录制、自动化、通知、相机／麦克风都不需要。

| 你会遇到的授权 | 为什么需要 | 不授权会怎样 |
| --- | --- | --- |
| 首次打开时在「**隐私与安全性**」选择「**仍要打开**」 | DMG 版本是 ad-hoc 签名、未经 Apple 公证，Gatekeeper 会拦下第一次启动。 | 设置助手起不来，App、helper 和分享扩展都无法安装。 |
| 「**通用 → 登录项与扩展 → 共享**」勾选 **DeepSeek Harness** | macOS 默认把第三方分享扩展**关着**，条目在列表里但不生效。 | 系统分享菜单里没有 **DeepSeek Harness**，什么都发不出去；助手第 3 步会复查并提示点击位置。 |
| 需要一个已配置好、正在运行的 DeepSeek Harness（无系统弹窗） | 真正接收分享的插件跑在 Harness 进程里，不在 appex 里。 | 分享内容留在本地收件箱，等 Harness 和插件启动后才投递；助手会提示未就绪。 |

沙盒 entitlement——写在代码签名里，安装即生效，**全程没有弹窗**：

| Entitlement | 存在的原因 |
| --- | --- |
| `com.apple.security.app-sandbox` | 系统拒绝加载非沙盒的分享扩展，所以它是分享入口能用起来的前提；它本身不授予任何数据访问。 |
| `com.apple.security.files.user-selected.read-only` | 扩展要读取**你**通过分享菜单交给它的条目；只覆盖这些交接内容，不会去浏览磁盘。 |
| `com.apple.security.temporary-exception.files.home-relative-path.read-write` = `/Library/Application Support/DSHShare/` | 沙盒扩展默认只能写自己的容器，而容器受系统保护（读取需要完全磁盘访问）。这条窄例外让扩展把收件箱放在非沙盒的 Harness 插件能读到的地方——正因如此才不需要申请更宽的文件权限。 |

其余部分：宿主 App 与包内 native helper **不沙盒**、以当前用户身份运行、没有特权 helper、不需要 `sudo`；装到 `~/Applications` 不需要管理员，装到 `/Applications` 仅在当前账户没有写权限时由系统提示输入密码。Harness 侧，插件在 Harness 进程内以你的用户身份运行，只读本工具自己的 `~/Library/Application Support/DSHShare/` 并调用 Harness 的公开插件接口；分享文件最终是否被模型处理、走哪条网络、能用哪些工具，取决于**你的 Harness 配置**。本项目没有自己的遥测，也不需要任何 API Key。

## 安装

下面两种方式**任选其一**。

| | **方式 A — 安装 DMG（适合普通用户）** | **方式 B — 从源码编译（适合专业开发者）** |
| --- | --- | --- |
| 需要下载 | Releases 里的 `DSHShare-<version>-universal2.dmg` | 本仓库 |
| 额外工具 | 无 | Xcode 或 Apple Command Line Tools |
| 二进制 | 预编译 **Universal 2**（Apple Silicon + Intel），ad-hoc 签名、未公证 | 在本机按你的架构编译，默认 ad-hoc 签名；可传 `SIGN_ID` 换证书 |
| 插件安装 | 由 App 的设置助手完成，无需终端 | `./scripts/install-plugin.sh` |
| 适合 | 普通用户：日常分享，不需要终端和编译工具 | 专业开发者：想审计代码、运行尚未发布的提交，或用自己的证书签名 |

### 方式 A — 安装 DMG（适合普通用户）

1. 先打开一次 **DeepSeek Harness**，配置好模型和 Agent，确认能新建会话，然后按 **⌘Q** 完全退出。
2. 打开 DMG，把 **DSHShare.app** 拖进 **Applications／应用程序**，再推出磁盘映像。
3. 从应用程序文件夹打开 **DSHShare**。App 未公证，若被系统拦截：先尝试打开一次，再到「**系统设置 → 隐私与安全性**」为它选择「**仍要打开**」。
4. 按中文设置助手依次操作：**准备 → 安装 → 启用共享 → 测试分享**。助手会自动选择 Harness 桌面版；「启用共享」这一步会检查接收端和系统分享入口，只为未就绪项提供操作，从系统设置返回后自动复查——无需选择配置名称，也不需要终端命令。
5. 在最后一页点击「**显示测试文件**」，在 Finder 里右键该文件选择「**共享 → DeepSeek Harness**」。先在 Harness 里选中一个会话，确认测试文件出现在输入区且没有触发回复，然后关闭助手。

也可以把 App 复制到自己的 `~/Applications`。固定在本机目录可以保证推出磁盘映像后分享扩展与 helper 仍然可用。磁盘映像内含[中文安装与使用说明](docs/installation.zh-CN.txt)。装好后助手可以关闭，日常分享不需要它常驻。

### 方式 B — 从源码编译安装（适合专业开发者）

克隆本仓库，在项目目录打开终端执行：

```bash
./scripts/build-app.sh --install
./scripts/install-plugin.sh
```

第一条用本机工具链编译 **DSHShare.app**，装进 `~/Applications` 并注册分享扩展；不加 `--install` 时只构建到 `build/` 不安装。第二条把接收插件装进 **desktop** profile（会复制到 `~/Library/Application Support/DSHShare/plugins/dsh-macos-share`，加 `--dev` 则软链仓库）。原有的原生 App 安装会备份到被 Git 忽略的 `backups/` 目录。

然后：

1. 打开 DeepSeek Harness，确认插件列表里的 **dsh-macos-share** 已启用；看不到就重启一次 Harness。
2. 到「**系统设置 → 通用 → 登录项与扩展 → 共享**」勾选 **DeepSeek Harness**（如果还没勾）。
3. 把安装前就在运行的来源应用完全退出再打开，微信务必用 **⌘Q**。

想用自己的证书签名而不是默认的 ad-hoc：

```bash
SIGN_ID="Developer ID Application: 你的名字 (TEAMID)" ./scripts/build-app.sh --install
```

公证流程、以及「分享扩展必须沙盒且签名有效」这条系统规则见[签名与安装](docs/signing.md)。

换用其他已存在的 Harness profile 时，只替换第二条命令：

```bash
DSH_PROFILE_DIR="$HOME/.dsh/profiles/你的-profile" ./scripts/install-plugin.sh
```

同一份共享收件箱只能由一个运行中的 profile 启用该插件：独占锁会挡住其他消费者。若别的 profile 占着锁，先禁用那边的插件再重新加载目标接收端；安装或更新前请完全退出所有接收端。两种方式的卸载流程相同，见[卸载](#卸载)。

## 如何使用

### 从 Finder 分享

1. 选中文件，打开「共享」菜单。
2. 点击 **DeepSeek Harness 的图标**。
3. 文件会作为附件进入 Harness 当前会话的输入区；文本和链接合并为 `分享内容.txt` 附件。
4. 检查附件、补充你的要求，再手动点击「**发送**」。仅分享不会启动 Agent。

分享前先在 Harness 选中接收会话。输入区原有的文字和附件会保留。没有打开会话时，分享会继续等待，选中会话后再接收。传输开始后会固定接收会话；途中切换会话时，回到原会话即可继续。

### 从微信分享

在内容的分享选项中，选择「**其他应用 → 选择电脑中的应用 → DeepSeek Harness**」。具体可用入口取决于微信向系统提供的内容；小程序卡片、完整聊天记录等微信私有格式不保证可直接转发。

**安装或更新扩展后，若微信仍显示旧图标或转发无反应，请先 ⌘Q 完全退出微信，再重新打开。**

### DeepSeek Harness 没有自动打开时

如果无法打开，系统会提示错误。请手动打开 DeepSeek Harness，并确认 **dsh-macos-share** 已启用。本地分享副本会保留，等待插件接收。打开一个有输入区的会话。排查期间不要反复分享同一内容，以免重复添加附件。

## 隐私与本地数据

点击分享后，内容会进入 DeepSeek Harness 的附件草稿；你手动发送后才会启动 Agent。模型访问、联网处理及工具权限以**你自己的 DeepSeek Harness 配置**为准，请只分享你愿意交给该 Agent 处理的内容。

原生扩展通过本机目录交接内容，不需要模型 API Key；本项目没有额外的遥测或统计服务。

| 位置 | 用途 |
| --- | --- |
| `/Applications/DSHShare.app` 或 `~/Applications/DSHShare.app` | macOS 共享入口与设置助手 |
| `~/Library/Application Support/DSHShare/plugins/dsh-macos-share` | 默认安装方式保存的插件文件 |
| `~/Library/Application Support/DSHShare/inbox` | 待处理的本地分享副本 |
| `inbox/failed/` | 失败包及错误信息 |

DSH Share 不保存会话历史，也不归档已完成的分享。Harness 输入区持有附件并确认收到后，**本工具立即删除收件箱里的分享副本、投递状态和临时完成回执**。DeepSeek Harness 收到的会话和附件属于转发结果，由 Harness 自身管理。

清理被中断时，接收端恢复运行后会自动继续；旧版本遗留的有效完成回执也会清除，不按天数保留。失败包会保留以便排查，不要把包含分享内容的收件箱或日志提交到公开仓库。

**待处理、尚未确认及失败内容不会按时间自动删除。** 文件通过本机流式传输交给 Harness 的附件草稿，文本和链接作为 UTF-8 文本文件。附件草稿遵循 Harness 自身的生命周期；关闭或重新加载 Harness 可能丢弃未发送的草稿。DeepSeek Harness 自身还可能有额外的附件限制。

## 常见问题

| 现象 | 处理方法 |
| --- | --- |
| 点击 DSHShare 没有窗口 | 先在「活动监视器」中退出 DSHShare，再从应用程序文件夹打开新版。保留一个安装副本，并推出安装磁盘；后台旧版可能接走打开请求。 |
| 菜单里没有入口，或头像还是占位图 | 在系统设置启用扩展，然后完全退出并重开来源应用。微信请使用 ⌘Q。 |
| DeepSeek Harness 没收到内容 | 打开应用，启用 **dsh-macos-share**，安装或更新插件后重启应用，并核对使用的 profile。 |
| 文件夹或大文件无法分享 | 每次分享不超过 128 个普通文件，合计不超过 256 MiB；失败内容会保留。 |
| 很长的内联文本分享失败 | 保存为文件再分享；内联文本与 manifest 元数据合计上限为 1 MiB。 |
| 插件提示收件箱被占用 | 停用另一个接收端，再重新加载需要使用的插件。不要删除 `.consumer.lock`；持有进程退出后系统会释放锁。 |
| 插件无法启动原生辅助程序 | 先运行 `./scripts/build-app.sh --install` 更新原生应用，再安装插件并重启 DSH。应用和接收插件需要一起更新。 |
| 某种微信内容无法转发 | 完全重启微信后重试；私有卡片若没有提供标准文本、URL 或文件，请改为分享原始链接或保存后的文件。 |
| 安装或系统安全检查失败 | 参阅[签名与安装排查](docs/signing.md)。静态签名通过、菜单里有入口，都不能单独证明分享成功。 |

更多边界见[已知问题](KNOWN-ISSUES.md)。Safari、预览、邮件等其他来源应用仍需分别进行兼容性验证。

## 更新

完全退出 DeepSeek Harness 和 DSHShare，用新版替换应用程序文件夹里的 **DSHShare.app**，打开它重新走一遍安装步骤。随后重新打开 DeepSeek Harness 和你用来分享的应用（微信、Finder）。原生 App 与接收插件会一起更新；安装器修改现有配置前会保留私有备份。

## 卸载

1. 保存正在处理的内容，用 **⌘Q 完全退出 DeepSeek Harness**。
2. 从应用程序文件夹打开 **DSHShare**，点击「开始安装」左侧的「**卸载**」。也可从顶部菜单「**DSH Share → 卸载 DSH Share…**」进入。
3. 查看移除范围，再确认「**卸载并移到废纸篓**」。完成后关闭窗口，重新打开微信等用来分享的应用以刷新共享菜单。

卸载会移除系统分享入口、安装记录中 Harness 配置里的接收插件，并将 App 移到废纸篓；其他插件与配置不受影响。

标准位置及安装记录中的 Harness 配置会自动处理。未被记录的手动安装配置，处理方式见[已知限制](KNOWN-ISSUES.md#uninstall--卸载)。

仅需暂停接收时，在 Harness 中停用 **dsh-macos-share** 即可。

## 分发与市场

接收插件发布为 npm 包 **`dsh-macos-share`**（更短的 `dsh-share` 已被一个无关插件占用），因此 `dsh plugin add dsh-macos-share` 即可把它装进 profile；原生分享入口仍通过 DMG 分发。

DeepSeek Harness 没有官方插件注册表，生态发现走社区索引 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)。投稿条目与维护者核对清单位于 [docs/market](docs/market/README.md)。

## 许可证

代码、文档及原创头像插画均采用 [MIT](LICENSE) 许可证。图标为本项目创作，不含第三方素材。

本项目独立维护，不是 DeepSeek Harness 官方发行版。
