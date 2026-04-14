# Hermes Voice Chat 🎙️

一个基于 Web 的语音对话应用，可以和 Hermes AI 进行实时语音交流。

## 功能特性

- 🎤 **语音输入** — 点击麦克风按钮，直接说话即可
- 🔊 **语音播报** — AI 回复自动朗读，解放双手
- 💬 **文字输入** — 也支持打字交流
- 🌊 **流式输出** — 回复逐字显示，无需等待完整响应
- 🔄 **对话重置** — 一键清空上下文，重新开始
- ⚙️ **自定义设置** — 语言、语速、音调、声音均可调整

## 快速开始

### 1. 安装依赖

```bash
pip3 install fastapi uvicorn pyyaml websockets
```

### 2. 启动服务

```bash
cd hermes-voice-chat
python3 server.py
```

服务默认运行在 `http://localhost:8765`

### 3. 打开浏览器

推荐使用 **Chrome** 浏览器访问 `http://localhost:8765`

> ⚠️ 语音识别功能依赖 Web Speech API，目前仅 Chrome 完整支持。
> 页面必须通过 localhost 或 HTTPS 访问，HTTP + 非 localhost 下语音识别不可用。

## 使用说明

### 语音对话流程

1. 点击中间的 🎤 麦克风按钮
2. 浏览器会请求麦克风权限，点击"允许"
3. 看到按钮变红并出现脉冲动画，表示正在录音
4. 说完话后再次点击按钮停止录音（或等待自动结束）
5. 识别的文字自动发送给 Hermes
6. Hermes 回复后自动语音朗读

### 键盘打字

如果不想用语音，也可以在底部输入框直接打字，按回车或点击"发送"。

### 按钮说明

| 按钮 | 功能 |
|------|------|
| 🎤 麦克风 | 开始/停止语音录制 |
| 🔇 静音 | 停止当前语音朗读 |
| 🔄 重置 | 清空对话历史，重新开始 |
| ⚙ 设置 | 打开设置面板 |

### 设置项

- **语音识别语言** — 语音输入的识别语言（中文/英文/日文/韩文）
- **语音合成声音** — AI 朗读时使用的声音（取决于系统可用语音）
- **语速** — 朗读速度（0.5x ~ 2.0x）
- **音调** — 朗读音调（0.5 ~ 2.0）
- **自动朗读回复** — 是否自动朗读 AI 的回复

## 项目结构

```
hermes-voice-chat/
├── server.py          # FastAPI 后端服务
└── static/
    └── index.html     # 前端页面（HTML + CSS + JS）
```

### 后端 (server.py)

- 读取 `~/.hermes/config.yaml` 获取 API 配置
- 通过 WebSocket 与前端通信
- 使用 OpenRouter API 流式调用大语言模型
- 自动将 Hermes 配置的模型和 API Key 传递给请求

### 前端 (index.html)

- 使用 **Web Speech API** 实现语音识别（STT）和语音合成（TTS）
- 通过 WebSocket 与后端实时通信
- 支持流式显示 AI 回复
- 暗色主题 UI，适配移动端

## 技术栈

- **后端**: Python 3.11+, FastAPI, Uvicorn, WebSocket
- **前端**: HTML5, CSS3, JavaScript (原生)
- **语音**: Web Speech API (SpeechRecognition + SpeechSynthesis)
- **AI**: OpenRouter API (兼容 OpenAI SDK 格式)

## 常见问题

### Q: 点击麦克风没反应？

确保：
1. 使用 Chrome 浏览器
2. 页面地址是 `http://localhost:8765`（不是 `0.0.0.0` 或 IP 地址）
3. 已允许浏览器访问麦克风

### Q: 语音识别不准？

1. 在设置中选择正确的识别语言
2. 尽量在安静环境下使用
3. 说话清晰，语速适中

### Q: AI 语音朗读声音不好？

1. 在设置中切换不同的语音合成声音
2. macOS 系统可以在"系统设置 → 辅助功能 → 语音"中下载更多声音
3. 调整语速和音调找到舒适的听感

### Q: 连接断开 / 报错？

1. 检查后端服务是否在运行
2. 确认 `~/.hermes/config.yaml` 中 API Key 有效
3. 查看终端中的错误日志

### Q: SSL 证书错误？

macOS 上的 Python 可能缺少根证书，已在代码中禁用 SSL 验证。
如需修复根本问题，运行：

```bash
/Applications/Python\ 3.12/Install\ Certificates.command
```

## 许可证

MIT
