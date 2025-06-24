# Phone Carrier Detector MCP Server

一个用于检测中国手机号码运营商的MCP (Model Context Protocol) 服务器。

## 功能特性

- 🔍 **运营商检测**: 支持中国三大运营商（中国移动、中国联通、中国电信）的号码识别
- 📱 **虚拟运营商**: 支持虚拟运营商号码识别
- 🚀 **批量处理**: 支持批量检测多个手机号码
- 📊 **详细信息**: 提供运营商、号码类型、前缀等详细信息
- 🎯 **高精度**: 基于最新的中国运营商号码段数据库

## 支持的运营商

| 运营商 | 主要号段 |
|--------|----------|
| 中国移动 | 130-139, 145, 147, 150-159, 166-178, 180-189, 198-199 |
| 中国联通 | 130-132, 145-146, 155-156, 166-167, 175-176, 185-186 |
| 中国电信 | 133, 149, 153, 173, 177, 180-181, 189, 199 |
| 虚拟运营商 | 170-178 |

## 安装

### 方法1: 通过npm安装

```bash
npm install phone-carrier-detector
```

### 方法2: 从源码安装

```bash
git clone https://github.com/dahuangbaojian/sms-mcp-server.git
cd sms-mcp-server
pip install -r requirements.txt
```

## 使用方法

### 在MCP客户端中使用

1. 配置MCP客户端（如Claude Desktop）:

```json
{
  "mcpServers": {
    "phone-carrier-detector": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {}
    }
  }
}
```

2. 重启客户端，然后就可以使用以下工具：

#### 单个号码检测

```
请帮我检测手机号码 13812345678 的运营商信息
```

#### 批量号码检测

```
请帮我批量检测这些号码的运营商：13812345678, 18612345678, 13312345678
```

## API 工具

### 1. detect_carrier

检测单个手机号码的运营商信息。

**参数:**
- `phone_number` (string): 要检测的手机号码

**示例输出:**
```
📱 手机号码运营商检测结果

📞 号码：13812345678
🏢 运营商：China Mobile
📋 号码类型：GSM
🔢 前缀：138
✅ 状态：有效号码

---
*数据来源：中国三大运营商号码段数据库*
```

### 2. batch_detect_carriers

批量检测多个手机号码的运营商信息。

**参数:**
- `phone_numbers` (array): 要检测的手机号码列表

## 开发

### 运行测试

```bash
python -m pytest tests/
```

### 代码格式化

```bash
black .
flake8 .
```

### 本地测试

```bash
python mcp_server.py
```

## 技术栈

- **Python 3.8+**
- **MCP Protocol 1.0**
- **正则表达式** - 号码格式验证
- **JSON Schema** - 工具参数验证

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持中国三大运营商检测
- 支持虚拟运营商检测
- 支持批量号码检测
- 提供详细的号码类型信息

## 支持

如果你遇到任何问题或有建议，请：

1. 查看 [Issues](https://github.com/dahuangbaojian/sms-mcp-server/issues)
2. 创建新的 Issue
3. 发送邮件到 support@example.com

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
