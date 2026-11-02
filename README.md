# DSH Share

<img src="assets/icon/AppIcon.png" alt="DSH Share icon" width="96" />

DSH Share is a macOS sharing tool that sends files, images, text and links from other apps on the **same Mac** to the **DeepSeek Harness desktop app** through the system Share menu. Shares appear as attachments in the **current thread’s input area**. Review them and send manually when ready.

English | [简体中文](README.zh-CN.md)

## Features

- **Finder:** select one or more regular files, then choose **Share → DeepSeek Harness**.
- **WeChat for Mac:** use **Other apps → Choose an app on this computer → DeepSeek Harness** when the content offers that option.
- Files, images, plain text and URLs exposed through a compatible macOS Share menu are accepted. Each share is limited to **128 files and 256 MiB in total**; folders are not supported.
- If DeepSeek Harness is not running, DSH Share attempts to open it. If opening fails, an error is reported to the user. Shared content remains queued locally until the app and plugin start.
- After confirmed forwarding, DSH Share immediately removes its local copies and forwarding records.

DSH Share provides a Universal 2 DMG containing Apple Silicon and Intel binaries — [download the latest release](https://github.com/bakkhos8/dsh-macos-share/releases/latest). Its setup assistant connects to Harness desktop automatically. Installation and everyday use require neither Python nor a standalone Node.js runtime. Source installation is also available; see [compatibility](docs/validation.md) for supported environments and verification limits.

## Download

Two installation paths are supported, and you only need one:

- **Option A — prebuilt DMG, for general users**: [latest release](https://github.com/bakkhos8/dsh-macos-share/releases/latest) — `DSHShare-<version>-universal2.dmg` plus its `.sha256`.
- **Option B — build from source, for professional developers**: clone this repository and follow [Option B](#option-b--build-and-install-from-source-for-professional-developers).

Changes between versions: [CHANGELOG.md](CHANGELOG.md).

## Before installing

You need:

- macOS **13 or newer**. Testing so far used an **Apple Silicon Mac running macOS 27.0.1**; Intel Macs and other OS versions are not yet verified.
- A working DeepSeek Harness desktop installation. The plugin interfaces were tested with **0.2.1-rc.5**.

Whichever path you pick, the result is the same two pieces: the native Share target (**DSHShare.app**) and the DeepSeek Harness plugin (**dsh-macos-share**). You never install both paths.

The inbox lock, cleanup command and plugin profile installer use a native executable bundled inside **DSHShare.app**. Installation and everyday use do not require Python or a separately installed Node.js runtime. The compiler is needed for source installation; the installed app uses macOS-provided runtime libraries.

### System permissions

DSH Share needs **two actions from you** and **three entitlements that macOS grants at install time without a prompt**. Nothing else is requested — no Full Disk Access, no Files & Folders, no Accessibility, Screen Recording, Automation, Notifications, Camera or Microphone.

| What you will be asked | Why it is needed | What breaks without it |
| --- | --- | --- |
| **Open Anyway** under **Privacy & Security** (first launch only) | The DMG build is ad-hoc signed and not notarized by Apple, so Gatekeeper blocks its first launch. | The setup assistant cannot start, so the app, helper and Share extension are never installed. |
| **General → Login Items & Extensions → Sharing → DeepSeek Harness** | macOS ships third-party Share extensions **disabled**; the entry is listed but inert until you enable it. | The system Share menu has no **DeepSeek Harness** item, so nothing can be shared. The assistant re-checks this step and tells you what to click. |
| **A running, configured DeepSeek Harness** (no OS prompt) | The plugin that receives shares runs inside Harness, not in the appex. | Shares stay queued in the local inbox until Harness and the plugin are running; the setup assistant otherwise reports it. |

Sandbox entitlements — declared in the code signature, granted at install, **no dialog ever appears**:

| Entitlement | Why it exists |
| --- | --- |
| `com.apple.security.app-sandbox` | macOS refuses to load a Share extension that is not sandboxed, so this one is mandatory for the entry to work at all. It grants no data access by itself. |
| `com.apple.security.files.user-selected.read-only` | The extension must read the bytes of the items **you** put into the Share menu. It is scoped to those hand-offs; the extension never browses folders. |
| `com.apple.security.temporary-exception.files.home-relative-path.read-write` = `/Library/Application Support/DSHShare/` | A sandboxed extension can otherwise write only its own container, which macOS protects (reading it would require Full Disk Access). This narrow exception lets the extension drop its inbox where the non-sandboxed Harness plugin can read it — the reason no broader folder permission is needed. |

Notes on the rest of the stack: the host app and its bundled native helper are **not sandboxed**, run as your user, use no privileged helper and need no `sudo`; installing into `~/Applications` needs no admin rights, and installing into `/Applications` only asks for a password if your account cannot write there. On the Harness side, the plugin runs inside Harness with your user's rights, reads only DSH Share's own directory (`~/Library/Application Support/DSHShare/`) and calls Harness' public plugin APIs; model access, network use and tool permissions for the shared files are whatever **your Harness configuration** allows. The project adds no telemetry and no API keys of its own.

## Install

Pick **one** of the following paths.

| | **Option A — DMG (general users)** | **Option B — from source (professional developers)** |
| --- | --- | --- |
| What you download | `DSHShare-<version>-universal2.dmg` from Releases | this repository |
| Extra tools | none | Xcode or Apple's Command Line Tools |
| Binary | prebuilt **Universal 2**, covers Apple Silicon and Intel, ad-hoc signed, not notarized | compiled on your Mac for your architecture, ad-hoc signed unless you pass `SIGN_ID` |
| Plugin installation | handled by the app's setup assistant, no Terminal | `./scripts/install-plugin.sh` |
| Suited to | everyday use: no terminal, no toolchain | professional developers: auditing the code, running commits that are not released yet, or signing with your own certificate |

### Option A — Install the DMG (for general users)

1. Install and open **DeepSeek Harness** once. Configure its model and agent, confirm a session works, then **Command-Q** to quit it completely.
2. Open the DMG, drag **DSHShare.app** into **Applications**, then eject the disk image.
3. Open **DSHShare** from Applications. The app is not notarized. If macOS blocks it, attempt to open it once, then choose **Open Anyway** for this app in **System Settings → Privacy & Security**.
4. Follow the Chinese-language assistant: **Prepare → Install → Enable sharing → Test a share**. It selects Harness desktop automatically. The sharing step checks the running receiver and system Share entry, and offers actions only for unmet checks. It rechecks when you return from settings; no profile selection or Terminal commands are needed.
5. On the final page, click **显示测试文件** (Show test file). In Finder, right-click the selected file and choose **Share → DeepSeek Harness**. First select a thread in Harness, then check that the test file appears in its input area without starting a reply. Close the assistant when finished.

You can also copy the app to your own `~/Applications` folder. A fixed local location keeps the share extension and helper available after ejecting the image. The disk image includes [installation and usage instructions in Chinese](docs/installation.zh-CN.txt). You can close the assistant after setup; it does not need to stay open for everyday sharing.

### Option B — Build and install from source (for professional developers)

Clone this repository, open Terminal in the project directory and run:

```bash
./scripts/build-app.sh --install
./scripts/install-plugin.sh
```

The first command compiles **DSHShare.app** with the local toolchain and installs it into `~/Applications` together with the registered Share extension; run it without `--install` to build into `build/` only. The second installs the receiving plugin into the **desktop** profile (it copies the plugin to `~/Library/Application Support/DSHShare/plugins/dsh-macos-share`; add `--dev` to symlink the repository instead). Existing native app installations are backed up under the project's ignored `backups/` directory.

Then:

1. Open DeepSeek Harness and check that **dsh-macos-share** is enabled in its plugin list. Restart DeepSeek Harness if the plugin has not appeared.
2. In **System Settings → General → Login Items & Extensions → Sharing**, enable **DeepSeek Harness** if needed.
3. Completely quit and reopen source apps that were already running, especially **WeChat**. Use **Command-Q**; closing a window is not sufficient.

Signing with your own certificate instead of the default ad-hoc signature:

```bash
SIGN_ID="Developer ID Application: Your Name (TEAMID)" ./scripts/build-app.sh --install
```

See [signing and installation](docs/signing.md) for notarization and for the macOS rule that a Share extension must be sandboxed and validly signed.

For a different existing DeepSeek Harness profile, replace only the second command with:

```bash
DSH_PROFILE_DIR="$HOME/.dsh/profiles/your-profile" ./scripts/install-plugin.sh
```

Enable this plugin in only one running profile for the shared inbox. An exclusive system lock blocks additional consumers. If another profile owns it, disable that profile's plugin, then reload the intended receiver. Completely quit all running receivers before installing or updating. Both paths uninstall the same way — see [Uninstall](#uninstall).

## Use it

### From Finder

1. Select your files and open the **Share** menu.
2. Click the **DeepSeek Harness icon**.
3. The files appear as attachments in the current Harness thread’s input area. Text and links become a `分享内容.txt` attachment.
4. Add your instructions, then click **Send** when ready. Sharing alone does not start the agent.

Select the receiving thread before sharing. Existing draft text and attachments are preserved. If no thread is open, select one to receive the pending share. A transfer already in progress stays bound to its original thread; return to that thread to finish it.

### From WeChat

Open the content's sharing options and choose **Other apps → Choose an app on this computer → DeepSeek Harness**. Available options depend on the content WeChat exposes to macOS; private formats such as mini-program cards or entire chat histories are not guaranteed.

**After installing or updating the extension, restart WeChat before trying again if it shows an old icon or forwarding does nothing.**

### If DeepSeek Harness does not open

If the app cannot be opened, an error is reported. Open DeepSeek Harness manually and confirm that **dsh-macos-share** is enabled. The saved share remains in the local inbox until it can be handled. Select a thread with an input area. Avoid repeatedly sharing the same item while checking a pending delivery, as each new share adds another attachment.

## Privacy and local data

Sharing puts attachments in the current Harness draft. The agent starts only after you send the draft. Model access, network transmission and tool permissions follow **your DeepSeek Harness configuration**; only share content you intend that agent to process.

The native extension hands content over through a local directory and does not need model API keys. This project adds no independent telemetry or analytics service.

| Location | Purpose |
| --- | --- |
| `/Applications/DSHShare.app` or `~/Applications/DSHShare.app` | Share menu target and setup assistant |
| `~/Library/Application Support/DSHShare/plugins/dsh-macos-share` | Plugin files installed by the default installer |
| `~/Library/Application Support/DSHShare/inbox` | Pending local copies of shares |
| `inbox/failed/` | Failed packages and their error details |

DSH Share does not keep a session history or an archive of completed shares. Once the Harness input area owns the attachments and confirms receipt, DSH Share immediately deletes the inbox copy, delivery state and temporary completion receipt. The session and attachments received by DeepSeek Harness are the forwarding result and are managed by Harness itself.

Interrupted cleanup resumes automatically when the receiver runs again. Confirmed completion records left by earlier versions are also removed, without an age limit. Failed packages remain available for diagnosis; do not publish inbox contents or logs containing shared data.

**Pending, unconfirmed and failed content never expires automatically.** Files are transferred through a bounded local stream into Harness-owned browser attachments. Text and links are attached as a UTF-8 text file. Draft attachments follow Harness’s own lifecycle; closing or reloading Harness may discard an unsent draft. DeepSeek Harness may impose additional attachment limits.

## Common problems

| Problem | What to do |
| --- | --- |
| Clicking DSHShare opens no window | Quit any running DSHShare in Activity Monitor, then open the current copy from Applications. Keep one installed copy and eject the installation disk image; an older copy still running can receive the open request. |
| Missing menu entry or old icon | Enable the extension in System Settings, then completely quit and reopen the source app. For WeChat, use Command-Q. |
| Nothing arrives in DeepSeek Harness | Open DeepSeek Harness, enable **dsh-macos-share**, and restart it after installing or updating the plugin. Check the intended profile. |
| A directory or a large file fails | Share at most 128 regular files and 256 MiB in total. Failed content is retained. |
| Very long inline text fails | Save it as a file and share the file. Inline text and manifest metadata together are limited to 1 MiB. |
| The plugin reports that the inbox is in use | Disable the other receiver, then reload the intended plugin. Do not remove `.consumer.lock`; the system releases ownership when its holder exits. |
| The plugin cannot start its native helper | Update the native app with `./scripts/build-app.sh --install`, then install the plugin and restart DSH. Update the native app and receiving plugin together. |
| A WeChat item cannot be forwarded | Retry after fully restarting WeChat. If its private card format is not exposed as text, a URL or a file, share the underlying link or saved file instead. |
| Installation or system security checks fail | See [signing and installation diagnostics](docs/signing.md). Signing checks and a visible menu entry alone do not prove a working share. |

Additional boundaries are listed in [known issues](KNOWN-ISSUES.md). Other source apps, including Safari, Preview and Mail, still need their own compatibility checks.

## Update

Quit DeepSeek Harness and DSHShare completely, replace **DSHShare.app** in Applications with the new version, then open it and run the setup steps again. Reopen Harness and the apps you share from (WeChat, Finder) afterwards. The native app and the receiving plugin are updated together; the installer keeps a private backup before changing existing configuration.

## Uninstall

1. Save your work and **Command-Q** to quit DeepSeek Harness completely.
2. Open the installed **DSHShare** from Applications and click **卸载** (Uninstall) immediately to the left of **开始安装** (Start installation). The same flow is also available from **DSH Share → 卸载 DSH Share…** in the macOS menu bar.
3. Review the removal summary, then confirm **卸载并移到废纸篓** (Uninstall and move to Trash). Close the window when complete, then reopen the apps you share from, such as WeChat, to refresh cached Share menus.

Uninstall removes the system share entry and the receiver from the Harness profiles recorded by the installer, then moves the app to Trash. Nothing else on your Mac is touched.

Standard profiles and custom profiles recorded by the installer are discovered automatically. See [known issues](KNOWN-ISSUES.md#uninstall--卸载) for manually installed, unrecorded configurations.

To pause receiving without uninstalling, disable **dsh-macos-share** in Harness.

## Distribution and marketplace

The receiving plugin is published as the npm package **`dsh-macos-share`** (the shorter name `dsh-share` was already taken by an unrelated plugin), so `dsh plugin add dsh-macos-share` installs it into a profile. The native share target still ships as the DMG.

DeepSeek Harness has no first-party plugin registry; discovery runs through the community index [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin). The submission entry and the maintainer-facing checklist live in [docs/market](docs/market/README.md).

## License

Source code, documentation and the original avatar artwork are available under [MIT](LICENSE). The artwork was created for this project and contains no third-party material.

DSH Share is an independently maintained integration and is not an official DeepSeek Harness distribution.
