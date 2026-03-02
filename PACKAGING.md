# CoPilotX 打包配置差异说明

本文档说明 CoPilotX 与源分支 ClawX 在 `electron-builder.yml` 配置上的差异及其影响。

---

## 📊 配置差异总览

| # | 差异项 | 源分支 (ClawX) | 本地 (CoPilotX) | 影响级别 |
|---|--------|---------------|----------------|---------|
| 1 | 应用标识 | ClawX | CoPilotX | 🔴 重要 |
| 2 | 打包目标 | dmg + zip | dmg + zip | ✅ 已修复 |
| 3 | macOS 公证 | 启用 | 禁用 | 🟡 中等 |
| 4 | 专属技能 | 无 | 新增 | ✅ 功能增强 |
| 5 | 图标格式 | icns/ico | png | 🟡 需优化 |

---

## 🔧 品牌重塑关键修改

### ⚠️ 重要：解决 exec 窗口问题

**问题原因：**
`package.json` 中的 `name` 字段未修改，导致 `app.getName()` 返回旧名称，Helper 路径查找失败，回退到 `process.execPath`，从而出现 exec 窗口。

**已修复：**
```json
// package.json
{
  "name": "copilotx"  // ✅ 已从 "clawx" 改为 "copilotx"
}
```

**影响：**
- ✅ **解决 exec 窗口问题**
- ✅ Helper 路径正确：`CoPilotX Helper.app`
- ✅ 应用名称统一

---

### 📋 需要修改的关键位置

#### 🔴 必须修改（影响功能）

| # | 文件 | 位置 | 当前值 | 修改为 | 状态 |
|---|------|------|--------|--------|------|
| 1 | `package.json` | `name` | ~~clawx~~ | copilotx | ✅ 已修复 |

#### 🟡 建议修改（保持一致性）

| # | 文件 | 位置 | 当前值 | 建议修改 | 影响 |
|---|------|------|--------|---------|------|
| 2 | `electron/utils/config.ts` | `CLAWX_CONFIG` | `~/.clawx` | `~/.copilotx` | 配置目录 |
| 3 | `electron/utils/paths.ts` | `getClawXConfigDir()` | `~/.clawx` | `~/.copilotx` | 配置目录 |
| 4 | `electron/utils/logger.ts` | 日志文件名 | `clawx-*.log` | `copilotx-*.log` | 日志文件 |
| 5 | `electron/utils/store.ts` | 随机 ID | `clawx-*` | `copilotx-*` | 存储 ID |
| 6 | `electron/utils/secure-storage.ts` | 存储名称 | `clawx-providers` | `copilotx-providers` | 安全存储 |
| 7 | `src/stores/settings.ts` | 存储名称 | `clawx-settings` | `copilotx-settings` | 设置存储 |
| 8 | `src/stores/chat.ts` | 缓存键 | `clawx:image-cache` | `copilotx:image-cache` | 图片缓存 |
| 9 | `electron/gateway/manager.ts` | 设备身份文件 | `clawx-device-identity.json` | `copilotx-device-identity.json` | 设备身份 |

#### 🟢 可选修改（不影响功能）

| # | 文件 | 说明 |
|---|------|------|
| 10 | `electron/utils/provider-registry.ts` | OpenRouter headers 中的 `X-Title: ClawX` |
| 11 | `electron/utils/openrouter-headers-preload.cjs` | OpenRouter headers |
| 12 | `electron/utils/openclaw-cli.ts` | 环境变量 `OPENCLAW_EMBEDDED_IN: 'ClawX'` |
| 13 | 代码注释和日志 | 注释和日志中的 `ClawX` |

---

### 💡 修改方案

#### 方案 1：完全重命名（推荐）

**优点：**
- ✅ 品牌完全统一
- ✅ 避免混淆

**缺点：**
- ⚠️ 用户需要迁移数据（`~/.clawx` → `~/.copilotx`）

**需要修改：**
- 所有上述文件（1-9）

#### 方案 2：保持兼容（保守）

**优点：**
- ✅ 用户无需迁移数据
- ✅ 保持与旧版本兼容

**缺点：**
- ⚠️ 品牌不完全统一

**只需修改：**
- ✅ `package.json`（已修复，解决 exec 窗口问题）

---

## 🔴 重要差异

### 1. 应用标识变更（品牌重塑）

**变更内容：**
```yaml
# 源分支
appId: app.clawx.desktop
productName: ClawX
copyright: Copyright © 2026 ClawX

# 本地
appId: app.copilotx.desktop
productName: CoPilotX
copyright: Copyright © 2026 CoPilotX
```

**影响：**
- ✅ **正面**：品牌重塑，应用名称更新为 CoPilotX
- ⚠️ **负面**：
  - 已安装的 ClawX 用户需要卸载后重新安装
  - 自动更新可能失效（appId 改变）
  - 用户数据可能需要迁移

