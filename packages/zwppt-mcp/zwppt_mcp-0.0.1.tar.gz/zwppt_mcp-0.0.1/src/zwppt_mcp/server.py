from mcp.server.fastmcp import FastMCP, Context
import hashlib
import hmac
import base64
import json
import time
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from typing import Optional, Dict, Any
import os

mcp = FastMCP(
    "ZWPPT_MCP",
    description="讯飞智能PPT生成服务MCP服务器，提供PPT生成、大纲生成、模板管理等功能。所有工具均为原子化，参数和依赖关系详见各工具描述。所有API鉴权信息通过环境变量AIPPT_APP_ID和AIPPT_API_SECRET读取。"
)

# 读取环境变量
AIPPT_APP_ID = os.getenv("AIPPT_APP_ID")
AIPPT_API_SECRET = os.getenv("AIPPT_API_SECRET")


def get_signature(app_id: str, api_secret: str, ts: int) -> str:
    """生成讯飞API签名"""
    auth = hashlib.md5((app_id + str(ts)).encode('utf-8')).hexdigest()
    return base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), auth.encode('utf-8'), hashlib.sha1).digest()
    ).decode('utf-8')

def get_headers(content_type: str = "application/json; charset=utf-8") -> dict:
    if not AIPPT_APP_ID or not AIPPT_API_SECRET:
        raise Exception("请先设置环境变量AIPPT_APP_ID和AIPPT_API_SECRET")
    timestamp = int(time.time())
    signature = get_signature(AIPPT_APP_ID, AIPPT_API_SECRET, timestamp)
    return {
        "appId": AIPPT_APP_ID,
        "timestamp": str(timestamp),
        "signature": signature,
        "Content-Type": content_type
    }

