# 本机验证记录

日期：2026-11-11；版本：0.1.0；平台：macOS Apple Silicon。

## 已完成

- ESLint：`npm run lint` 通过，无错误或警告。
- Vue / TypeScript 检查与生产前端构建：`npm run build` 通过。
- Rust 格式检查、Clippy（all-targets、warnings as errors）通过。
- Rust 测试：12 项通过，覆盖 HTTP CONNECT 的成功/认证/拒绝/畸形响应、TLS 失败、代理地址校验、配置持久化与损坏备份、未来版本保护、子进程环境隔离与参数字面量、macOS 应用身份与 launcher 路径解析。
- 应用打包：`npm run tauri build -- --debug --bundles app` 成功。
- 产物为 arm64，应用标识 `io.github.thinkrail-launcher-lite`，与原启动器配置隔离。
- 调试构建的初始签名完整性检查失败；对本地产物执行 `codesign --force --deep --sign -` 后，严格签名完整性检查通过。此为 adhoc 本地签名，不是 Developer ID 签名或公证。

## 验证边界

此前已在本机确认：使用显式的 HTTP_PROXY / HTTPS_PROXY / ALL_PROXY 环境，通过 macOS open 启动 ThinkRail 后，用户报告对话恢复。启动器复用这些环境变量，并通过本机 helper 测试验证子进程可以收到代理环境。

本次没有启动开发服务器，没有退出或重启用户当前运行的 ThinkRail，没有用新启动器进行真实 ThinkRail 对话验收，也没有做新启动器的原生界面交互验收。启动器采用与上游一致的可执行文件直接启动方式，实际 ThinkRail 启动与长期联网仍需用户使用验证。Windows/Linux 未实机验证。

原 `antigravity-launcher-lite` 源码未修改。初始验证时项目尚未提交、推送或公开发布。

## 图标更新验证（2026-11-11）

- 已替换界面图标、桌面各尺寸 PNG、ICO、ICNS、彩色托盘图标和 macOS 单色模板图标；生成方式与提示词见 `icon-design.md`。
- 平台验证：本机 macOS Apple Silicon 上 `npm run lint`、`npm run build`、`cargo fmt`、`cargo clippy --locked --all-targets -- -D warnings`、`cargo test --locked` 均通过，Rust 测试 12 项通过；Rust 命令使用 `src-tauri/Cargo.toml`。
- `npm run tauri build -- --debug --bundles app` 成功，已更新本地调试应用。已检查源图透明通道、32 像素应用图标和单色托盘资源；未启动原生界面，未验证 Dock 缓存或菜单栏实际显示，未对本次产物重新做签名验收。Windows/Linux 未实机验证。
- 真实客户端对话验证：本次未执行；未启动、退出或重启 ThinkRail，未读取客户端账号数据。
- 未启动开发服务器，未推送或发布。

## 开源仓库准备（2026-11-11）

- 根据用户授权，以公开仓库 `Alisonispig/thinkrail-launcher-lite` 开源；同步 ThinkRail 专属项目描述，保留上游 MIT 版权声明并添加本项目版权声明。
- 沿用上游的三平台 GitHub Actions 验证流程，并增加 ESLint；该流程只验证和编译，不自动发布安装包。
- 补齐第三方声明生成脚本，本机 macOS arm64 目标生成成功。构建产物、依赖目录、环境文件和生成的声明文件不进入 Git。
- 本机平台验证：`npm run lint`、`npm run build`、`cargo fmt`、`cargo clippy --locked --all-targets -- -D warnings`、`cargo test --locked` 通过；12 项 Rust 测试通过。Windows/Linux 结果以远程 CI 为准，编译验证不等同于实机交互验收。
- 真实客户端对话验证：本次未执行，未启动或重启 ThinkRail。

## 应用内更新验证（0.1.1，2026-11-11）

- 本机平台：macOS Apple Silicon。`npm run lint`、`npm run build`、`cargo fmt`、`cargo clippy --locked --all-targets -- -D warnings`、`cargo test --locked` 通过；Rust 测试 14 项通过。新增测试覆盖下载地址限制、正确签名包、篡改包、清单版本伪造、降级和预发布版本拒绝。签名测试使用一次性测试密钥，私钥未保留。
- Python 更新清单测试 3 项通过，覆盖四平台合并、缺包、缺签名及非法版本。两份工作流通过 YAML 语法解析，发布输入的工程版本一致性检查在本地通过；远程构建尚未运行。
- 本地 `npm run tauri build -- --debug --bundles app` 在提供维护者密钥后成功，生成 0.1.1 应用、`.app.tar.gz` 和 `.sig`。确认签名可信注释绑定 0.1.1，内置公钥与本地签名公钥一致；实际产物尚未走一轮升级安装。
- 原生界面验证：打开本地新版应用，设置页显示更新入口；点击检查后显示进行中状态，并锁定冲突操作。当前直连 GitHub 发生网络超时，界面正确提示切换连接后重试，按钮恢复可用。未下载或安装真实更新，未替换系统应用目录中的应用。
- 平台限制：Windows/Linux 及 macOS Intel 尚未实机验证。macOS 原生下载、写入替换和重启闭环须在正式签名 Release 可用后验收。本次更新包签名不代表 Apple Developer ID 签名或公证验收。
- 真实客户端对话验证：本次未执行；未启动、退出或重启 ThinkRail。
- 签名私钥保存在仓库外，权限 0600，已配置到本仓库的 GitHub Actions Secret。开源仓库只包含公钥和测试签名。
- 未启动开发服务器；本次功能改动尚未推送，未创建或公开发布 Release。

