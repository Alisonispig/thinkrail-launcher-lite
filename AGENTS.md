# ThinkRail Launcher Lite 项目约定

- 独立的 Tauri 2 / Vue 3 / Rust 桌面项目，文档使用中文。
- 只向 ThinkRail 子进程传入代理，不改变系统全局代理，不开启 TUN。
- 不自动退出或强制终止用户的 ThinkRail；已有实例时提示用户正常退出。
- 不读取 ThinkRail 的凭据、会话、Cookie 或账号数据库。
- 不通过 shell 拼接执行输入；保持窄范围 IPC 和路径、代理端点校验。
- 修改后运行 npm run lint、npm run build、cargo fmt、cargo clippy、cargo test。
- 不启动开发服务器。平台验证与真实客户端对话验证必须分别记录。
- 不自动推送或发布；发布需要用户明确授权。
- 用户于 2026-11-11 要求与 `../antigravity-launcher-lite` 配套发布：以后要求发布任一项目时，默认同时准备两个项目，统一版本号、分别构建和校验，两个项目均通过后再同批次公开；不因普通代码修改自行发布。具体流程见 `doc/release-policy.md`。
