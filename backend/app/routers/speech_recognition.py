"""
语音识别路由（阿里云 RESTful ASR）

提供一个接口接收前端上传的音频（二进制PCM/WAV），
调用阿里云的 RESTful API 进行识别并返回文本结果。
"""

import os
import json
import http.client
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query


router = APIRouter()


def build_asr_request_path(
    app_key: str,
    format: str = "pcm",
    sample_rate: int = 16000,
    enable_punctuation_prediction: bool = True,
    enable_inverse_text_normalization: bool = True,
    enable_voice_detection: bool = False,
) -> str:
    """构建阿里云ASR RESTful请求路径（不含host）。

    返回形如：/stream/v1/asr?appkey=xxx&format=pcm&sample_rate=16000&...
    """
    base_path = "/stream/v1/asr"
    params = [
        f"appkey={app_key}",
        f"format={format}",
        f"sample_rate={sample_rate}",
    ]
    if enable_punctuation_prediction:
        params.append("enable_punctuation_prediction=true")
    if enable_inverse_text_normalization:
        params.append("enable_inverse_text_normalization=true")
    if enable_voice_detection:
        params.append("enable_voice_detection=true")

    return base_path + "?" + "&".join(params)


def aliyun_asr_recognize(
    token: str,
    host: str,
    request_path: str,
    audio_bytes: bytes,
):
    """调用阿里云 ASR RESTful 接口，返回解析后的JSON。

    若识别成功，返回包含status、result等字段的JSON；失败抛出异常。
    """
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
            # 返回格式异常
            raise HTTPException(status_code=502, detail="ASR响应非JSON格式")

        return {
            "http_status": response.status,
            "http_reason": response.reason,
            "data": data,
        }
    finally:
        conn.close()


@router.post("/recognize")
async def recognize_speech(
    file: UploadFile = File(..., description="上传的音频文件，建议16k采样率PCM或WAV"),
    format: str = Query("pcm", description="音频格式：pcm或wav，默认pcm"),
    sample_rate: int = Query(16000, description="采样率，默认16000"),
    enable_punctuation_prediction: bool = Query(True, description="是否启用标点预测"),
    enable_inverse_text_normalization: bool = Query(True, description="是否启用ITN反标准化"),
    enable_voice_detection: bool = Query(False, description="是否启用断句语音检测"),
):
    """接收音频文件并返回识别文本。

    环境变量：
    - ALIYUN_APP_KEY：项目AppKey
    - ALIYUN_TOKEN：服务鉴权Token（通过 acquiretoken.py 获取）
    - ALIYUN_ASR_ENDPOINT（可选）：默认 https://nls-gateway-cn-shanghai.aliyuncs.com
    """

    app_key = os.getenv("ALIYUN_APP_KEY")
    token = os.getenv("ALIYUN_TOKEN")
    endpoint = os.getenv("ALIYUN_ASR_ENDPOINT", "https://nls-gateway-cn-shanghai.aliyuncs.com")

    if not app_key:
        raise HTTPException(status_code=500, detail="环境变量缺失：ALIYUN_APP_KEY")
    if not token:
        raise HTTPException(status_code=500, detail="环境变量缺失：ALIYUN_TOKEN")

    # 解析host（http.client需要host与path分离）
    if not endpoint.startswith("https://"):
        raise HTTPException(status_code=500, detail="ALIYUN_ASR_ENDPOINT 必须以 https:// 开头")

    host = endpoint.replace("https://", "")
    # 构建请求路径
    request_path = build_asr_request_path(
        app_key=app_key,
        format=format,
        sample_rate=sample_rate,
        enable_punctuation_prediction=enable_punctuation_prediction,
        enable_inverse_text_normalization=enable_inverse_text_normalization,
        enable_voice_detection=enable_voice_detection,
    )

    # 读取音频二进制
    try:
        audio_bytes = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="无法读取上传的音频文件")

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="音频数据为空")

    # 调用阿里云ASR
    try:
        result = aliyun_asr_recognize(
            token=token,
            host=host,
            request_path=request_path,
            audio_bytes=audio_bytes,
        )
    except HTTPException:
        # 透传HTTP异常
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"调用ASR失败: {str(e)}")

    data = result.get("data", {})
    status_code = data.get("status")

    if status_code == 20000000:
        recognized_text = data.get("result", "")
        return {
            "success": True,
            "recognized_text": recognized_text,
            "raw": data,
        }
    else:
        # 识别失败，返回错误详情
        return {
            "success": False,
            "error": data,
        }