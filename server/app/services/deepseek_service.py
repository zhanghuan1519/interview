from datetime import time
from openai import OpenAI
import json

api_key="sk-a3639789c53545a98dfd9590c70f8d19"

def call_deepseek(question_count: int, tech_question_percent: int, resume: str, job_title:str, job_description: str, job_requirements: str):
    a = """{
        "questions": [
            {
                "content": "请描述一次您成功设计并实施的云解决方案案例，包括您如何理解客户需求、设计解决方案以及最终的实施效果。",
                "type": "technical"
            },
            {
                "content": "在您的职业生涯中，您是如何处理跨部门或跨公司合作中的技术挑战的？请举例说明。",
                "type": "technical"
            },
            {
                "content": "您如何看待公有云、混合云、Openstack、IaaS、PaaS等技术在当前云原生行业中的应用和发展趋势？",
                "type": "technical"
            },
            {
                "content": "在您负责的珠海市公共数据授权运营项目中，您是如何规划技术方案并确保其成功实施的？",
                "type": "technical"
            },
            {
                "content": "请分享一次您在项目中使用大数据、数据库、IOT、AI等技术解决实际问题的经验。",
                "type": "technical"
            },
            {
                "content": "在您的职业生涯中，您是如何快速学习并掌握新技术或新产品的？请举例说明。",
                "type": "technical"
            },
            {
                "content": "您如何评估一个云解决方案的可行性，包括技术可行性、成本效益分析和风险评估？",
                "type": "technical"
            },
            {
                "content": "在您的工作经历中，您是如何处理项目中的突发技术问题或挑战的？请分享一个具体的例子。",
                "type": "technical"
            },
            {
                "content": "在您的职业生涯中，您是如何与客户沟通并理解他们的业务需求的？请分享一个成功的案例。",
                "type": "behavioral"
            },
            {
                "content": "请描述一次您在团队中扮演领导角色，成功推动项目进展的经历。",
                "type": "behavioral"
            }
        ]
    }"""    
    return json.loads(a)
    
    
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    system_prompt = """
    你是一个AI面试官,你的任务是为候选人提供面试问题.所有问的问题的语言为中文.你问的问题必须仔细结合岗位需求和候选人的简历情况.
    你的输出内容以JSON格式返回,包含一个问题列表,每个问题包含问题内容和问题类型.其中,问题类型包括: technical, behavioral, follow_up.
    输出格式为:
    {
        "questions": [
            {
                "content": "问题内容",
                "type": "问题类型"
            }
        ]
    }
    """
    user_prompt = """
    请你结合候选人简历和岗位的各种要求输出面试问题,需要输出的问题个数为{},其中技术问题占比为{}%,其余为行为问题.
    候选人简历: {}
    岗位名称: {}
    岗位描述: {}
    岗位要求: {}
    """
    user_prompt = user_prompt.format(question_count, tech_question_percent, resume, job_title, job_description, job_requirements)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt}, 
            {"role": "user", "content": user_prompt}
        ],
        response_format= {
            'type': 'json_object'
        }
    )
    print(response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)