```
# 贡献指南

感谢您对ThinkCheck项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告问题
- 在GitHub Issues中创建新issue
- 详细描述问题和重现步骤
- 如果是bug报告，请包含环境信息

### 提交代码
1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 代码规范
- 使用Python 3.7+语法
- 遵循PEP 8编码规范
- 添加适当的类型注解
- 为公共API编写文档字符串
- 为新功能添加测试用例

### 开发环境设置
```

bash

# 克隆项目

git clone <https://github.com/yourusername/thinkcheck.git>

cd thinkcheck

# 安装开发依赖

pip install -e ".\[dev]"

# 运行测试

pytest

# 代码格式化

black thinkcheck/

```
## 项目结构
```

thinkcheck/

├── thinkcheck/ # 核心库代码

├── tests/ # 测试代码

├── examples/ # 使用示例

├── docs/ # 文档

└── ...

```
## 开发流程
1. 讨论功能提案
2. 编写测试用例
3. 实现功能
4. 运行测试和代码检查
5. 更新文档
6. 提交PR

## 联系方式
- GitHub Issues: 问题讨论
- GitHub Discussions: 功能讨论
- Email: contact@harmonic-theory.org
```