@mcp.tool()
def get_theme_list(
    ctx: Context,
    pay_type: str = "not_free",
    style: Optional[str] = None,
    color: Optional[str] = None,
    industry: Optional[str] = None,
    page_num: int = 2,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    获取PPT模板列表。
    
    使用说明：
    1. 此工具用于获取可用的PPT模板列表，需先调用本工具获取template_id，后续PPT生成需用到。
    2. 可通过style、color、industry等参数筛选模板。
    3. 需先设置环境变量AIPPT_APP_ID和AIPPT_API_SECRET。
    
    参数：
    - pay_type: 模板付费类型，可选值：free-免费模板，not_free-付费模板。
    - style: 模板风格，如：简约、商务、科技等。
    - color: 模板颜色，如：红色、蓝色等。
    - industry: 模板行业，如：教育培训、金融等。
    - page_num: 页码，从1开始。
    - page_size: 每页数量，最大100。
    
    返回：
    包含模板列表的字典，每个模板包含template_id等信息。
    """
    url = "https://zwapi.xfyun.cn/api/ppt/v2/template/list"
    headers = get_headers()
    params = {
        "payType": pay_type,
        "pageNum": page_num,
        "pageSize": page_size
    }
    if style:
        params["style"] = style
    if color:
        params["color"] = color
    if industry:
        params["industry"] = industry
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"调用失败: {response.text}")

    return response.text

@mcp.tool()
def create_ppt_task(
    ctx: Context,
    text: str,
    template_id: str,
    author: str = "XXXX",
    is_card_note: bool = True,
    search: bool = False,
    is_figure: bool = True,
    ai_image: str = "normal"
) -> Dict[str, Any]:
    """
    创建PPT生成任务。
    
    使用说明：
    1. 在调用本工具前，必须先调用get_theme_list获取有效的template_id。
    2. 工具会返回任务ID(sid)，需用get_task_progress轮询查询进度。
    3. 任务完成后，可从get_task_progress结果中获取PPT下载地址。
    4. 需先设置环境变量AIPPT_APP_ID和AIPPT_API_SECRET。
    
    参数：
    - text: PPT生成的内容描述，用于生成PPT的主题和内容。
    - template_id: PPT模板ID，需通过get_theme_list获取。
    - author: PPT作者名称，将显示在生成的PPT中。
    - is_card_note: 是否生成PPT演讲备注，True表示生成，False表示不生成。
    - search: 是否联网搜索，True表示联网搜索补充内容，False表示不联网。
    - is_figure: 是否自动配图，True表示自动配图，False表示不配图。
    - ai_image: AI配图类型，仅在is_figure为True时生效。可选值：normal-普通配图(20%正文配图)，advanced-高级配图(50%正文配图)。
    
    返回：
    成功时返回包含sid的字典，失败时抛出异常。
    """
    url = 'https://zwapi.xfyun.cn/api/ppt/v2/create'
    form_data = MultipartEncoder(
        fields={
            "query": text,
            "templateId": template_id,
            "author": author,
            "isCardNote": str(is_card_note),
            "search": str(search),
            "isFigure": str(is_figure),
            "aiImage": ai_image
        }
    )
    headers = get_headers(form_data.content_type)
    response = requests.post(url, data=form_data, headers=headers)

    if response.status_code != 200:
        raise Exception(f"调用失败: {response.text}")

    resp = json.loads(response.text)
    if resp['code'] == 0:
        return {"sid": resp['data']['sid']}
    else:
        raise Exception(f"调用失败: {response.text}")

@mcp.tool()
def get_task_progress(
    ctx: Context,
    sid: str
) -> Dict[str, Any]:
    """
    查询PPT生成任务进度。
    
    使用说明：
    1. 用于查询通过create_ppt_task或create_ppt_by_outline创建的任务进度。
    2. 需定期轮询本工具直到任务完成。
    3. 任务完成后，可从返回结果中获取PPT下载地址。
    4. 需先设置环境变量AIPPT_APP_ID和AIPPT_API_SECRET。
    
    参数：
    - sid: 任务ID，从create_ppt_task或create_ppt_by_outline工具获取。
    
    返回：
    包含任务状态和PPT下载地址的字典。
    """
    url = f"https://zwapi.xfyun.cn/api/ppt/v2/progress?sid={sid}"
    headers = get_headers()
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"调用失败: {response.text}")
    
    return response.text

@mcp.tool()
def create_outline(
    ctx: Context,
    text: str,
    language: str = "cn",
    search: bool = False
) -> Dict[str, Any]:
    """
    创建PPT大纲。
    
    使用说明：
    1. 用于根据文本内容生成PPT大纲。
    2. 生成的大纲可用于create_ppt_by_outline工具。
    3. 可通过search参数控制是否联网搜索补充内容。
    4. 需先设置环境变量AIPPT_APP_ID和AIPPT_API_SECRET。
    
    参数：
    - text: 需要生成大纲的内容描述。
    - language: 大纲生成的语言，目前支持cn(中文)。
    - search: 是否联网搜索，True表示联网搜索补充内容，False表示不联网。
    
    返回：
    包含生成的大纲内容的字典。
    """
    url = "https://zwapi.xfyun.cn/api/ppt/v2/createOutline"
    form_data = MultipartEncoder(
        fields={
            "query": text,
            "language": language,
            "search": str(search)
        }
    )
    headers = get_headers(form_data.content_type)
    response = requests.post(url, data=form_data, headers=headers)

    if response.status_code != 200:
        raise Exception(f"调用失败: {response.text}")

    return response.text

@mcp.tool()
def create_outline_by_doc(
    ctx: Context,
    file_name: str,
    text: str,
    file_url: Optional[str] = None,
    file_path: Optional[str] = None,
    language: str = "cn",
    search: bool = False
) -> Dict[str, Any]:
    """
    从文档创建PPT大纲。
    
    使用说明：
    1. 用于根据文档内容生成PPT大纲。
    2. 支持通过file_url或file_path上传文档。
    3. 文档格式支持：pdf(不支持扫描件)、doc、docx、txt、md。
    4. 文档大小限制：10M以内，字数限制8000字以内。
    5. 生成的大纲可用于create_ppt_by_outline工具。
    6. 需先设置环境变量AIPPT_APP_ID和AIPPT_API_SECRET。
    
    参数：
    - file_name: 文档文件名，必须包含文件后缀名。
    - file_url: 文档文件的URL地址，与file_path二选一必填。
    - file_path: 文档文件的本地路径，与file_url二选一必填。
    - text: 补充的文本内容，用于指导大纲生成。
    - language: 大纲生成的语言，目前支持cn(中文)。
    - search: 是否联网搜索，True表示联网搜索补充内容，False表示不联网。
    
    返回：
    包含生成的大纲内容的字典。
    """
    url = "https://zwapi.xfyun.cn/api/ppt/v2/createOutlineByDoc"
    fields = {
        "fileName": file_name,
        "query": text,
        "language": language,
        "search": str(search)
    }
    if file_url:
        fields["fileUrl"] = file_url
    elif file_path:
        fields["file"] = (file_name, open(file_path, 'rb'), 'text/plain')
    form_data = MultipartEncoder(fields=fields)
    headers = get_headers(form_data.content_type)
    response = requests.post(url, data=form_data, headers=headers)

    if response.status_code != 200:
        raise Exception(f"调用失败: {response.text}")
    
    return response.text

@mcp.tool()
def create_ppt_by_outline(
    ctx: Context,
    text: str,
    outline: dict,
    template_id: str,
    author: str = "XXXX",
    is_card_note: bool = True,
    search: bool = False,
    is_figure: bool = True,
    ai_image: str = "normal"
) -> Dict[str, Any]:
    """
    根据大纲创建PPT。
    
    使用说明：
    1. 用于根据已生成的大纲创建PPT。
    2. 大纲需通过create_outline或create_outline_by_doc工具生成。
    3. template_id需通过get_theme_list工具获取。
    4. 工具会返回任务ID(sid)，需用get_task_progress轮询查询进度。
    5. 任务完成后，可从get_task_progress结果中获取PPT下载地址。
    6. 需先设置环境变量AIPPT_APP_ID和AIPPT_API_SECRET。
    
    参数：
    - text: PPT生成的内容描述，用于指导PPT生成。
    - outline: 大纲内容，需从create_outline或create_outline_by_doc工具返回的JSON响应中提取['data']['outline']字段的值。该字段包含生成的大纲内容，格式为dict。
    - template_id: PPT模板ID，需通过get_theme_list工具获取。
    - author: PPT作者名称，将显示在生成的PPT中。
    - is_card_note: 是否生成PPT演讲备注，True表示生成，False表示不生成。
    - search: 是否联网搜索，True表示联网搜索补充内容，False表示不联网。
    - is_figure: 是否自动配图，True表示自动配图，False表示不配图。
    - ai_image: AI配图类型，仅在is_figure为True时生效。可选值：normal-普通配图(20%正文配图)，advanced-高级配图(50%正文配图)。
    
    返回：
    成功时返回包含sid的字典，失败时抛出异常。
    """
    url = "https://zwapi.xfyun.cn/api/ppt/v2/createPptByOutline"
    headers = get_headers()
    if isinstance(outline, str):
        outline = json.loads(outline)
    body = {
        "query": text,
        "outline": outline,
        "templateId": template_id,
        "author": author,
        "isCardNote": is_card_note,
        "search": search,
        "isFigure": is_figure,
        "aiImage": ai_image
    }
    response = requests.post(url, json=body, headers=headers)

    if response.status_code != 200:
        raise Exception(f"调用失败: {response.text}")
    
    resp = json.loads(response.text)
    if resp['code'] == 0:
        return {"sid": resp['data']['sid']}
    else:
        raise Exception(f"根据大纲创建PPT失败: {response.text}")

def main():
    mcp.run()

if __name__ == "__main__":
    main()