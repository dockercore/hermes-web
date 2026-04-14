"""
Hermes Voice Chat - Backend Server
纯 stdlib 流式调用 OpenRouter API
"""

import json
import asyncio
import ssl
import urllib.request
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

CONFIG_PATH = Path.home() / ".hermes" / "config.yaml"

def load_config():
    try:
        import yaml
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

SYSTEM_PROMPT = """你是 Hermes，一个友好、智能的AI助手。你正在通过语音和用户对话。
请遵循以下规则：
1. 回复简洁自然，适合语音播报（避免过长的段落、代码块、Markdown格式）
2. 用口语化的方式回答，就像和朋友聊天一样
3. 如果用户用中文说话，你用中文回复；用英文则英文回复
4. 避免使用特殊符号、表格等不方便语音播报的内容
5. 回答控制在3-5句话以内，保持对话节奏"""


def _do_request(url, headers, body, ctx):
    """同步: 发起请求并返回 response 对象"""
    req = urllib.request.Request(url, data=body, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    return urllib.request.urlopen(req, context=ctx, timeout=120)


async def stream_chat(messages: list):
    """流式调用 OpenRouter API，逐 token yield"""
    config = load_config()
    api_key = config.get("model", {}).get("api_key", "")
    base_url = config.get("model", {}).get("base_url", "https://openrouter.ai/api/v1")
    model = config.get("model", {}).get("default", "z-ai/glm-5.1")

    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 500,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://hermes-voice-chat.local",
    }
    ctx = ssl.create_default_context()
    loop = asyncio.get_event_loop()

    try:
        resp = await loop.run_in_executor(None, _do_request, url, headers, payload, ctx)

        buf = ""
        while True:
            chunk = await loop.run_in_executor(None, lambda: resp.read(256))
            if not chunk:
                break
            buf += chunk.decode("utf-8", errors="replace")

            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    return
                try:
                    data = json.loads(data_str)
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue

    except Exception as e:
        yield f"\n[ERROR: {e}]"


@app.get("/")
async def index():
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.websocket("/ws/chat")
async def chat_websocket(ws: WebSocket):
    await ws.accept()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)

            if payload.get("type") == "message":
                user_text = payload.get("content", "")
                if not user_text.strip():
                    continue
                messages.append({"role": "user", "content": user_text})

                full_reply = ""
                try:
                    async for token in stream_chat(messages):
                        full_reply += token
                        await ws.send_text(json.dumps({
                            "type": "stream",
                            "content": token,
                        }))

                    messages.append({"role": "assistant", "content": full_reply})
                    await ws.send_text(json.dumps({
                        "type": "done",
                        "content": full_reply,
                    }))

                except Exception as e:
                    await ws.send_text(json.dumps({
                        "type": "error",
                        "content": f"API 调用失败: {str(e)}",
                    }))

            elif payload.get("type") == "reset":
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                await ws.send_text(json.dumps({"type": "reset", "content": "对话已重置"}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
