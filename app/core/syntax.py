"""
邮箱语法验证器
基于 RFC 5322 标准进行格式验证
"""
import re
from typing import Tuple, Optional
from app.models.schemas import SyntaxResult


class SyntaxValidator:
    """邮箱语法验证器"""

    # RFC 5322 兼容的邮箱正则表达式
    EMAIL_REGEX = re.compile(
        r"^(?P<local>"
        r"[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+"
        r"(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
        r"|"
        r'"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]'
        r'|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*"'
        r")"
        r"@"
        r"(?P<domain>"
        r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+"
        r"[a-zA-Z]{2,}"
        r")$",
        re.IGNORECASE
    )

    # 简化的邮箱正则（用于快速验证）
    SIMPLE_EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        re.IGNORECASE
    )

    # 常见的无效模式
    INVALID_PATTERNS = [
        (r"\.{2,}", "连续的点号"),
        (r"^\.|\.$", "以点号开头或结尾"),
        (r"@.*@", "包含多个@符号"),
        (r"\s", "包含空格"),
        (r"[<>()[\]:;,\\]", "包含非法字符"),
    ]

    # 最大长度限制
    MAX_EMAIL_LENGTH = 254
    MAX_LOCAL_LENGTH = 64
    MAX_DOMAIN_LENGTH = 253

    @classmethod
    def validate(cls, email: str) -> SyntaxResult:
        """
        验证邮箱语法格式

        Args:
            email: 待验证的邮箱地址

        Returns:
            SyntaxResult: 验证结果
        """
        if not email or not isinstance(email, str):
            return SyntaxResult(valid=False, error="邮箱地址不能为空")

        email = email.strip().lower()

        # 长度检查
        if len(email) > cls.MAX_EMAIL_LENGTH:
            return SyntaxResult(
                valid=False,
                error=f"邮箱地址过长，最大{cls.MAX_EMAIL_LENGTH}个字符"
            )

        # 基础格式检查
        if "@" not in email:
            return SyntaxResult(valid=False, error="缺少@符号")

        # 分割本地部分和域名
        parts = email.rsplit("@", 1)
        if len(parts) != 2:
            return SyntaxResult(valid=False, error="邮箱格式无效")

        local_part, domain = parts

        # 本地部分检查
        if not local_part:
            return SyntaxResult(valid=False, error="本地部分不能为空")
        if len(local_part) > cls.MAX_LOCAL_LENGTH:
            return SyntaxResult(
                valid=False,
                error=f"本地部分过长，最大{cls.MAX_LOCAL_LENGTH}个字符"
            )

        # 域名检查
        if not domain:
            return SyntaxResult(valid=False, error="域名不能为空")
        if len(domain) > cls.MAX_DOMAIN_LENGTH:
            return SyntaxResult(
                valid=False,
                error=f"域名过长，最大{cls.MAX_DOMAIN_LENGTH}个字符"
            )

        # 检查无效模式
        for pattern, message in cls.INVALID_PATTERNS:
            if re.search(pattern, email):
                return SyntaxResult(valid=False, error=message)

        # 正则验证
        if not cls.SIMPLE_EMAIL_REGEX.match(email):
            return SyntaxResult(valid=False, error="邮箱格式不符合规范")

        # 域名格式验证
        domain_error = cls._validate_domain(domain)
        if domain_error:
            return SyntaxResult(valid=False, error=domain_error)

        return SyntaxResult(
            valid=True,
            local_part=local_part,
            domain=domain
        )

    @classmethod
    def _validate_domain(cls, domain: str) -> Optional[str]:
        """验证域名格式"""
        # 检查是否以点号开头或结尾
        if domain.startswith(".") or domain.endswith("."):
            return "域名格式无效"

        # 检查是否有连续的点号
        if ".." in domain:
            return "域名包含连续的点号"

        # 分割域名标签
        labels = domain.split(".")
        if len(labels) < 2:
            return "域名必须包含至少一个点号"

        # 检查顶级域名
        tld = labels[-1]
        if len(tld) < 2:
            return "顶级域名至少需要2个字符"
        if not tld.isalpha():
            return "顶级域名只能包含字母"

        # 检查每个标签
        for label in labels:
            if not label:
                return "域名标签不能为空"
            if len(label) > 63:
                return "域名标签过长"
            if label.startswith("-") or label.endswith("-"):
                return "域名标签不能以连字符开头或结尾"
            if not re.match(r"^[a-zA-Z0-9-]+$", label):
                return "域名包含无效字符"

        return None

    @classmethod
    def normalize(cls, email: str) -> str:
        """标准化邮箱地址"""
        return email.strip().lower()
