def send_invitation(email: str, interview_link: str) -> bool:
    """
    模拟发送面试邀请邮件
    """
    # 实际中调用邮件服务接口
    print(f"向{email}发送面试邀请，链接：{interview_link}")
    return True


def send_email(email_address: str, code: str) -> bool:
    """
    模拟发送验证码邮件
    """
    # 实际中调用邮件服务接口
    print(f"向{email_address}发送验证码邮件，验证码：{code}")
    return True