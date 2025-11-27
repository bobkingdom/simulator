"""
SMTP验证器
通过SMTP协议验证邮箱是否存在（不发送实际邮件）
"""
import asyncio
import socket
from typing import Optional, Tuple
import aiosmtplib
from aiosmtplib import SMTP, SMTPException
from app.models.schemas import SMTPResult


class SMTPValidator:
    """SMTP验证器 - 不发送邮件验证邮箱是否存在"""

    # 默认配置
    DEFAULT_TIMEOUT = 10
    DEFAULT_PORT = 25
    BACKUP_PORTS = [587, 465]

    # 用于验证的发件人地址
    SENDER_EMAIL = "verify@email-validator.local"

    # Catch-all 检测用的随机地址
    CATCH_ALL_TEST_USER = "nonexistent_user_test_12345678"

    @classmethod
    async def validate(
        cls,
        email: str,
        mx_hosts: list[str],
        timeout: int = DEFAULT_TIMEOUT
    ) -> SMTPResult:
        """
        通过SMTP验证邮箱是否存在

        原理：
        1. 连接到MX服务器
        2. 发送 HELO/EHLO 命令
        3. 发送 MAIL FROM 命令
        4. 发送 RCPT TO 命令检查收件人是否存在
        5. 不发送 DATA 和实际邮件内容

        Args:
            email: 待验证的邮箱地址
            mx_hosts: MX服务器列表
            timeout: 超时时间（秒）

        Returns:
            SMTPResult: SMTP验证结果
        """
        result = SMTPResult()

        if not mx_hosts:
            result.error = "没有可用的MX服务器"
            return result

        # 尝试每个MX服务器
        last_error = None
        for mx_host in mx_hosts[:3]:  # 最多尝试3个MX服务器
            try:
                smtp_result = await cls._verify_with_host(
                    email, mx_host, timeout
                )
                if smtp_result.connectable:
                    return smtp_result
                last_error = smtp_result.error
            except Exception as e:
                last_error = str(e)
                continue

        result.error = last_error or "所有MX服务器连接失败"
        return result

    @classmethod
    async def _verify_with_host(
        cls,
        email: str,
        mx_host: str,
        timeout: int
    ) -> SMTPResult:
        """使用指定的MX主机验证邮箱"""
        result = SMTPResult()

        try:
            # 尝试连接
            smtp = SMTP(
                hostname=mx_host,
                port=cls.DEFAULT_PORT,
                timeout=timeout
            )

            try:
                await smtp.connect()
                result.connectable = True

                # 发送 EHLO
                hostname = socket.getfqdn()
                await smtp.ehlo(hostname)

                # 发送 MAIL FROM
                code, message = await smtp.execute_command(
                    "MAIL", f"FROM:<{cls.SENDER_EMAIL}>"
                )

                if code >= 400:
                    result.smtp_response = f"{code} {message}"
                    result.error = "MAIL FROM 被拒绝"
                    return result

                # 发送 RCPT TO 验证收件人
                code, message = await smtp.execute_command(
                    "RCPT", f"TO:<{email}>"
                )

                result.smtp_response = f"{code} {message}"

                if code == 250:
                    result.accepts_mail = True
                    # 检测是否为 catch-all
                    result.is_catch_all = await cls._check_catch_all(
                        smtp, email
                    )
                elif code == 251:
                    # 用户不在本地，但会转发
                    result.accepts_mail = True
                elif code in (450, 451, 452):
                    # 临时错误，可能有效
                    result.accepts_mail = False
                    result.error = f"临时错误: {message}"
                elif code in (550, 551, 552, 553):
                    # 永久错误，用户不存在
                    result.accepts_mail = False
                    result.error = f"邮箱不存在: {message}"
                else:
                    result.accepts_mail = False
                    result.error = f"未知响应: {code} {message}"

                # 发送 RSET 重置状态
                await smtp.execute_command("RSET")

            finally:
                try:
                    await smtp.quit()
                except Exception:
                    pass

        except asyncio.TimeoutError:
            result.error = f"连接 {mx_host} 超时"
        except aiosmtplib.SMTPConnectError as e:
            result.error = f"无法连接到 {mx_host}: {str(e)}"
        except aiosmtplib.SMTPServerDisconnected:
            result.error = f"服务器 {mx_host} 断开连接"
        except Exception as e:
            result.error = f"SMTP验证错误: {str(e)}"

        return result

    @classmethod
    async def _check_catch_all(cls, smtp: SMTP, email: str) -> Optional[bool]:
        """
        检测是否为 catch-all 邮箱服务器

        Catch-all 服务器会接受任何收件人地址
        """
        try:
            domain = email.split("@")[1]
            test_email = f"{cls.CATCH_ALL_TEST_USER}@{domain}"

            code, _ = await smtp.execute_command(
                "RCPT", f"TO:<{test_email}>"
            )

            # 如果随机地址也被接受，则可能是 catch-all
            return code == 250

        except Exception:
            return None

    @classmethod
    def validate_sync(
        cls,
        email: str,
        mx_hosts: list[str],
        timeout: int = DEFAULT_TIMEOUT
    ) -> SMTPResult:
        """同步版本的SMTP验证"""
        return asyncio.run(cls.validate(email, mx_hosts, timeout))
