# 贡献指南

感谢您对 ThinkCheck 项目的关注！我们欢迎任何形式的贡献，包括问题反馈、代码提交、文档改进和功能建议。

## 如何贡献

### 报告问题

- 在 GitHub Issues 中创建新 issue。
- 详细描述问题现象、复现步骤和期望行为。
- 如果是 bug 报告，请包含 Python 版本、操作系统和相关依赖版本。

### 提交代码

1. Fork 本项目到您的账号。
2. 基于 `main` 分支创建特性分支：`git checkout -b feature/AmazingFeature`。
3. 提交更改：`git commit -m 'Add some AmazingFeature'`。
4. 推送到您的 fork：`git push origin feature/AmazingFeature`。
5. 在原始仓库创建 Pull Request，并说明改动内容和动机。

### 代码规范

- 使用 Python 3.7+ 语法。
- 遵循 PEP 8 编码规范。
- 为公共 API 添加类型注解和文档字符串。
- 为新功能或 bug 修复补充测试用例。
- 提交前确保测试通过：`pytest`。

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/luoxuejian000/-thinkcheck-lib-.git
cd -thinkcheck-lib-

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black thinkcheck/
```

## 项目结构

```
thinkcheck/
├── thinkcheck/    # 核心库代码
├── tests/         # 测试代码
├── examples/      # 使用示例
├── docs/          # 文档
└── ...
```

## 开发流程

1. 在 issue 或 discussion 中讨论功能提案。
2. 编写测试用例。
3. 实现功能或修复 bug。
4. 运行测试和代码检查。
5. 更新相关文档和变更日志。
6. 提交 PR 并等待 review。

## 联系方式

- GitHub Issues: 问题讨论
- GitHub Discussions: 功能讨论
- Email: contact@harmonic-theory.org
