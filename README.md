# tool-release-forge

> **语义化版本发版、更新日志提炼与制品签名打包锻造炉**  
> Universal CLI Facade (UCFS v1.0) 标准实现 | 100% 离线自省 | Conventional Commits 语义分类与 SHA-256 校验和

---

## 🌟 核心价值与实用性痛点解答

在将项目推向生产发布与开源交付时，传统的 GitHub Release 操作繁琐且容易出错：
1. **更新日志编写繁琐**：人工去翻查数百次提交，手动整理变更点，容易遗漏重大突破性变更（Breaking Changes）或贡献者致谢。
2. **多平台发布包打包混乱**：需要手动用外部工具打包 zip 和 tar.gz，文件名规范不一，容易包含 `.git` 或缓存垃圾文件。
3. **缺少防篡改校验和**：很多项目未提供 `SHA256SUMS`，下游用户或包管理器无法校验下载文件的完整性与真实性。

`tool-release-forge` 将发布闭环浓缩为单一确定性操作：
- **Conventional Commits 自动提取分类**：精准解析 `feat:`, `fix:`, `perf:`, `docs:`, `refactor:`，按优先级生成专业 Markdown 发版日志。
- **纯标准库双格式归档**：自动剔除隐藏目录并生成标准 `.tar.gz` 与 `.zip`。
- **密码学 SHA-256 校验和生成**：自动计算每一个分发包的 SHA-256 哈希值，输出规范 `SHA256SUMS` 文件。
- **GitHub CLI 协同规划**：生成一键发布的 `gh release create` 命令行指令，或在配置完成后自动发布。

---

## ⚡ 极速开始 (Quick Start in 3 Seconds)

```bash
# 1. 环境校验
python main.py setup

# 2. 对当前项目锻造发布包 (生成 dist/ 归档、更新日志与 SHA256SUMS)
python main.py run

# 3. 运行离线单元测试
python main.py test

# 4. 核心健康自检
python main.py health

# 5. 清理缓存与 dist/
python main.py clean
```

### 高级功能：完整发版锻造与直接发布
```bash
# 为指定项目锻造 v1.0.0 发布包（指定提交范围从 v0.9.0 到 HEAD）
python main.py forge --target D:\github\my-project --tag v1.0.0 --from-tag v0.9.0

# 仅提炼更新日志并输出到终端或文件
python main.py notes --target D:\github\my-project --tag v1.0.0 --out RELEASE_NOTES.md
```

---

## 🛡️ 架构与不变式

- **独立职责**：专注发布日志生成、产物打包与 SHA256 校验，不干预业务构建或修改源码。
- **离线确定性**：日志提炼与归档打包完全离线，不强依赖 GitHub 网络。

---

## 🚫 Non-Goals (明确非目标)

1. **不替代编译器**：本工具不编译 C/Rust 二进制（编译由项目构建系统或 CI 完成），本工具负责将构建出的文件打包归档。
2. **不强制自动推送 Git Tag**：Tag 必须由用户或 CI 显式创建，本工具不会隐式篡改 Git 标签。
3. **不越权修改源码**：除在 `dist/` 下生成发布包外，绝不修改用户源码。
