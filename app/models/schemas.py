"""
Pydantic 数据模型定义
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ValidationLevel(str, Enum):
    """验证级别"""
    SYNTAX = "syntax"           # 仅语法验证
    DNS = "dns"                 # 语法 + DNS/MX验证
    SMTP = "smtp"               # 语法 + DNS + SMTP验证
    FULL = "full"               # 完整验证（包含一次性邮箱检测等）


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"                 # 低风险 - 邮箱有效
    MEDIUM = "medium"           # 中等风险 - 可能有效
    HIGH = "high"               # 高风险 - 可能无效
    INVALID = "invalid"         # 无效邮箱


class EmailValidationRequest(BaseModel):
    """邮箱验证请求"""
    email: str = Field(..., description="待验证的邮箱地址")
    level: ValidationLevel = Field(
        default=ValidationLevel.FULL,
        description="验证级别"
    )
    timeout: int = Field(
        default=10,
        ge=1,
        le=30,
        description="SMTP验证超时时间（秒）"
    )


class BatchValidationRequest(BaseModel):
    """批量验证请求"""
    emails: list[str] = Field(..., min_length=1, max_length=100, description="邮箱列表")
    level: ValidationLevel = Field(default=ValidationLevel.FULL)
    timeout: int = Field(default=10, ge=1, le=30)


class SyntaxResult(BaseModel):
    """语法验证结果"""
    valid: bool
    local_part: Optional[str] = None
    domain: Optional[str] = None
    error: Optional[str] = None


class DNSResult(BaseModel):
    """DNS验证结果"""
    has_mx: bool = False
    mx_records: list[str] = []
    has_a_record: bool = False
    error: Optional[str] = None


class SMTPResult(BaseModel):
    """SMTP验证结果"""
    connectable: bool = False
    accepts_mail: bool = False
    is_catch_all: Optional[bool] = None
    smtp_response: Optional[str] = None
    error: Optional[str] = None


class DeepAnalysisResult(BaseModel):
    """深度分析结果"""
    is_disposable: bool = False          # 是否为一次性邮箱
    is_role_account: bool = False         # 是否为角色账户 (admin, info等)
    is_free_provider: bool = False        # 是否为免费邮箱提供商
    provider_name: Optional[str] = None   # 邮箱提供商名称
    suggestions: list[str] = []           # 建议


class EmailValidationResult(BaseModel):
    """邮箱验证完整结果"""
    email: str
    valid: bool
    risk_level: RiskLevel
    score: int = Field(ge=0, le=100, description="可信度评分 0-100")

    syntax: SyntaxResult
    dns: Optional[DNSResult] = None
    smtp: Optional[SMTPResult] = None
    deep_analysis: Optional[DeepAnalysisResult] = None

    validation_time_ms: int = Field(description="验证耗时（毫秒）")
    message: str = Field(description="验证结果说明")


class BatchValidationResult(BaseModel):
    """批量验证结果"""
    total: int
    valid_count: int
    invalid_count: int
    results: list[EmailValidationResult]


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    message: str
