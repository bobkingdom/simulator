"""
核心邮箱验证引擎
整合所有验证器，提供统一的验证接口
"""
import asyncio
import time
from typing import Optional
from app.models.schemas import (
    EmailValidationRequest,
    EmailValidationResult,
    BatchValidationResult,
    ValidationLevel,
    RiskLevel,
    SyntaxResult,
    DNSResult,
    SMTPResult,
    DeepAnalysisResult,
)
from app.core.syntax import SyntaxValidator
from app.core.dns import DNSValidator
from app.core.smtp import SMTPValidator
from app.core.disposable import DisposableDetector


class EmailValidator:
    """邮箱验证引擎"""

    @classmethod
    async def validate(cls, request: EmailValidationRequest) -> EmailValidationResult:
        """
        验证邮箱地址

        Args:
            request: 验证请求

        Returns:
            EmailValidationResult: 验证结果
        """
        start_time = time.time()
        email = request.email.strip().lower()

        # 初始化结果
        result = EmailValidationResult(
            email=email,
            valid=False,
            risk_level=RiskLevel.INVALID,
            score=0,
            syntax=SyntaxResult(valid=False),
            validation_time_ms=0,
            message=""
        )

        # Step 1: 语法验证
        syntax_result = SyntaxValidator.validate(email)
        result.syntax = syntax_result

        if not syntax_result.valid:
            result.message = f"语法错误: {syntax_result.error}"
            result.validation_time_ms = int((time.time() - start_time) * 1000)
            return result

        # 如果只需要语法验证
        if request.level == ValidationLevel.SYNTAX:
            result.valid = True
            result.risk_level = RiskLevel.MEDIUM
            result.score = 50
            result.message = "语法验证通过，未进行深度验证"
            result.validation_time_ms = int((time.time() - start_time) * 1000)
            return result

        domain = syntax_result.domain

        # Step 2: DNS/MX验证
        dns_result = await DNSValidator.validate(domain, timeout=request.timeout)
        result.dns = dns_result

        if not dns_result.has_mx and not dns_result.has_a_record:
            result.message = f"DNS验证失败: {dns_result.error or '无MX记录'}"
            result.validation_time_ms = int((time.time() - start_time) * 1000)
            return result

        # 如果只需要DNS验证
        if request.level == ValidationLevel.DNS:
            result.valid = True
            result.risk_level = RiskLevel.MEDIUM
            result.score = 60
            result.message = "DNS验证通过，未进行SMTP验证"
            result.validation_time_ms = int((time.time() - start_time) * 1000)
            return result

        # Step 3: SMTP验证
        smtp_result = await SMTPValidator.validate(
            email=email,
            mx_hosts=dns_result.mx_records,
            timeout=request.timeout
        )
        result.smtp = smtp_result

        # 如果只需要SMTP验证
        if request.level == ValidationLevel.SMTP:
            result = cls._calculate_result(result, syntax_result, dns_result, smtp_result, None)
            result.validation_time_ms = int((time.time() - start_time) * 1000)
            return result

        # Step 4: 深度分析（完整验证）
        deep_result = DisposableDetector.analyze(email)
        result.deep_analysis = deep_result

        # 计算最终结果
        result = cls._calculate_result(result, syntax_result, dns_result, smtp_result, deep_result)
        result.validation_time_ms = int((time.time() - start_time) * 1000)

        return result

    @classmethod
    def _calculate_result(
        cls,
        result: EmailValidationResult,
        syntax: SyntaxResult,
        dns: DNSResult,
        smtp: SMTPResult,
        deep: Optional[DeepAnalysisResult]
    ) -> EmailValidationResult:
        """计算验证结果和评分"""

        score = 0
        messages = []

        # 语法验证 (基础分 30分)
        if syntax.valid:
            score += 30

        # DNS验证 (20分)
        if dns.has_mx:
            score += 20
        elif dns.has_a_record:
            score += 10
            messages.append("使用A记录作为邮件服务器")

        # SMTP验证 (30分)
        if smtp.connectable:
            score += 10
            if smtp.accepts_mail:
                score += 20
            else:
                messages.append(smtp.error or "SMTP验证未通过")

            # Catch-all 检测扣分
            if smtp.is_catch_all:
                score -= 10
                messages.append("邮件服务器接受所有地址(catch-all)")

        # 深度分析 (20分)
        if deep:
            if not deep.is_disposable:
                score += 10
            else:
                score -= 20
                messages.append("一次性/临时邮箱")

            if not deep.is_role_account:
                score += 5
            else:
                score -= 5
                messages.append("角色账户")

            if deep.is_free_provider:
                score += 5
                if deep.provider_name:
                    messages.append(f"邮箱提供商: {deep.provider_name}")
            else:
                score += 5
                messages.append("可能是企业邮箱")

        # 确保分数在0-100范围内
        score = max(0, min(100, score))
        result.score = score

        # 确定风险等级和有效性
        if score >= 80:
            result.valid = True
            result.risk_level = RiskLevel.LOW
            result.message = "邮箱验证通过，可信度高"
        elif score >= 60:
            result.valid = True
            result.risk_level = RiskLevel.MEDIUM
            result.message = "邮箱可能有效，建议确认"
        elif score >= 40:
            result.valid = False
            result.risk_level = RiskLevel.HIGH
            result.message = "邮箱可能无效，风险较高"
        else:
            result.valid = False
            result.risk_level = RiskLevel.INVALID
            result.message = "邮箱无效"

        # 添加详细信息
        if messages:
            result.message += " (" + "; ".join(messages) + ")"

        return result

    @classmethod
    async def validate_batch(
        cls,
        emails: list[str],
        level: ValidationLevel = ValidationLevel.FULL,
        timeout: int = 10
    ) -> BatchValidationResult:
        """
        批量验证邮箱

        Args:
            emails: 邮箱列表
            level: 验证级别
            timeout: 超时时间

        Returns:
            BatchValidationResult: 批量验证结果
        """
        tasks = []
        for email in emails:
            request = EmailValidationRequest(
                email=email,
                level=level,
                timeout=timeout
            )
            tasks.append(cls.validate(request))

        results = await asyncio.gather(*tasks)

        valid_count = sum(1 for r in results if r.valid)

        return BatchValidationResult(
            total=len(emails),
            valid_count=valid_count,
            invalid_count=len(emails) - valid_count,
            results=list(results)
        )

    @classmethod
    def validate_sync(cls, request: EmailValidationRequest) -> EmailValidationResult:
        """同步版本的验证方法"""
        return asyncio.run(cls.validate(request))
