"""
DNS/MX记录验证器
验证域名是否存在且配置了邮件服务器
"""
import asyncio
from typing import List, Tuple
import dns.resolver
import dns.asyncresolver
from app.models.schemas import DNSResult


class DNSValidator:
    """DNS/MX记录验证器"""

    # DNS查询超时时间
    DEFAULT_TIMEOUT = 5.0

    @classmethod
    async def validate(cls, domain: str, timeout: float = DEFAULT_TIMEOUT) -> DNSResult:
        """
        验证域名的DNS记录

        Args:
            domain: 域名
            timeout: 超时时间（秒）

        Returns:
            DNSResult: DNS验证结果
        """
        result = DNSResult()

        try:
            # 创建异步解析器
            resolver = dns.asyncresolver.Resolver()
            resolver.timeout = timeout
            resolver.lifetime = timeout

            # 并行查询 MX 和 A 记录
            mx_task = cls._query_mx(resolver, domain)
            a_task = cls._query_a(resolver, domain)

            mx_result, a_result = await asyncio.gather(
                mx_task, a_task,
                return_exceptions=True
            )

            # 处理MX查询结果
            if isinstance(mx_result, Exception):
                if not isinstance(mx_result, dns.resolver.NXDOMAIN):
                    result.error = f"MX查询异常: {str(mx_result)}"
            else:
                result.has_mx = mx_result[0]
                result.mx_records = mx_result[1]

            # 处理A记录查询结果
            if isinstance(a_result, Exception):
                pass  # A记录查询失败不影响结果
            else:
                result.has_a_record = a_result

            # 如果没有MX但有A记录，可能使用A记录作为邮件服务器
            if not result.has_mx and result.has_a_record:
                result.mx_records = [domain]

        except dns.resolver.NXDOMAIN:
            result.error = "域名不存在"
        except dns.resolver.NoAnswer:
            result.error = "域名无DNS记录"
        except dns.resolver.Timeout:
            result.error = "DNS查询超时"
        except Exception as e:
            result.error = f"DNS查询失败: {str(e)}"

        return result

    @classmethod
    async def _query_mx(
        cls,
        resolver: dns.asyncresolver.Resolver,
        domain: str
    ) -> Tuple[bool, List[str]]:
        """查询MX记录"""
        try:
            answers = await resolver.resolve(domain, "MX")
            mx_records = []
            for rdata in sorted(answers, key=lambda x: x.preference):
                mx_host = str(rdata.exchange).rstrip(".")
                mx_records.append(mx_host)
            return (len(mx_records) > 0, mx_records)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            return (False, [])
        except Exception:
            return (False, [])

    @classmethod
    async def _query_a(
        cls,
        resolver: dns.asyncresolver.Resolver,
        domain: str
    ) -> bool:
        """查询A记录"""
        try:
            answers = await resolver.resolve(domain, "A")
            return len(answers) > 0
        except Exception:
            return False

    @classmethod
    def validate_sync(cls, domain: str, timeout: float = DEFAULT_TIMEOUT) -> DNSResult:
        """同步版本的DNS验证"""
        return asyncio.run(cls.validate(domain, timeout))

    @classmethod
    async def get_mx_hosts(cls, domain: str, timeout: float = DEFAULT_TIMEOUT) -> List[str]:
        """获取MX主机列表，按优先级排序"""
        result = await cls.validate(domain, timeout)
        return result.mx_records
