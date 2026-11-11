# 应用内更新

设置页提供「检查更新」和「下载安装并重启」。更新针对本启动器，保留独立配置，不关闭或重启 ThinkRail。旧版 0.1.0 没有更新模块，需要先安装一次 1.0.2，之后才可使用应用内更新。

## 更新来源与安装

- 使用 Tauri 2 官方 updater 插件；固定读取本仓库 `releases/latest/download/latest.json`。没有公开的更新清单或 GitHub 无法访问时提示重试，不误报为最新版本。
- 手动检查，不在启动时下载。网络默认直连并禁用自动代理发现；用户可显式使用启动页校验过的 HTTP 代理，不改变系统代理设置。
- IPC 只接受是否使用代理及其主机、端口；不接受下载地址、密钥、安装路径、版本覆盖或命令行参数。检查结果只保存在 Rust 内存，安装操作只能使用该结果。
- 更新只接受更高的正式版本。下载地址必须属于本仓库的 HTTPS Release 附件路径，下载和安装均验证内置公钥对应的签名；签名必须绑定清单声明的版本，拒绝篡改包、重放旧包、降级和预发布版本。
- 下载显示进度，失败可重试。验证成功后使用插件安装并重启启动器；Windows 由 NSIS 更新进程接管并重新打开应用。
- macOS 需要将应用放在可写目录，不能从只读 DMG 内更新。Windows 使用当前用户安装；Linux 更新包使用 AppImage。各平台真实安装升级必须分别验收，不能以编译通过替代。

技术依据：[Tauri updater 文档](https://v2.tauri.app/plugin/updater/)。更新包的 minisign 签名用于校验发布来源，不等同于 Apple Developer ID 签名或公证。

## 签名密钥

公钥写入 `src-tauri/tauri.conf.json`。维护者私钥保存在仓库外的 `~/.config/thinkrail-launcher-lite/updater.key`，文件权限为 0600。请单独备份；丢失后无法继续向信任旧公钥的已安装应用发布更新。测试目录只包含一次性测试密钥的公钥、签名和测试内容，不包含私钥。

GitHub 手动构建工作流需要仓库 Actions Secret `TAURI_SIGNING_PRIVATE_KEY`，值为维护者私钥文件的完整内容；若私钥有密码，再设置 `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`。不要把私钥写入仓库、日志或 Release 附件。

2026-11-11 已为本仓库配置 `TAURI_SIGNING_PRIVATE_KEY`；当前私钥没有额外密码。该配置不触发构建或发布。

本机签名构建示例：

```sh
export TAURI_SIGNING_PRIVATE_KEY="$HOME/.config/thinkrail-launcher-lite/updater.key"
export TAURI_SIGNING_PRIVATE_KEY_PASSWORD=''
python3 scripts/third_party_notices.py --target aarch64-apple-darwin
npm run tauri build -- --bundles app
```

`tauri build` 自动把应用版本写入签名的可信注释，`requireSignedVersion` 强制校验该版本。不带版本的旧格式签名不能用于此项目。

## 维护者发布流程

1. 同步修改 `package.json`、`package-lock.json`、`src-tauri/Cargo.toml`、`src-tauri/Cargo.lock`、`src-tauri/tauri.conf.json` 的版本，并填写 `doc/releases/<版本>.md`。
2. 完成检查与必要的平台安装升级验收，按项目约定取得用户推送/发布授权。
3. 按 [两个启动器的配套发布](release-policy.md) 同批次准备版本；推送后手动运行 `release.yml` 的「打包发布（含签名更新包）」工作流。流程沿用 Antigravity 的七个安装包/应用 ZIP、架构检查、安装/启动烟测和校验文件，并生成四平台签名更新包与 `latest.json`，上传至同一提交对应的 Release 草稿；任一平台失败不会创建草稿。
4. 检查草稿的目标提交、版本、说明、四个平台更新包、签名及 `latest.json` 后，再明确发布为正式 Release。草稿不能被用户更新端点发现；不要将只支持部分平台的包标记为最新正式版。

`scripts/updater_manifest.py` 负责收集与合并清单；`python3 -m unittest discover -s scripts -p 'test_*.py'` 验证缺包、缺签名、版本输入和平台合并。
