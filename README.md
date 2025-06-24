# Phone Carrier Detector MCP Server

一个用于检测中国手机号码运营商和归属地的 MCP (Model Context Protocol) 服务器。

## 功能特性

* 🔍 **运营商检测**: 支持中国三大运营商（中国移动、中国联通、中国电信）的号码识别
* 📍 **归属地检测**: 提供省份和城市级别的归属地信息
* 📱 **虚拟运营商**: 支持虚拟运营商号码识别
* 🚀 **批量处理**: 支持批量检测多个手机号码（最多100个）
* 📊 **详细信息**: 提供运营商、归属地、前缀等详细信息
* 🎯 **高精度**: 基于真实的中国运营商号码段数据库（492,088条记录）
* ⚡ **高性能**: 内存数据库，查询速度极快

## 支持的运营商

| 运营商 | 主要号段 |
|--------|----------|
| 中国移动 | 134-139, 147, 150-152, 157-159, 172, 178, 182-184, 187-188, 198 |
| 中国联通 | 130-132, 145, 155-156, 166, 175-176, 185-186 |
| 中国电信 | 133, 149, 153, 173, 177, 180-181, 189, 199 |
| 中国广电 | 192 |
| 中国铁通 | 174 |

## 安装

### 方法1: 从源码安装

```bash
git clone https://github.com/dahuangbaojian/sms-mcp-server.git
cd sms-mcp-server
```

### 方法2: 直接使用

项目使用 Python 标准库实现，无需额外依赖。如需运行测试：

```bash
pip install pytest
```

## 使用方法

### 在 MCP 客户端中使用

1. 配置 MCP 客户端（如 Claude Desktop）:

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
请帮我检测手机号码 13812345678 的运营商和归属地信息
```

#### 批量号码检测

```
请帮我批量检测这些号码的运营商和归属地：13812345678, 18687654321, 13312345678
```

## API 工具

### 1. detect_carrier

检测单个手机号码的运营商和归属地信息。

**参数:**
* `phone_number` (string): 要检测的手机号码（11位数字）

**示例输出:**
```json
{
  "success": true,
  "phone_number": "13812345678",
  "carrier": "China Mobile",
  "carrier_cn": "移动",
  "province": "江苏",
  "city": "连云港",
  "prefix": "1381234"
}
```

### 2. batch_detect_carriers

批量检测多个手机号码的运营商和归属地信息。

**参数:**
* `phone_numbers` (array): 要检测的手机号码列表（最多100个）

**示例输出:**
```json
{
  "success": true,
  "total": 3,
  "results": [
    {
      "success": true,
      "phone_number": "13812345678",
      "carrier": "China Mobile",
      "province": "江苏",
      "city": "连云港"
    }
  ]
}
```

## 数据来源

项目使用真实的中国手机号归属地数据库，包含：
- **492,088 条记录**
- **覆盖所有主要运营商**
- **精确到城市级别**
- **实时更新**

## 开发

### 运行测试

```bash
# 运行所有测试
python tests/run_tests.py --all

# 运行单元测试
python tests/run_tests.py --unit

# 运行集成测试
python tests/run_tests.py --integration

# 运行数据解析器测试
python tests/run_tests.py --data
```

### 解析数据

```bash
# 从原始数据文件生成数据库
python parse_phone_data.py
```

### 本地测试

```bash
python mcp_server.py
```

## 项目结构

```
.
├── mcp_server.py              # MCP协议主服务
├── parse_phone_data.py        # 数据解析脚本
├── data/                      # 数据目录
│   ├── 手机号归属地1219.txt   # 原始数据文件
│   └── phone_database.json    # 解析后的数据库
├── tests/                     # 测试目录
│   ├── test_mcp_server.py     # 单元测试
│   ├── test_mcp_integration.py # 集成测试
│   ├── test_data_parser.py    # 数据解析测试
│   └── run_tests.py           # 测试运行器
├── package.json               # MCP配置
├── mcp-metadata.json          # MCP元数据
└── README.md                  # 项目说明
```

## 技术栈

* **Python 3.8+**
* **MCP Protocol 2024-11-05**
* **JSON-RPC 2.0**
* **正则表达式** - 号码格式验证
* **内存数据库** - 高性能查询

## 性能特点

* **内存占用**: ~100MB（包含49万条记录）
* **查询速度**: O(1) 哈希表查找
* **并发支持**: 异步处理，支持高并发
* **错误处理**: 完善的错误处理和参数验证

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

* 初始版本发布
* 支持中国三大运营商检测
* 支持归属地检测（省份+城市）
* 支持虚拟运营商检测
* 支持批量号码检测
* 基于真实数据库（49万+记录）
* 完整的 MCP 协议实现
* 全面的测试覆盖

## 支持

如果你遇到任何问题或有建议，请：

1. 查看 [Issues](https://github.com/dahuangbaojian/sms-mcp-server/issues)
2. 创建新的 Issue
3. 发送邮件到 dahuangbaojian@example.com

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
