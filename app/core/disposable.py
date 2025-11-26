"""
一次性邮箱检测器
检测临时邮箱、一次性邮箱、角色账户等
"""
from typing import Set, Optional
from app.models.schemas import DeepAnalysisResult


class DisposableDetector:
    """一次性/临时邮箱检测器"""

    # 常见的一次性邮箱域名列表
    DISPOSABLE_DOMAINS: Set[str] = {
        # 10 Minute Mail 系列
        "10minutemail.com", "10minutemail.net", "10minutemail.org",
        "10minutemail.co.uk", "10minutemail.de",
        # Guerrilla Mail
        "guerrillamail.com", "guerrillamail.net", "guerrillamail.org",
        "guerrillamail.biz", "guerrillamail.de", "guerrillamailblock.com",
        # Temp Mail
        "tempmail.com", "temp-mail.org", "temp-mail.io", "tempail.com",
        "tempmailaddress.com", "tempmail.net", "tempmail.de",
        # Mailinator
        "mailinator.com", "mailinator.net", "mailinator.org",
        "mailinator2.com", "mailinater.com",
        # 其他常见临时邮箱
        "throwaway.email", "throwawaymail.com", "trashmail.com",
        "trashmail.net", "trashmail.org", "trash-mail.com",
        "fakeinbox.com", "fakemailgenerator.com",
        "getnada.com", "getairmail.com",
        "mohmal.com", "maildrop.cc", "mailnesia.com",
        "yopmail.com", "yopmail.fr", "yopmail.net",
        "dispostable.com", "mailcatch.com", "mailslurp.com",
        "sharklasers.com", "spam4.me", "spamgourmet.com",
        "spambox.us", "spamfree24.org", "spamherelots.com",
        "emailondeck.com", "anonymbox.com", "bgsaddrmwn.com",
        "burnermail.io", "clrmail.com", "discard.email",
        "discardmail.com", "dropmail.me", "emailsensei.com",
        "fakemail.fr", "fakemailgenerator.net",
        "inboxalias.com", "jetable.org", "mailforspam.com",
        "mintemail.com", "mytrashmail.com", "nada.email",
        "proxymail.eu", "rcpt.at", "spambog.com",
        "spamex.com", "spamfree.eu", "spamspot.com",
        "tempomail.fr", "tempsky.com", "wegwerfmail.de",
        "wegwerfmail.net", "wegwerfmail.org",
    }

    # 常见的免费邮箱提供商
    FREE_PROVIDERS: dict[str, str] = {
        # 全球主流
        "gmail.com": "Gmail",
        "googlemail.com": "Gmail",
        "outlook.com": "Outlook",
        "hotmail.com": "Hotmail",
        "live.com": "Microsoft Live",
        "msn.com": "MSN",
        "yahoo.com": "Yahoo",
        "yahoo.co.uk": "Yahoo UK",
        "yahoo.co.jp": "Yahoo Japan",
        "ymail.com": "Yahoo",
        "icloud.com": "Apple iCloud",
        "me.com": "Apple",
        "mac.com": "Apple",
        "aol.com": "AOL",
        "protonmail.com": "ProtonMail",
        "proton.me": "ProtonMail",
        "zoho.com": "Zoho",
        "mail.com": "Mail.com",
        "gmx.com": "GMX",
        "gmx.net": "GMX",
        "gmx.de": "GMX",
        # 中国主流
        "qq.com": "QQ邮箱",
        "foxmail.com": "Foxmail",
        "163.com": "网易163",
        "126.com": "网易126",
        "yeah.net": "网易yeah",
        "sina.com": "新浪邮箱",
        "sina.cn": "新浪邮箱",
        "sohu.com": "搜狐邮箱",
        "aliyun.com": "阿里云邮箱",
        "139.com": "中国移动",
        "189.cn": "中国电信",
        "wo.cn": "中国联通",
        # 其他地区
        "naver.com": "Naver (韩国)",
        "daum.net": "Daum (韩国)",
        "yandex.com": "Yandex (俄罗斯)",
        "yandex.ru": "Yandex (俄罗斯)",
        "mail.ru": "Mail.ru (俄罗斯)",
        "web.de": "Web.de (德国)",
        "t-online.de": "T-Online (德国)",
        "libero.it": "Libero (意大利)",
    }

    # 角色账户前缀（通常是通用账户，不是个人账户）
    ROLE_PREFIXES: Set[str] = {
        "admin", "administrator", "webmaster", "hostmaster",
        "postmaster", "root", "abuse", "noc", "security",
        "info", "information", "contact", "support", "help",
        "sales", "marketing", "billing", "accounts", "accounting",
        "hr", "jobs", "careers", "recruitment",
        "feedback", "suggestions", "complaints",
        "news", "newsletter", "subscribe", "unsubscribe",
        "noreply", "no-reply", "donotreply", "do-not-reply",
        "mailer-daemon", "null", "nobody",
        "office", "reception", "mail", "email",
        "team", "staff", "hello", "hi", "enquiries", "enquiry",
        "press", "media", "pr", "legal",
        "privacy", "compliance", "gdpr", "dpo",
        "orders", "order", "shipping", "returns",
        "all", "everyone", "company", "general",
    }

    @classmethod
    def analyze(cls, email: str) -> DeepAnalysisResult:
        """
        深度分析邮箱地址

        Args:
            email: 邮箱地址

        Returns:
            DeepAnalysisResult: 分析结果
        """
        result = DeepAnalysisResult()
        suggestions = []

        try:
            local_part, domain = email.lower().split("@", 1)
        except ValueError:
            return result

        # 检测一次性邮箱
        result.is_disposable = cls._is_disposable(domain)
        if result.is_disposable:
            suggestions.append("此邮箱为一次性/临时邮箱，可能很快失效")

        # 检测免费邮箱提供商
        provider = cls.FREE_PROVIDERS.get(domain)
        if provider:
            result.is_free_provider = True
            result.provider_name = provider
        else:
            result.is_free_provider = False
            # 检查是否为企业邮箱
            if not result.is_disposable:
                suggestions.append("此邮箱可能是企业或组织邮箱")

        # 检测角色账户
        result.is_role_account = cls._is_role_account(local_part)
        if result.is_role_account:
            suggestions.append("此邮箱可能是通用角色账户，非个人邮箱")

        # 检查本地部分的质量
        local_suggestions = cls._analyze_local_part(local_part)
        suggestions.extend(local_suggestions)

        result.suggestions = suggestions
        return result

    @classmethod
    def _is_disposable(cls, domain: str) -> bool:
        """检测是否为一次性邮箱域名"""
        domain = domain.lower()

        # 直接匹配
        if domain in cls.DISPOSABLE_DOMAINS:
            return True

        # 检查子域名
        parts = domain.split(".")
        for i in range(len(parts) - 1):
            parent_domain = ".".join(parts[i:])
            if parent_domain in cls.DISPOSABLE_DOMAINS:
                return True

        # 检查常见的一次性邮箱特征
        disposable_keywords = [
            "temp", "tmp", "disposable", "throwaway",
            "trash", "spam", "fake", "guerrilla",
            "mailinator", "10minute", "minute"
        ]
        for keyword in disposable_keywords:
            if keyword in domain:
                return True

        return False

    @classmethod
    def _is_role_account(cls, local_part: str) -> bool:
        """检测是否为角色账户"""
        local_part = local_part.lower()

        # 精确匹配
        if local_part in cls.ROLE_PREFIXES:
            return True

        # 带数字后缀的匹配 (如 admin1, support2)
        for prefix in cls.ROLE_PREFIXES:
            if local_part.startswith(prefix) and local_part[len(prefix):].isdigit():
                return True

        return False

    @classmethod
    def _analyze_local_part(cls, local_part: str) -> list[str]:
        """分析本地部分的特征"""
        suggestions = []

        # 检查是否过短
        if len(local_part) < 3:
            suggestions.append("邮箱用户名过短，可信度较低")

        # 检查是否全是数字
        if local_part.isdigit():
            suggestions.append("邮箱用户名全为数字")

        # 检查是否有随机特征
        if cls._looks_random(local_part):
            suggestions.append("邮箱用户名看起来可能是随机生成的")

        return suggestions

    @classmethod
    def _looks_random(cls, s: str) -> bool:
        """检测字符串是否看起来像随机生成的"""
        if len(s) < 8:
            return False

        # 去除常见分隔符后检查
        cleaned = s.replace(".", "").replace("_", "").replace("-", "")

        # 检查连续的辅音/元音比例
        vowels = set("aeiou")
        consonants = set("bcdfghjklmnpqrstvwxyz")

        vowel_count = sum(1 for c in cleaned.lower() if c in vowels)
        consonant_count = sum(1 for c in cleaned.lower() if c in consonants)

        # 如果几乎没有元音，可能是随机的
        if len(cleaned) > 6 and vowel_count < len(cleaned) * 0.15:
            return True

        # 如果数字字母混合且较长
        digits = sum(1 for c in cleaned if c.isdigit())
        if len(cleaned) > 10 and digits > len(cleaned) * 0.4:
            return True

        return False

    @classmethod
    def is_disposable_domain(cls, domain: str) -> bool:
        """检测域名是否为一次性邮箱域名"""
        return cls._is_disposable(domain)

    @classmethod
    def get_provider_name(cls, domain: str) -> Optional[str]:
        """获取邮箱提供商名称"""
        return cls.FREE_PROVIDERS.get(domain.lower())
