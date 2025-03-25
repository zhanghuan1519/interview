def generate_interview_questions(config: dict) -> list:
    """
    根据面试规则生成题目列表，实际可结合AI接口生成问题
    """
    question_count = config.get("question_count", 10)
    questions = []
    for i in range(1, question_count+1):
        questions.append({
            "order": i,
            "question_text": f"请回答第{i}个面试问题",
            "question_type": "technical",
            "answer_time_limit": config.get("answer_duration", 300)
        })
    return questions