**建议：**
- 在发布说明中明确告知用户
- 提供迁移指南
- 考虑数据迁移脚本

---

### 2. 打包目标变更（已修复）

**变更内容：**
```yaml
# 源分支
target:
  - target: dmg    # DMG 安装镜像
    arch:
      - x64
      - arm64
  - target: zip    # ZIP 压缩包
    arch:
      - x64
      - arm64

# 本地（已修复）
target:
  - target: dmg    # ✅ 已恢复
    arch:
      - x64
      - arm64
  - target: zip
    arch:
      - x64
      - arm64
```

**影响：**
- ✅ **已修复**：现在会生成 DMG 和 ZIP 两种格式
- ✅ 用户体验更好（DMG 是 macOS 标准分发格式）

**打包结果：**
```
release/
├── CoPilotX-0.1.20-beta.0-mac-x64.dmg      # Intel Mac 安装镜像
├── CoPilotX-0.1.20-beta.0-mac-arm64.dmg    # Apple Silicon 安装镜像
├── CoPilotX-0.1.20-beta.0-mac-x64.zip      # Intel Mac 压缩包
└── CoPilotX-0.1.20-beta.0-mac-arm64.zip    # Apple Silicon 压缩包
```

---

## 🟡 次要差异

### 3. macOS 公证禁用

**变更内容：**
```yaml
# 源分支
notarize: true

# 本地
notarize: false  # 是否需要公证，$99每年
```

**影响：**
- ✅ **正面**：
  - 打包速度更快（无需等待 Apple 审核）
  - 无需 Apple Developer 账号（$99/年）
  - 无需配置公证环境变量

- ⚠️ **负面**：
  - 用户首次打开会看到"无法验证开发者"警告
  - 需要用户右键 → 打开 → 仍要打开
  - 不适合正式发布

**建议：**
- **开发/测试**：保持 `notarize: false`
- **正式发布**：启用 `notarize: true` 并配置 Apple Developer 证书

**如何启用公证：**
1. 申请 Apple Developer 账号（$99/年）
2. 配置环境变量：
   ```bash
   export APPLE_ID="your-apple-id@email.com"
   export APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
   export APPLE_TEAM_ID="XXXXXXXXXX"
   ```
3. 修改配置：
   ```yaml
   notarize: true
   ```

---

### 4. 专属技能打包（新增功能）

**新增内容：**
```yaml
extraResources:
  # Bundled skills (private/custom skills packaged with the app)
  - from: resources/bundled-skills/
    to: bundled-skills/
```

**影响：**
- ✅ **正面**：
  - 可以打包私有技能到应用中
  - 用户无需手动安装技能
  - 应用自包含，体验更好
  - 支持离线使用

- ⚠️ **负面**：
  - 应用体积增加（约几 MB）
  - 技能更新需要重新打包应用

**使用方法：**
1. 将技能放入 `resources/bundled-skills/` 目录
2. 添加 `.exclusive` 标记文件
3. 打包时自动包含

**目录结构：**
```
resources/bundled-skills/
├── tender-search/
│   ├── .exclusive
│   ├── SKILL.md
│   ├── _meta.json
│   └── tender_search.py
├── sysinfo/
│   ├── .exclusive
│   ├── SKILL.md
│   ├── _meta.json
│   └── sysinfo.py
└── quick-notes/
    ├── .exclusive
    ├── SKILL.md
    ├── _meta.json
    └── quick_notes.py
```

---

### 5. 图标格式变更

**变更内容：**
```yaml
# macOS
mac.icon: resources/icons/icon.icns → resources/icons/copilot-icon.png
dmg.icon: resources/icons/icon.icns → resources/icons/copilot-icon.png

# Windows
win.icon: resources/icons/icon.ico → resources/icons/copilot-icon.png
nsis.installerIcon: resources/icons/icon.ico → resources/icons/copilot-icon.png
nsis.uninstallerIcon: resources/icons/icon.ico → resources/icons/copilot-icon.png
```

**影响：**
- ⚠️ **潜在问题**：
  - macOS 推荐使用 `.icns` 格式（支持多种分辨率）
  - Windows 推荐使用 `.ico` 格式（支持多种分辨率）
  - PNG 可能导致图标显示模糊或异常

**建议：**
转换为正确的图标格式：

