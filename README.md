# SMS MCP Server

一个简单的短信SMS MCP服务器，提供手机运营商检测功能。

## 功能特性

- 手机号码运营商检测
- RESTful API接口
- 支持中国三大运营商（移动、联通、电信）的号码识别

## 安装

1. 克隆仓库：
```bash
git clone [repository-url]
cd sms-mcp-server
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行服务器

```bash
python main.py
```

服务器将在 http://localhost:8000 启动

## API 使用

### 检测运营商

**请求：**
```bash
curl -X POST "http://localhost:8000/detect-carrier" \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "13812345678"}'
```

**响应：**
```json
{
    "phone_number": "13812345678",
    "carrier": "China Mobile"
}
```

## API 文档

访问 http://localhost:8000/docs 查看完整的API文档。
