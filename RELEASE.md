# CoPilotX 自动打包发布指南

本文档说明如何使用 GitHub Actions 自动构建和发布 CoPilotX。

---

## 📋 目录

- [概述](#概述)
- [触发方式](#触发方式)
- [构建流程](#构建流程)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 概述

CoPilotX 使用 GitHub Actions 实现自动化构建和发布，支持：

- ✅ **多平台构建**：macOS、Windows、Linux
- ✅ **多架构支持**：x64、arm64
- ✅ **自动发布**：GitHub Releases
- ✅ **CDN 分发**：阿里云 OSS（可选）

---

## 触发方式

### 方式 1：推送 Tag（推荐）

```bash
# 创建 tag
git tag v0.1.21

# 推送 tag（自动触发构建）
git push origin v0.1.21
```

**版本号规则：**

| 格式 | 示例 | 说明 |
|------|------|------|
| 正式版 | `v1.0.0` | 稳定发布版本 |
| Alpha | `v1.0.0-alpha.1` | 内部测试版本 |
| Beta | `v1.0.0-beta.1` | 公开测试版本 |

---

### 方式 2：手动触发

#### 通过 GitHub 网页界面

1. 打开仓库：https://github.com/w5240/CoPilotX
2. 点击 **Actions** 标签
3. 在左侧选择 **Release** workflow
4. 点击右侧 **Run workflow** 按钮
5. 输入版本号（如 `0.1.21`）
6. 点击绿色的 **Run workflow** 按钮

#### 通过 GitHub CLI

```bash
# 安装 GitHub CLI（如未安装）
brew install gh

# 认证
gh auth login

# 触发构建
gh workflow run release.yml -f version=0.1.21

# 查看构建状态
gh run list --workflow=release.yml
gh run watch
```

---

## 构建流程

### 完整流程图

```
触发构建
    ↓
┌─────────────────────────────────────┐
│  并行构建（3个平台同时进行）          │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌────────┐│
│  │ macOS   │ │ Windows │ │ Linux  ││
│  │ x64     │ │ x64     │ │ x64    ││
│  │ arm64   │ │ arm64   │ │ arm64  ││
│  └─────────┘ └─────────┘ └────────┘│
└─────────────────────────────────────┘
    ↓
上传构建产物到 GitHub Artifacts
    ↓
┌─────────────────────────────────────┐
│  发布到 GitHub Releases              │
│  - 创建 Release                      │
│  - 上传安装包                        │
│  - 生成发布说明                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  上传到阿里云 OSS（可选）             │
│  - 更新 latest/ 目录                 │
│  - 归档到 releases/vX.Y.Z/           │
│  - 生成 release-info.json            │
└─────────────────────────────────────┘
    ↓
构建完成 ✅
```

### 构建产物

| 平台 | 文件格式 | 架构 |
|------|---------|------|
| **macOS** | `.dmg`, `.zip` | x64, arm64 |
| **Windows** | `.exe` | x64, arm64 |
| **Linux** | `.AppImage`, `.deb`, `.rpm` | x64, arm64 |

### 构建时间

- **macOS**: ~10-15 分钟
- **Windows**: ~5-10 分钟
- **Linux**: ~5-10 分钟
- **总时间**: ~15-20 分钟（并行执行）

---

## 配置说明

### GitHub Secrets 配置

在 GitHub 仓库设置中配置：

**路径**：Settings → Secrets and variables → Actions → New repository secret

#### 必需的 Secrets

| Secret 名称 | 说明 | 是否必需 |
|------------|------|---------|
| `GITHUB_TOKEN` | GitHub 自动提供 | ✅ 自动 |

#### 可选的 Secrets（阿里云 OSS）

⚠️ **注意：OSS 上传默认已禁用。如需启用，请取消注释 `.github/workflows/release.yml` 中的 `upload-oss` job。**

| Secret 名称 | 说明 |
|------------|------|
| `OSS_ACCESS_KEY_ID` | 阿里云 AccessKey ID |
| `OSS_ACCESS_KEY_SECRET` | 阿里云 AccessKey Secret |

**启用 OSS 上传：**

1. 配置 GitHub Secrets：
   - `OSS_ACCESS_KEY_ID`: 阿里云 AccessKey ID
   - `OSS_ACCESS_KEY_SECRET`: 阿里云 AccessKey Secret

2. 取消注释 `.github/workflows/release.yml` 中的 `upload-oss` job（约 214-400 行）

3. 更新 `finalize` job 的依赖：
   ```yaml
   finalize:
     needs: [publish, upload-oss]  # 添加 upload-oss
   ```

#### 可选的 Secrets（macOS 签名和公证）

⚠️ **注意：默认已禁用代码签名和公证。如需启用，请配置以下 Secrets 并修改 `.github/workflows/release.yml`。**

| Secret 名称 | 说明 | 费用 |
|------------|------|------|
| `MAC_CERTS` | macOS 开发者证书（base64 编码） | - |
| `MAC_CERTS_PASSWORD` | 证书密码 | - |
| `APPLE_ID` | Apple ID | - |
| `APPLE_APP_SPECIFIC_PASSWORD` | App 专用密码 | - |
| `APPLE_TEAM_ID` | Team ID | - |

**启用代码签名和公证：**

1. 申请 Apple Developer 账号（$99/年）
2. 在 GitHub Secrets 中配置上述变量
3. 修改 `.github/workflows/release.yml`，添加环境变量：
   ```yaml
   - name: Build macOS
     env:
       GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
       CSC_LINK: ${{ secrets.MAC_CERTS }}
       CSC_KEY_PASSWORD: ${{ secrets.MAC_CERTS_PASSWORD }}
       APPLE_ID: ${{ secrets.APPLE_ID }}
       APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
       APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
   ```
4. 修改 `electron-builder.yml`：
   ```yaml
   mac:
     notarize: true  # 启用公证
   ```

---

### 禁用阿里云 OSS 上传

**默认已禁用 OSS 上传。** 如需启用，请取消注释 `.github/workflows/release.yml` 中的 `upload-oss` job。

---

## 常见问题

### 1. 构建失败怎么办？

**检查步骤：**

1. 打开 Actions 页面查看错误日志
2. 检查是否有未提交的更改
3. 确认 `pnpm-lock.yaml` 是否最新
4. 查看具体的错误信息

**常见错误：**

| 错误 | 解决方案 |
|------|---------|
| 依赖安装失败 | 删除 `node_modules`，重新 `pnpm install` |
| 构建超时 | 检查网络连接，或重试构建 |
| 权限错误 | 检查 GitHub Token 权限 |

---

### 2. 如何查看构建进度？

**网页界面：**
1. 打开 Actions 页面
2. 点击正在运行的 workflow
3. 查看实时日志

**命令行：**
```bash
gh run watch
```

---

### 3. 如何下载构建产物？

**方式 1：GitHub Releases**
- 构建完成后自动发布到 Releases 页面
- 地址：https://github.com/w5240/CoPilotX/releases

**方式 2：Actions Artifacts**
- 在 workflow 运行页面下载
- 保留 7 天

---

### 4. 如何回滚发布？

```bash
# 删除 GitHub Release
gh release delete v0.1.21

# 删除远程 tag
git push origin --delete v0.1.21

# 删除本地 tag
git tag -d v0.1.21
```

---

### 5. 如何修改发布说明？

编辑 `.github/workflows/release.yml` 中的 `body` 部分：

```yaml
body: |
  ## 🚀 CoPilotX ${{ github.ref_name }}
  
  CoPilotX - 你的个人 AI 助手
  
  ### 📦 下载
  
  #### macOS
  - **Apple Silicon**: `CoPilotX-*-mac-arm64.dmg`
  - **Intel**: `CoPilotX-*-mac-x64.dmg`
  
  #### Windows
  - **安装程序**: `CoPilotX-*-win-x64.exe`
```

---

### 6. 如何只构建特定平台？

修改 `.github/workflows/release.yml` 中的 `matrix`：

```yaml
strategy:
  matrix:
    include:
      - os: macos-latest
        platform: mac
      # 注释掉其他平台
      # - os: windows-latest
      #   platform: win
      # - os: ubuntu-latest
      #   platform: linux
```

---

## 📊 发布检查清单

发布前请确认：

- [ ] 代码已推送到 `main` 分支
- [ ] 版本号已更新（`package.json`）
- [ ] CHANGELOG 已更新
- [ ] 测试已通过
- [ ] 文档已更新

发布后请确认：

- [ ] GitHub Release 已创建
- [ ] 安装包可正常下载
- [ ] 应用可正常安装和运行
- [ ] 自动更新功能正常（如启用）

---

## 🔗 相关链接

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [electron-builder 文档](https://www.electron.build/)
- [GitHub CLI 文档](https://cli.github.com/manual/)

---

## 📝 示例：完整发布流程

### 正式版本发布

```bash
# 1. 更新版本号
pnpm version patch  # 或 minor, major

# 2. 推送代码和 tag
git push origin main
git push origin --tags

# 3. 等待构建完成（~15-20 分钟）

# 4. 验证发布
# 打开 https://github.com/w5240/CoPilotX/releases
```

### 测试版本发布

```bash
# 1. 创建测试 tag
git tag v0.1.21-beta.1

# 2. 推送 tag
git push origin v0.1.21-beta.1

# 3. 验证测试版本
# 打开 https://github.com/w5240/CoPilotX/releases
```

---

**最后更新：** 2026-03-02  
**维护者：** CoPilotX Team