**macOS (.icns)：**
```bash
# 方法 1: 使用 sips
mkdir copilot-icon.iconset
sips -z 16 16     copilot-icon.png --out copilot-icon.iconset/icon_16x16.png
sips -z 32 32     copilot-icon.png --out copilot-icon.iconset/icon_16x16@2x.png
sips -z 32 32     copilot-icon.png --out copilot-icon.iconset/icon_32x32.png
sips -z 64 64     copilot-icon.png --out copilot-icon.iconset/icon_32x32@2x.png
sips -z 128 128   copilot-icon.png --out copilot-icon.iconset/icon_128x128.png
sips -z 256 256   copilot-icon.png --out copilot-icon.iconset/icon_128x128@2x.png
sips -z 256 256   copilot-icon.png --out copilot-icon.iconset/icon_256x256.png
sips -z 512 512   copilot-icon.png --out copilot-icon.iconset/icon_256x256@2x.png
sips -z 512 512   copilot-icon.png --out copilot-icon.iconset/icon_512x512.png
sips -z 1024 1024 copilot-icon.png --out copilot-icon.iconset/icon_512x512@2x.png
iconutil -c icns copilot-icon.iconset -o resources/icons/copilot-icon.icns

# 方法 2: 使用在线工具
# https://cloudconvert.com/png-to-icns
```

**Windows (.ico)：**
```bash
# 方法 1: 使用 ImageMagick
convert copilot-icon.png -define icon:auto-resize=256,128,64,48,32,16 copilot-icon.ico

# 方法 2: 使用在线工具
# https://cloudconvert.com/png-to-ico
```

**修改配置：**
```yaml
# macOS
mac:
  icon: resources/icons/copilot-icon.icns
dmg:
  icon: resources/icons/copilot-icon.icns

# Windows
win:
  icon: resources/icons/copilot-icon.ico
nsis:
  installerIcon: resources/icons/copilot-icon.ico
  uninstallerIcon: resources/icons/copilot-icon.ico
```

---

## 🚀 打包流程

### 准备工作

1. **下载 uv 二进制文件**（Python 包管理工具）：
   ```bash
   # 下载当前平台
   pnpm run uv:download

   # 下载所有平台（用于跨平台打包）
   pnpm run uv:download:all
   ```

2. **检查图标文件**：
   ```bash
   ls -la resources/icons/
   # 应该包含：copilot-icon.png, copilot-icon.icns, copilot-icon.ico
   ```

### 打包命令

```bash
# macOS（x64 + arm64）
pnpm package:mac

# Windows（需要 Windows 环境）
pnpm package:win

# Linux
pnpm package:linux

# 所有平台（需要 CI/CD）
pnpm release
```

### 打包结果

**macOS：**
```
release/
├── CoPilotX-0.1.20-beta.0-mac-x64.dmg      # Intel Mac 安装镜像
├── CoPilotX-0.1.20-beta.0-mac-arm64.dmg    # Apple Silicon 安装镜像
├── CoPilotX-0.1.20-beta.0-mac-x64.zip      # Intel Mac 压缩包
├── CoPilotX-0.1.20-beta.0-mac-arm64.zip    # Apple Silicon 压缩包
└── *.blockmap                               # 增量更新文件
```

**Windows：**
```
release/
├── CoPilotX-0.1.20-beta.0-win-x64.exe      # Windows 安装程序
├── CoPilotX-0.1.20-beta.0-win-arm64.exe    # Windows ARM 安装程序
└── *.blockmap                               # 增量更新文件
```

---

## 📝 注意事项

### 1. 用户迁移

由于 appId 改变，已安装 ClawX 的用户需要：
1. 卸载旧版本 ClawX
2. 安装新版本 CoPilotX
3. 重新配置设置和技能

### 2. 自动更新

appId 改变可能导致自动更新失效，建议：
- 在旧版本中提示用户手动下载新版本
- 提供迁移指南和说明文档

### 3. 安全警告

由于禁用公证，用户首次打开会看到安全警告：
- **解决方法**：右键点击应用 → 打开 → 仍要打开
- **正式发布**：启用公证，避免安全警告

### 4. 图标显示

使用 PNG 格式图标可能导致显示问题：
- **临时方案**：保持现状，观察实际效果
- **正式发布**：转换为 .icns 和 .ico 格式

---

## 🔗 相关文件

- [electron-builder.yml](./electron-builder.yml) - 打包配置文件
- [resources/bundled-skills/](./resources/bundled-skills/) - 专属技能目录
- [scripts/download-bundled-uv.mjs](./scripts/download-bundled-uv.mjs) - uv 下载脚本
- [.github/workflows/release.yml](./.github/workflows/release.yml) - CI/CD 发布流程

---

## 📚 参考文档

- [Electron Builder 配置文档](https://www.electron.build/configuration/configuration)
- [macOS 公证指南](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [图标格式转换](https://cloudconvert.com/)
- [uv 官方文档](https://docs.astral.sh/uv/)

---

**最后更新：** 2026-03-02  
**维护者：** CoPilotX Team
