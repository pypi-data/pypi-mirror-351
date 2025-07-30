from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event as BaseEvent, Message
from nonebot import get_plugin_config, get_bot

import httpx

from nonebot_plugin_alconna.uniseg import UniMessage
from typing import Optional

from .config import Config

# 获取插件配置
plugin_config = get_plugin_config(Config)

get_other_status = on_command(
    "getsleepy",
    aliases={"获取其他Sleepy状态"}
)

async def get_status_data(custom_url: Optional[str] = None) -> Optional[dict]:
    url = f"{custom_url or plugin_config.sleepyurl}/query"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        return None


def format_device_info(device_data: dict) -> str:
    device_lines = []
    for device_name, info in device_data.items():
        using_status = "✅ 使用中" if info.get('using', False) else "❌ 未使用"
        device_lines.append(
            f"  - {info.get('show_name', device_name)}: {using_status}\n"
            f"    应用: {info.get('app_name')}"
        )
    return "\n".join(device_lines)

async def create_status_message(data: dict, url: Optional[str] = None) -> UniMessage:
    msg = UniMessage()

    # info
    if 'info' in data and isinstance(data['info'], dict):
        info = data['info']
        display_url = url or plugin_config.sleepyurl
        msg += (
            f"👋你好 {display_url}\n"
            f"🌐 个人信息:\n"
            f"  状态: {info.get('name')}\n"
            f"  {info.get('desc')}\n"
        )

    # device info
    if 'device' in data and isinstance(data['device'], dict):
        msg += "\n\n📱 设备使用情况:\n"
        msg += format_device_info(data['device'])

    # 最后更新时间
    if 'last_updated' in data:
        msg += f"\n\n⏱ 最后更新: {data['last_updated']}"
    
    return msg

@get_other_status.handle()
async def handle_get_other_status(arg_msg: Message = CommandArg()):
    """处理getsleepy命令"""
    # 获取URL参数
    url = arg_msg.extract_plain_text().strip()
    if not url:
        await get_other_status.send("请提供要查询的URL\n用法: /getsleepy url")
        return

    await get_other_status.send("正在获取状态信息，请稍候...")

    # 获取状态数据
    data = await get_status_data(url)
    
    # 如果获取数据失败，返回错误信息
    if data is None:
        await get_other_status.send("获取状态信息失败，请检查URL是否正确")
        return

    # 生成并发送消息
    msg = await create_status_message(data, url)
    await get_other_status.send(str(msg))