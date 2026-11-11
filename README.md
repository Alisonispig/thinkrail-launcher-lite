# ThinkRail Launcher Lite

轻量级 ThinkRail 桌面代理启动器，仅对客户端进程设置代理，无需 TUN，不修改系统代理。使用 Tauri 2、Vue 3、Rust 构建，支持代理连通性检测、启动后收起至菜单栏，以及独立配置存储。

本项目基于 [Antigravity Launcher Lite](https://github.com/Alisonispig/antigravity-launcher-lite) 派生，以 MIT 许可证开源并保留上游版权声明。

## 使用

1. 打开自己的代理软件，确认 HTTP 或混合端口可用，无需开启 TUN。
2. 正常退出已打开的 ThinkRail（仅关窗口可能仍在后台运行）。
3. 打开 **ThinkRail Launcher Lite**，默认客户端路径为 `/Applications/ThinkRail.app`，代理为 `127.0.0.1:17891`；按实际情况修改。
4. 点击「检测并启动」，随后在 ThinkRail 内发送消息确认实际连通。

代理检测执行 HTTP CONNECT 和带证书校验的 HTTPS 请求，目标为 `https://chatgpt.com/backend-api/codex/responses`。无凭据请求可能返回 401、403、405 等 HTTP 状态，说明已收到目标响应，不代表登录或模型调用成功。此检测不覆盖全部提供方。

## 功能与边界

- 校验 ThinkRail 应用身份，macOS 从 Info.plist 读取实际 launcher 可执行路径，匹配 `ai.thinkrail.app`。
- 只给启动的进程设置大小写 HTTP_PROXY、HTTPS_PROXY、ALL_PROXY；本地回环连接加入 NO_PROXY，避免影响 ThinkRail 内置服务。
- 清除继承的冲突代理设置，不改系统代理，也不修改 ThinkRail 安装文件。
- 记住路径、主机、端口、语言、主题和启动后收起窗口的选择；配置与反重力启动器完全独立。
- 启动前识别已有实例，不自动退出用户客户端。成功启动后默认收起至菜单栏，退出启动器不会终止 ThinkRail。
- 不内置代理内核或节点；目前仅支持无需认证的 HTTP / 混合端口，不支持 SOCKS-only 或 PAC。
- 首版不包含客户端更新后自动恢复代理，更新重启后请正常退出并再次通过本启动器打开。

配置目录：`~/Library/Application Support/io.github.thinkrail-launcher-lite/config.json`。

## 开发与构建

使用 Node.js、项目固定的 Rust 1.99.1 及 Tauri 系统构建依赖。

```sh
npm ci
npm run lint
npm run build
cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
cargo clippy --locked --manifest-path src-tauri/Cargo.toml --all-targets -- -D warnings
cargo test --locked --manifest-path src-tauri/Cargo.toml
npm run tauri build -- --debug --bundles app
```

本机调试构建产物：`src-tauri/target/debug/bundle/macos/ThinkRail Launcher Lite.app`。正式构建使用 `npm run tauri build -- --bundles app`。不需要启动开发服务器。

## 来源与验证范围

源自 [Antigravity Launcher Lite](https://github.com/Alisonispig/antigravity-launcher-lite) 的 1.0.2 源码，复用界面、配置存储、代理握手、平台路径校验和菜单栏代码；删除原客户端的更新恢复流程，改用 ThinkRail 身份、独立应用标识和 Codex 检测目标。应用和托盘图标已重新设计，见 `doc/icon-design.md`。正式打包前运行 `python3 scripts/third_party_notices.py --target <Rust 目标三元组>`，生成随应用附带的第三方声明。

当前以 macOS Apple Silicon 为交付目标，Windows/Linux 适配代码仅沿用基础结构，未实机验证，不承诺对应平台可用。验证结果见 `doc/verification.md`。

本工具为独立非官方项目，与 ThinkRail 官方无隶属关系。
