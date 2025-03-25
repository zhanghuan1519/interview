def parse_resume(file_path: str) -> dict:
    """
    模拟简历解析功能，实际中可以调用第三方AI解析服务
    """
    # 示例返回解析结果
    return {
        "parsed_name": "张三",
        "parsed_education": "本科",
        "parsed_experience": '{"years": 3, "details": "曾在XX公司任职"}'
    }