## 对齐 Antigravity 1.0.2 发布准备（2026-11-11）

- 用户明确要求按 Antigravity 的版本与发布流程执行，并要求以后两个项目配套发布。ThinkRail 版本统一为 1.0.2；此前本地 0.1.1 未公开发布。Antigravity 已公开的 1.0.2 保持不变。
- 对齐七个安装包/应用 ZIP、架构与代码签名完整性检查、CI 安装/启动烟测、BUILD-METADATA 和 SHA256SUMS。新增的签名更新包、签名与 latest.json 也纳入总校验文件；静态清单复用 Windows/Linux 安装包，不重复分发同一内容。
- 更新清单 Python 测试增至 4 项，新增覆盖全部 16 个发布附件的收集与校验文件完整性；工作流 YAML 语法和工程版本一致性检查通过。远程构建与公开结果在完成后补记。
- 两仓库 AGENTS.md 已写入配套发布约定，Antigravity 本次仅维护文档，不重新打包或覆盖旧附件。
- 首轮远程 Windows 测试在测试程序入口以 `0xc0000139` 退出，没有进入用例。排查到 [Tauri 上游的模拟应用测试清单问题](https://github.com/tauri-apps/tauri/issues/13419)，为 MSVC 的所有链接目标显式嵌入与 Tauri 默认一致的 Common Controls v6 清单，避免只有应用 exe 获得清单而 lib 单元测试缺失；不申请额外权限。签名测试内容另通过 `.gitattributes` 保持原始字节，不随 Windows 换行设置改变。
- 首轮打包已取消，修复后将从同一新提交重新运行整批验证与打包，不混合旧产物。

## 1.0.2 正式发布与升级验收（2026-11-11）

- 正式 Release：<https://github.com/Alisonispig/thinkrail-launcher-lite/releases/tag/v1.0.2>。已公开、设为 Latest，非 prerelease；标签与构建元数据均指向 `81ab82c5b19173b26cc4970d447be5687bc79ed1`。
- 常规三平台验证运行 `43001492541` 成功。Windows 入口问题修复后，普通验证又发现 Python 默认 CP1252 导致中文读取/输出失败；现显式使用 UTF-8 并修正测试读取。该后续提交 `d67cc61` 只改 CI 与 Python 测试，不改变应用代码；发布工作流原本已设置 PYTHONUTF8。
- 发布运行 `43000283241` 的四个打包任务全部成功，包含 Rust 测试、Clippy、Python 清单测试、前端 lint/build、依赖许可生成、原生安装包、版本/架构/签名完整性检查、CI 安装与启动烟测。四个平台统一来自 `81ab82c`。
- 初次及重跑时，集成令牌新建草稿被 GitHub 403 拒绝。维护者账号创建对应草稿并固定构建提交后，仅重跑草稿任务，最终汇总上传成功；未重新打包、未混用其他提交产物，未扩大仓库默认令牌权限。
- 已公开 16 个附件：七个常规安装包/应用 ZIP、两个 Mac 更新 tar.gz、四份更新签名、latest.json、BUILD-METADATA.json、SHA256SUMS.txt。全部下载后核对资产字节数、GitHub 资产摘要、总 SHA-256、版本及构建提交；四份更新包另通过公钥密码学校验和签名版本绑定检查。两个 Mac ZIP 均通过本机严格签名完整性、应用身份、版本和 arm64/x86_64 架构核对。
- 原生应用内升级：工作区中的 0.1.1 测试应用经启动页代理检查正式端点，发现 1.0.2；点击「下载安装并重启」后自动下载、替换、重启。界面与 Info.plist 均显示 1.0.2，可执行文件哈希与 CI arm64 正式包一致，签名完整；默认路径、代理和开关正常恢复。事后复核发现升级前后均无落盘配置文件，前述辅助脚本比较的是“文件不存在”状态，不能当作配置文件哈希保留的证据。已有配置文件的真实升级字节保留尚待验收，Rust 配置兼容与持久化测试已通过。
- 本机已安装入口 `/Applications/ThinkRail Launcher Lite.app` 也已换为经校验的 arm64 正式包并打开，显示 1.0.2。只正常退出两个启动器实例，没有操作 ThinkRail 客户端。原 0.1.0 应用备份在忽略目录 `release-assets/local-before-1.0.2-0kt338n8/ThinkRail Launcher Lite.app`。
- 平台与真实客户端边界：macOS Apple Silicon 的启动器升级闭环已验收；Intel Mac、Windows、Linux 的真实设备升级仍待验收。未执行真实 ThinkRail 对话，未启动/退出/重启 ThinkRail，未读取其账号数据。Apple Developer ID、公证和 Windows Authenticode 均未宣称完成。
- Antigravity 保持已公开的 1.0.2，本次维护文档提交 `68fbb96` 的三平台验证运行 `42998737366` 成功；以后两个仓库按同一批次、同版本号准备与发布。
- 本机验收结果在公开后补入 Release 正文和维护文档；标签与全部附件（包括构建时的 latest.json 说明快照）保持原字节，不覆盖已公开安装包。
