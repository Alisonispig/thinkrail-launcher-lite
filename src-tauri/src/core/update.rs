use super::{Result, error, proxy::ProxyInput};
use serde::Serialize;
use std::time::Duration;
use tauri::ipc::Channel;
use tauri_plugin_updater::{Update, UpdaterExt};
use tokio::sync::Mutex;

#[derive(Default)]
pub struct PendingUpdate(pub Mutex<Option<Update>>);

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct UpdateInfo {
    version: String,
    notes: String,
}

#[derive(Clone, Serialize)]
#[serde(tag = "event", rename_all = "camelCase")]
pub enum Progress {
    Downloading { downloaded: u64, total: Option<u64> },
    Installing,
}

// 下载地址来自固定的 GitHub 更新清单；IPC 不接受 URL、文件路径或安装参数。
fn validate_download(url: &tauri::Url) -> Result<()> {
    if url.scheme() != "https"
        || url.host_str() != Some("github.com")
        || !url.username().is_empty()
        || url.password().is_some()
        || url.port_or_known_default() != Some(443)
        || url.query().is_some()
        || url.fragment().is_some()
        || !url
            .path()
            .starts_with("/Alisonispig/thinkrail-launcher-lite/releases/download/")
    {
        return Err(error("UPDATE_INVALID", "update"));
    }
    Ok(())
}

fn update_error(value: tauri_plugin_updater::Error) -> super::AppError {
    use tauri_plugin_updater::Error;
    let code = match value {
        Error::ReleaseNotFound => "UPDATE_UNAVAILABLE",
        Error::TargetNotFound(_) | Error::TargetsNotFound(_) => "UPDATE_PLATFORM_MISSING",
        Error::Minisign(_)
        | Error::Base64(_)
        | Error::SignatureUtf8(_)
        | Error::SignedVersionMismatch { .. }
        | Error::MissingSignedVersion => "UPDATE_SIGNATURE_FAILED",
        Error::Reqwest(_) => "UPDATE_NETWORK_FAILED",
        _ => "UPDATE_FAILED",
    };
    error(code, "update")
}

fn stable_only(
    builder: tauri_plugin_updater::UpdaterBuilder,
) -> tauri_plugin_updater::UpdaterBuilder {
    builder.version_comparator(|current, release| {
        release.version > current && release.version.pre.is_empty()
    })
}

pub async fn check(
    app: &tauri::AppHandle,
    pending: &PendingUpdate,
    proxy: Option<ProxyInput>,
) -> Result<Option<UpdateInfo>> {
    let mut stored = pending.0.lock().await;
    *stored = None;
    let mut builder = app.updater_builder().timeout(Duration::from_secs(30));
    builder = match proxy {
        Some(proxy) => builder.proxy(
            proxy
                .url()?
                .parse()
                .map_err(|_| error("INVALID_PROXY", "input"))?,
        ),
        None => builder.no_proxy(),
    };
    // 只接受比当前版本新的正式版本，不允许降级或预发布版本。
    let update = stable_only(builder)
        .build()
        .map_err(update_error)?
        .check()
        .await
        .map_err(update_error)?;
    let Some(mut update) = update else {
        return Ok(None);
    };
    validate_download(&update.download_url)?;
    // 大型安装包允许更长超时；网络选择沿用此次检查结果。
    update.timeout = Some(Duration::from_secs(600));
    let info = UpdateInfo {
        version: update.version.clone(),
        notes: update
            .body
            .clone()
            .unwrap_or_default()
            .chars()
            .take(4000)
            .collect(),
    };
    *stored = Some(update);
    Ok(Some(info))
}

