# 图标设计

日期：2026-11-11。

应用图标使用内置 imagegen 工具重新生成：双轨汇入向上箭头，青蓝至紫色渐变，浅色圆角底板。源图位于 `src/assets/app-icon.png`，通过 Tauri CLI 导出 `src-tauri/icons/` 中的桌面平台 PNG、ICO 和 ICNS。

菜单栏使用同一造型的简化单色矢量图 `src/assets/tray-template.svg`，导出 32 像素的 `src-tauri/icons/tray-template.png` 和 64 像素的 `src/assets/tray-template-source.png`。非 macOS 托盘使用彩色的 `src-tauri/icons/tray.png`。

重新导出桌面图标：

```sh
npm run tauri icon -- src/assets/app-icon.png -o src-tauri/icons
```

该命令还会生成移动端目录；本项目只保留桌面资源。

## 生成提示词

```text
Use case: logo-brand
Asset type: production desktop application icon for ThinkRail Launcher Lite, a small independent process proxy launcher.
Primary request: a new polished minimal app icon, with an abstract railway / two parallel rails flowing upward and converging into one clear forward-upward launch arrow. One distinctive simple symbol, legible at 32px.
Style/medium: precision geometric vector-like rendering, smooth perfectly clean edges, restrained soft gradients.
Color palette: cyan and electric blue on the main rails, a subtle violet accent, on a softly off-white rounded-square app tile.
Composition/framing: square 1024x1024 canvas, centered rounded-square tile occupying 82% of canvas with uniform transparent outside margins; central mark occupying about 60% of tile. Front-facing flat app icon, no perspective.
Constraints: transparent outside the tile, opaque off-white tile, no text, no letters, no border, no grain or speckling, no mockup, no extra objects, no watermark. Clean professional utility app identity.
```
