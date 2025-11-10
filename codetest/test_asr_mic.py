#!/usr/bin/env python3
# coding=utf-8
"""
使用麦克风录音，按下回车结束录音，并调用阿里云 RESTful ASR 接口识别。

环境变量（请在运行前设置）：
- ALIYUN_APP_KEY：项目AppKey
- ALIYUN_TOKEN：服务鉴权Token（可通过 acquiretoken.py 获取）
- ALIYUN_ASR_ENDPOINT（可选）：默认 https://nls-gateway-cn-shanghai.aliyuncs.com

依赖：
- PyAudio（Windows建议使用预编译wheel安装）
"""

import os
import json
import time
import http.client

# 可选：自动加载仓库中的 .env
try:
    from dotenv import load_dotenv
    _env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))
    if os.path.exists(_env_path):
        load_dotenv(_env_path)
    else:
        load_dotenv()
except Exception:
    pass

try:
    import msvcrt  # Windows按键检测
except ImportError:
    msvcrt = None

try:
    import pyaudio
except ImportError:
    print("未安装 PyAudio，请先安装：pip install PyAudio")
    print("如果安装失败，建议搜索并安装匹配你Python版本的预编译wheel。")
    raise


def record_audio_until_enter(sample_rate: int = 16000, channels: int = 1, chunk: int = 1024) -> bytes:
    """录音直到按下回车，返回原始PCM字节（16-bit LE）。"""
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk,
    )

    print("开始录音...（在控制台按下回车结束）")
    frames = []
    start_time = time.time()

    try:
        while True:
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)

            # 监听回车
            if msvcrt and msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch == "\r" or ch == "\n":
                    break
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    duration = time.time() - start_time
    print(f"录音结束，时长约 {duration:.1f} 秒")
    return b"".join(frames)


def build_request_path(app_key: str, sample_rate: int = 16000, fmt: str = "pcm",
                       enable_punc: bool = True, enable_itn: bool = True, enable_vad: bool = False) -> str:
    path = "/stream/v1/asr"
    params = [
        f"appkey={app_key}",
        f"format={fmt}",
        f"sample_rate={sample_rate}",
    ]
    if enable_punc:
        params.append("enable_punctuation_prediction=true")
    if enable_itn:
        params.append("enable_inverse_text_normalization=true")
    if enable_vad:
        params.append("enable_voice_detection=true")
    return path + "?" + "&".join(params)


def aliyun_asr(token: str, host: str, request_path: str, audio_bytes: bytes):
    headers = {
        "X-NLS-Token": token,
        "Content-type": "application/octet-stream",
        "Content-Length": str(len(audio_bytes)),
    }
    conn = http.client.HTTPSConnection(host)
    try:
        conn.request(method="POST", url=request_path, body=audio_bytes, headers=headers)
        response = conn.getresponse()
        body = response.read()
        try:
            data = json.loads(body)
        except ValueError:
            print("响应不是JSON格式：", body[:200])
            raise
        return response.status, response.reason, data
    finally:
        conn.close()


def main():
    app_key = os.getenv("ALIYUN_APP_KEY")
    token = os.getenv("ALIYUN_TOKEN")
    endpoint = os.getenv("ALIYUN_ASR_ENDPOINT", "https://nls-gateway-cn-shanghai.aliyuncs.com")

    if not app_key or not token:
        print("请先设置环境变量 ALIYUN_APP_KEY 与 ALIYUN_TOKEN")
        return
    if not endpoint.startswith("https://"):
        print("ALIYUN_ASR_ENDPOINT 必须以 https:// 开头")
        return

    host = endpoint.replace("https://", "")
    sample_rate = int(os.getenv("ALIYUN_ASR_SAMPLE_RATE", "16000"))
    fmt = os.getenv("ALIYUN_ASR_FORMAT", "pcm")

    # 录音
    audio_bytes = record_audio_until_enter(sample_rate=sample_rate)

    # 构建请求
    request_path = build_request_path(
        app_key=app_key,
        sample_rate=sample_rate,
        fmt=fmt,
        enable_punc=True,
        enable_itn=True,
        enable_vad=False,
    )

    print("发送识别请求...")
    status, reason, data = aliyun_asr(token, host, request_path, audio_bytes)
    print("HTTP状态:", status, reason)
    print("识别响应:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    if data.get("status") == 20000000:
        print("识别结果:", data.get("result", ""))
    else:
        print("识别失败，错误码:", data.get("status"))


if __name__ == "__main__":
    main()