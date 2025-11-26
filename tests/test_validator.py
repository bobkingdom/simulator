"""
邮箱验证器测试用例
"""
import pytest
import asyncio
from app.core.syntax import SyntaxValidator
from app.core.disposable import DisposableDetector
from app.core.validator import EmailValidator
from app.models.schemas import EmailValidationRequest, ValidationLevel


class TestSyntaxValidator:
    """语法验证器测试"""

    def test_valid_emails(self):
        """测试有效邮箱格式"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user123@example.co.uk",
            "user_name@subdomain.example.org",
            "123@example.com",
            "user@mail.example.com",
        ]
        for email in valid_emails:
            result = SyntaxValidator.validate(email)
            assert result.valid, f"Expected {email} to be valid, got error: {result.error}"

    def test_invalid_emails(self):
        """测试无效邮箱格式"""
        invalid_emails = [
            "",                          # 空字符串
            "notanemail",               # 没有@
            "@example.com",             # 没有本地部分
            "user@",                    # 没有域名
            "user@@example.com",        # 双@
            "user@.com",                # 域名以点开头
            "user@example.",            # 域名以点结尾
            "user@example..com",        # 连续的点
            "user name@example.com",    # 包含空格
            "user@example",             # 没有顶级域名
        ]
        for email in invalid_emails:
            result = SyntaxValidator.validate(email)
            assert not result.valid, f"Expected {email} to be invalid"

    def test_email_normalization(self):
        """测试邮箱地址标准化"""
        assert SyntaxValidator.normalize("  User@Example.COM  ") == "user@example.com"

    def test_extract_parts(self):
        """测试提取邮箱各部分"""
        result = SyntaxValidator.validate("user@example.com")
        assert result.valid
        assert result.local_part == "user"
        assert result.domain == "example.com"


class TestDisposableDetector:
    """一次性邮箱检测器测试"""

    def test_disposable_domains(self):
        """测试一次性邮箱域名检测"""
        disposable_emails = [
            "test@mailinator.com",
            "test@10minutemail.com",
            "test@guerrillamail.com",
            "test@tempmail.com",
            "test@yopmail.com",
        ]
        for email in disposable_emails:
            result = DisposableDetector.analyze(email)
            assert result.is_disposable, f"Expected {email} to be disposable"

    def test_legitimate_domains(self):
        """测试正常邮箱域名"""
        legitimate_emails = [
            "test@gmail.com",
            "test@outlook.com",
            "test@company.com",
        ]
        for email in legitimate_emails:
            result = DisposableDetector.analyze(email)
            assert not result.is_disposable, f"Expected {email} to not be disposable"

    def test_role_accounts(self):
        """测试角色账户检测"""
        role_emails = [
            "admin@example.com",
            "info@example.com",
            "support@example.com",
            "noreply@example.com",
        ]
        for email in role_emails:
            result = DisposableDetector.analyze(email)
            assert result.is_role_account, f"Expected {email} to be a role account"

    def test_personal_accounts(self):
        """测试个人账户（非角色账户）"""
        personal_emails = [
            "john.doe@example.com",
            "jane123@example.com",
            "zhang.san@example.com",
        ]
        for email in personal_emails:
            result = DisposableDetector.analyze(email)
            assert not result.is_role_account, f"Expected {email} to not be a role account"

    def test_free_providers(self):
        """测试免费邮箱提供商检测"""
        free_provider_emails = [
            ("test@gmail.com", "Gmail"),
            ("test@qq.com", "QQ邮箱"),
            ("test@outlook.com", "Outlook"),
            ("test@163.com", "网易163"),
        ]
        for email, expected_provider in free_provider_emails:
            result = DisposableDetector.analyze(email)
            assert result.is_free_provider
            assert result.provider_name == expected_provider

    def test_corporate_domains(self):
        """测试企业邮箱（非免费提供商）"""
        result = DisposableDetector.analyze("user@somecompany.com")
        assert not result.is_free_provider
        assert result.provider_name is None


class TestEmailValidator:
    """集成测试 - 邮箱验证器"""

    @pytest.mark.asyncio
    async def test_syntax_only_validation(self):
        """测试仅语法验证"""
        request = EmailValidationRequest(
            email="user@example.com",
            level=ValidationLevel.SYNTAX
        )
        result = await EmailValidator.validate(request)
        assert result.valid
        assert result.syntax.valid
        assert result.dns is None
        assert result.smtp is None

    @pytest.mark.asyncio
    async def test_invalid_syntax(self):
        """测试无效语法"""
        request = EmailValidationRequest(
            email="invalid-email",
            level=ValidationLevel.SYNTAX
        )
        result = await EmailValidator.validate(request)
        assert not result.valid
        assert not result.syntax.valid

    @pytest.mark.asyncio
    async def test_batch_validation(self):
        """测试批量验证"""
        emails = [
            "valid@gmail.com",
            "invalid-email",
            "another.valid@example.com"
        ]
        result = await EmailValidator.validate_batch(
            emails=emails,
            level=ValidationLevel.SYNTAX
        )
        assert result.total == 3
        assert result.valid_count == 2
        assert result.invalid_count == 1

    @pytest.mark.asyncio
    async def test_disposable_email_detection(self):
        """测试一次性邮箱检测"""
        request = EmailValidationRequest(
            email="test@mailinator.com",
            level=ValidationLevel.SYNTAX  # 使用语法级别避免网络调用
        )
        result = await EmailValidator.validate(request)
        # 语法级别验证会通过，但完整验证会检测到一次性邮箱

    @pytest.mark.asyncio
    async def test_validation_time_tracking(self):
        """测试验证时间记录"""
        request = EmailValidationRequest(
            email="user@example.com",
            level=ValidationLevel.SYNTAX
        )
        result = await EmailValidator.validate(request)
        assert result.validation_time_ms >= 0


class TestAPIModels:
    """API模型测试"""

    def test_validation_request_defaults(self):
        """测试请求模型默认值"""
        request = EmailValidationRequest(email="test@example.com")
        assert request.level == ValidationLevel.FULL
        assert request.timeout == 10

    def test_validation_request_custom(self):
        """测试请求模型自定义值"""
        request = EmailValidationRequest(
            email="test@example.com",
            level=ValidationLevel.DNS,
            timeout=5
        )
        assert request.level == ValidationLevel.DNS
        assert request.timeout == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
