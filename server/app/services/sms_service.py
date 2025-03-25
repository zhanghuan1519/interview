def send_sms(phone_number: str, code: str) -> bool:
    """
    模拟发送验证码短信
    """
    # 实际中调用短信服务接口
    print(f"向{phone_number}发送验证码短信，验证码：{code}")
    return True