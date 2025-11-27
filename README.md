# 📧 Email Validation API

不发送邮件，验证邮箱地址是否能够正常接收邮件的服务。

## 核心功能

- **语法验证**: 检查邮箱格式是否符合 RFC 5322 标准
- **DNS验证**: 检查域名是否存在，是否配置了MX记录
- **SMTP验证**: 连接邮件服务器验证收件人是否存在（不发送邮件）
- **深度分析**: 检测一次性邮箱、角色账户、免费邮箱提供商等

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 使用

### 快速验证 (GET)

```bash
curl http://localhost:8000/api/v1/check/user@example.com
```

响应:
```json
{
    "email": "user@example.com",
    "valid": true,
    "score": 85,
    "risk": "low"
}
```

### 完整验证 (POST)

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "level": "full"}'
```

### 批量验证

```bash
curl -X POST http://localhost:8000/api/v1/validate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["user1@gmail.com", "user2@test.com"],
    "level": "full"
  }'
```

## 验证级别

| 级别 | 说明 | 耗时 |
|------|------|------|
| `syntax` | 仅语法验证 | <10ms |
| `dns` | 语法+DNS验证 | ~500ms |
| `smtp` | 语法+DNS+SMTP验证 | ~2s |
| `full` | 完整验证（推荐） | ~2s |

## 风险等级

| 等级 | 说明 | 评分范围 |
|------|------|----------|
| `low` | 低风险，邮箱有效 | 80-100 |
| `medium` | 中等风险，可能有效 | 60-79 |
| `high` | 高风险，可能无效 | 40-59 |
| `invalid` | 邮箱无效 | 0-39 |

## 验证结果说明

```json
{
    "email": "user@gmail.com",
    "valid": true,
    "risk_level": "low",
    "score": 90,
    "syntax": {
        "valid": true,
        "local_part": "user",
        "domain": "gmail.com"
    },
    "dns": {
        "has_mx": true,
        "mx_records": ["alt1.gmail-smtp-in.l.google.com", ...]
    },
    "smtp": {
        "connectable": true,
        "accepts_mail": true,
        "is_catch_all": false
    },
    "deep_analysis": {
        "is_disposable": false,
        "is_role_account": false,
        "is_free_provider": true,
        "provider_name": "Gmail"
    },
    "validation_time_ms": 1523,
    "message": "邮箱验证通过，可信度高"
}
```

## 检测能力

### 一次性邮箱检测

自动识别以下类型的临时邮箱:
- 10 Minute Mail
- Mailinator
- Guerrilla Mail
- Temp Mail
- 更多...

### 角色账户检测

识别通用角色账户:
- admin, info, support
- noreply, webmaster
- sales, hr, legal
- 更多...

### 邮箱提供商识别

支持识别:
- Gmail, Outlook, Yahoo
- QQ邮箱, 163邮箱, 126邮箱
- 阿里云邮箱, Foxmail
- 更多...

## 运行测试

```bash
pytest tests/ -v
```

## 项目结构

```
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI入口
│   ├── api/
│   │   └── routes.py     # API路由
│   ├── core/
│   │   ├── validator.py  # 核心验证引擎
│   │   ├── syntax.py     # 语法验证
│   │   ├── dns.py        # DNS验证
│   │   ├── smtp.py       # SMTP验证
│   │   └── disposable.py # 一次性邮箱检测
│   └── models/
│       └── schemas.py    # 数据模型
├── tests/
│   └── test_validator.py
├── requirements.txt
└── README.md
```

## 技术栈

- **FastAPI**: 现代高性能Python API框架
- **dnspython**: DNS查询
- **aiosmtplib**: 异步SMTP验证
- **Pydantic**: 数据校验

## 注意事项

1. SMTP验证可能被某些邮件服务器限制或阻止
2. 建议在生产环境配置适当的请求频率限制
3. Catch-all服务器可能导致验证结果不准确

## License

MIT
