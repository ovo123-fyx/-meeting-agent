"""Agent 可调用的工具。

每个工具是一个普通的 Python 函数。模型只能看到 TOOL_SCHEMAS 中的
声明，决定调用哪一个后由 dispatch() 实际执行。
"""

from data import NOTES


# ---------- 工具：列出会议 ----------

def list_meetings():
    """返回所有会议的日期与标题，不含正文。"""
    return [{"date": n["date"], "title": n["title"]} for n in NOTES]


# ---------- 工具：按关键词检索纪要 ----------

def search_notes(keyword):
    """返回正文包含 keyword 的会议（日期、标题、正文）；无匹配时返回 []。"""
    results = []
    for n in NOTES:
        if keyword in n["content"]:
            results.append(n)
    return results


# ---------- 工具声明（传给模型） ----------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_meetings",
            "description": "列出所有会议的日期和标题。当用户问有哪些会议、"
                           "或者需要先知道有什么会可查的时候用。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "在所有会议纪要的正文里搜索一个关键词，"
                           "返回包含该关键词的会议内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "要搜索的关键词，例如 预算、准确率、导出",
                    }
                },
                "required": ["keyword"],
            },
        },
    },
]


# ---------- 名称到实现的映射 ----------

REGISTRY = {
    "list_meetings": list_meetings,
    "search_notes": search_notes,
}


def dispatch(name, args):
    """按模型给出的名称和参数执行对应函数。"""
    if name not in REGISTRY:
        return {"error": f"未注册的工具: {name}"}
    return REGISTRY[name](**args)
