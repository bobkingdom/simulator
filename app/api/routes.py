"""
API路由定义
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import (
    EmailValidationRequest,
    EmailValidationResult,
    BatchValidationRequest,
    BatchValidationResult,
    ValidationLevel,
    HealthResponse,
)
from app.core.validator import EmailValidator
from app import __version__


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """
    健康检查接口

    返回服务状态和版本信息
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        message="邮箱验证服务运行正常"
    )


@router.post("/validate", response_model=EmailValidationResult, tags=["验证"])
async def validate_email(request: EmailValidationRequest):
    """
    验证单个邮箱地址

    验证级别说明：
    - **syntax**: 仅验证邮箱格式
    - **dns**: 验证格式 + DNS/MX记录
    - **smtp**: 验证格式 + DNS + SMTP服务器连接
    - **full**: 完整验证（包含一次性邮箱检测等）

    返回结果包含：
    - 有效性判断
    - 风险等级 (low/medium/high/invalid)
    - 可信度评分 (0-100)
    - 详细验证信息
    """
    try:
        result = await EmailValidator.validate(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")


@router.get("/validate/{email}", response_model=EmailValidationResult, tags=["验证"])
async def validate_email_get(
    email: str,
    level: ValidationLevel = Query(
        default=ValidationLevel.FULL,
        description="验证级别"
    ),
    timeout: int = Query(
        default=10,
        ge=1,
        le=30,
        description="超时时间（秒）"
    )
):
    """
    通过GET请求验证邮箱地址

    快捷接口，直接在URL中传入邮箱地址
    """
    request = EmailValidationRequest(
        email=email,
        level=level,
        timeout=timeout
    )
    try:
        result = await EmailValidator.validate(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")


@router.post("/validate/batch", response_model=BatchValidationResult, tags=["验证"])
async def validate_emails_batch(request: BatchValidationRequest):
    """
    批量验证邮箱地址

    支持同时验证多个邮箱地址（最多100个）

    返回：
    - 总数统计
    - 有效/无效计数
    - 每个邮箱的详细验证结果
    """
    try:
        result = await EmailValidator.validate_batch(
            emails=request.emails,
            level=request.level,
            timeout=request.timeout
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量验证失败: {str(e)}")


@router.get("/check/{email}", tags=["快捷验证"])
async def quick_check(email: str):
    """
    快速验证接口

    返回简化的验证结果，适合快速检查

    返回格式：
    ```json
    {
        "email": "user@example.com",
        "valid": true,
        "score": 85,
        "risk": "low"
    }
    ```
    """
    request = EmailValidationRequest(
        email=email,
        level=ValidationLevel.FULL,
        timeout=10
    )
    try:
        result = await EmailValidator.validate(request)
        return {
            "email": result.email,
            "valid": result.valid,
            "score": result.score,
            "risk": result.risk_level.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")
