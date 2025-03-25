def check_device() -> dict:
    """
    模拟设备检测，返回摄像头、麦克风、网络状态
    """
    return {
        "camera": True,
        "microphone": True,
        "network": True
    }
