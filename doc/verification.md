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