pub async fn install(
    app: tauri::AppHandle,
    pending: &PendingUpdate,
    progress: Channel<Progress>,
) -> Result<()> {
    let update = pending
        .0
        .lock()
        .await
        .clone()
        .ok_or_else(|| error("UPDATE_CHECK_REQUIRED", "update"))?;
    validate_download(&update.download_url)?;
    let mut downloaded = 0u64;
    let bytes = update
        .download(
            |chunk, total| {
                downloaded = downloaded.saturating_add(chunk as u64);
                let _ = progress.send(Progress::Downloading { downloaded, total });
            },
            || {},
        )
        .await
        .map_err(update_error)?;
    // download 与 install 均由官方插件验证签名；验证通过之前不替换应用。
    let _ = progress.send(Progress::Installing);
    tauri::async_runtime::spawn_blocking(move || update.install(bytes))
        .await
        .map_err(|_| error("UPDATE_FAILED", "update"))?
        .map_err(update_error)?;
    // 仅重启本启动器，不退出或重启 ThinkRail。
    app.restart();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signed_package_is_bound_to_payload_and_version() {
        let mut context = tauri::test::mock_context(tauri::test::noop_assets());
        context.config_mut().plugins.0.insert(
            "updater".into(),
            serde_json::json!({
                "pubkey": include_str!("../../test-fixtures/update-test.pub").trim(),
                "requireSignedVersion": true
            }),
        );
        let app = tauri::test::mock_builder()
            .plugin(
                tauri_plugin_updater::Builder::new()
                    .pubkey(include_str!("../../test-fixtures/update-test.pub").trim())
                    .build(),
            )
            .build(context)
            .unwrap();
        let updater = stable_only(app.updater_builder())
            .target("test-target")
            .executable_path("/Applications/Test.app/Contents/MacOS/Test")
            .endpoints(vec!["https://github.com/Alisonispig/thinkrail-launcher-lite/releases/latest/download/latest.json".parse().unwrap()]).unwrap()
            .build().unwrap();
        let mut manifest = serde_json::json!({
            "version": "2.0.0",
            "platforms": {"test-target": {
                "url": "https://github.com/Alisonispig/thinkrail-launcher-lite/releases/download/v2.0.0/test.tar.gz",
                "signature": include_str!("../../test-fixtures/update-payload.sig").trim()
            }}
        });
        let payload = include_bytes!("../../test-fixtures/update-payload.txt");
        let update = updater.restore_update(manifest.clone()).unwrap().unwrap();
        update.verify(payload).unwrap();
        assert!(update.verify(b"tampered payload").is_err());
        // 清单被篡改为更高版本，也不能重放旧版本的有效签名包。
        manifest["version"] = serde_json::json!("3.0.0");
        let mismatch = updater.restore_update(manifest.clone()).unwrap().unwrap();
        assert!(matches!(
            mismatch.verify(payload),
            Err(tauri_plugin_updater::Error::SignedVersionMismatch { .. })
        ));
        manifest["version"] = serde_json::json!("99.0.0-beta.1");
        assert!(updater.restore_update(manifest.clone()).unwrap().is_none());
        manifest["version"] = serde_json::json!("0.0.0");
        assert!(updater.restore_update(manifest).unwrap().is_none());
    }

    #[test]
    fn download_is_limited_to_this_repository() {
        assert!(validate_download(&"https://github.com/Alisonispig/thinkrail-launcher-lite/releases/download/v0.1.1/app.tar.gz".parse().unwrap()).is_ok());
        for url in [
            "http://github.com/Alisonispig/thinkrail-launcher-lite/releases/download/v1/app",
            "https://github.com/other/repo/releases/download/v1/app",
            "https://github.com.evil.test/Alisonispig/thinkrail-launcher-lite/releases/download/v1/app",
            "https://user@github.com/Alisonispig/thinkrail-launcher-lite/releases/download/v1/app",
            "https://github.com:8443/Alisonispig/thinkrail-launcher-lite/releases/download/v1/app",
            "https://github.com/Alisonispig/thinkrail-launcher-lite/releases/download/v1/app?url=evil",
            "file:///tmp/update.app",
        ] {
            assert!(validate_download(&url.parse().unwrap()).is_err(), "{url}");
        }
    }
}
