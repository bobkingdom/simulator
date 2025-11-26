"""
邮箱验证API服务
FastAPI 入口文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app import __version__


# 创建FastAPI应用
app = FastAPI(
    title="邮箱验证API",
    description="""
## 📧 Email Validation API

不发送邮件，验证邮箱地址是否能够正常接收邮件的服务。

### 核心功能

- **语法验证**: 检查邮箱格式是否符合 RFC 5322 标准
- **DNS验证**: 检查域名是否存在，是否配置了MX记录
- **SMTP验证**: 连接邮件服务器验证收件人是否存在（不发送邮件）
- **深度分析**: 检测一次性邮箱、角色账户等

### 验证级别

| 级别 | 说明 | 耗时 |
|------|------|------|
| syntax | 仅语法验证 | <10ms |
| dns | 语法+DNS验证 | ~500ms |
| smtp | 语法+DNS+SMTP验证 | ~2s |
| full | 完整验证 | ~2s |

### 风险等级

- **low**: 低风险，邮箱有效
- **medium**: 中等风险，可能有效
- **high**: 高风险，可能无效
- **invalid**: 邮箱无效

### 使用示例

```python
import httpx

# 单个验证
response = httpx.get("http://localhost:8000/api/v1/check/user@example.com")
print(response.json())

# 批量验证
response = httpx.post("http://localhost:8000/api/v1/validate/batch", json={
    "emails": ["user1@example.com", "user2@test.com"],
    "level": "full"
})
print(response.json())
```
    """,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(router, prefix="/api/v1")


# 根路由
@app.get("/", tags=["根"])
async def root():
    """
    根路径，返回API信息
    """
    return {
        "name": "邮箱验证API",
        "version": __version__,
        "description": "不发送邮件，验证邮箱地址是否能够正常接收邮件",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
