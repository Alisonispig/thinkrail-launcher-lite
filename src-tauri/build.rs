fn main() {
    let mut attributes =
        tauri_build::Attributes::new().app_manifest(tauri_build::AppManifest::new().commands(&[
            "validate_app",
            "probe_proxy",
            "launch_thinkrail",
            "load_config",
            "save_config",
            "set_window_theme",
            "set_close_after_launch",
            "check_update",
            "install_update",
        ]));
    let windows_msvc = std::env::var("CARGO_CFG_TARGET_OS").as_deref() == Ok("windows")
        && std::env::var("CARGO_CFG_TARGET_ENV").as_deref() == Ok("msvc");
    if windows_msvc {
        attributes = attributes
            .windows_attributes(tauri_build::WindowsAttributes::new_without_app_manifest());
    }
    tauri_build::try_build(attributes).expect("构建 Tauri 权限清单失败");
    if windows_msvc {
        // Tauri 默认只给应用 exe 链接资源，lib 单元测试也需要 Common Controls v6。
        // 使用同一最小清单覆盖所有链接目标，不增加权限或修改系统配置。
        let manifest =
            std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("windows-app-manifest.xml");
        println!("cargo:rerun-if-changed={}", manifest.display());
        println!("cargo:rustc-link-arg=/MANIFEST:EMBED");
        println!("cargo:rustc-link-arg=/MANIFESTINPUT:{}", manifest.display());
    }
}
