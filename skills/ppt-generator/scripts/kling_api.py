#!/usr/bin/env python3
"""
可灵（Kling）视频生成 API 封装
支持图生视频（首尾帧控制）功能
"""

import os
import time
import jwt
import requests
import base64
from typing import Optional, Dict, Any
from pathlib import Path


class KlingVideoGenerator:
    """可灵视频生成器"""

    # API基础配置
    API_BASE_URL = "https://api-beijing.klingai.com"
    API_CREATE_TASK = "/v1/videos/image2video"
    API_QUERY_TASK = "/v1/videos/image2video/{task_id}"

    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        初始化可灵API客户端

        Args:
            access_key: 访问密钥（如果不提供，从环境变量读取）
            secret_key: 密钥（如果不提供，从环境变量读取）
        """
        # 从环境变量读取密钥
        self.access_key = access_key or os.environ.get("Kling_Access_Key")
        self.secret_key = secret_key or os.environ.get("Kling_Secret_Key")

        if not self.access_key or not self.secret_key:
            raise ValueError(
                "❌ 可灵API密钥未配置！\n"
                "请在.env文件中配置：\n"
                "  Kling_Access_Key=your-access-key\n"
                "  Kling_Secret_Key=your-secret-key"
            )

        print(f"✅ 可灵API客户端初始化成功")
        print(f"   Access Key: {self.access_key[:8]}...{self.access_key[-4:]}")

    def generate_jwt_token(self, expire_seconds: int = 1800) -> str:
        """
        生成JWT Token用于API鉴权

        Args:
            expire_seconds: Token有效期（秒），默认1800秒（30分钟）

        Returns:
            jwt_token: 生成的Token字符串
        """
        current_time = int(time.time())

        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }

        payload = {
            "iss": self.access_key,
            "exp": current_time + expire_seconds,  # 过期时间
            "nbf": current_time - 5  # 开始生效时间（当前时间-5秒）
        }

        token = jwt.encode(payload, self.secret_key, headers=headers)
        return token

    def _get_auth_header(self) -> Dict[str, str]:
        """获取认证请求头"""
        token = self.generate_jwt_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _image_to_base64(self, image_path: str) -> str:
        """
        将图片转换为Base64编码（不带data:前缀）

        Args:
            image_path: 图片路径

        Returns:
            base64_str: Base64编码字符串
        """
        with open(image_path, 'rb') as f:
            image_data = f.read()

        base64_str = base64.b64encode(image_data).decode('utf-8')
        return base64_str

    def create_video_task(
        self,
        image_start: str,
        image_end: Optional[str] = None,
        prompt: str = "",
        model_name: str = "kling-v2-6",
        duration: str = "5",
        mode: str = "std",
        cfg_scale: float = 0.5,
        negative_prompt: str = "",
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建图生视频任务

        Args:
            image_start: 起始帧图片路径或Base64编码
            image_end: 结束帧图片路径或Base64编码（可选）
            prompt: 正向提示词（转场描述）
            model_name: 模型名称，默认kling-v2-6
            duration: 视频时长，5或10秒
            mode: 生成模式，std（标准）或pro（高品质）
            cfg_scale: 自由度，0-1，值越大与提示词相关性越强
            negative_prompt: 负向提示词
            callback_url: 回调URL（可选）

        Returns:
            response_data: API响应数据
        """
        # 处理图片（如果是路径，转换为Base64）
        if os.path.exists(image_start):
            image_start_b64 = self._image_to_base64(image_start)
            print(f"📷 起始帧已转换为Base64: {Path(image_start).name}")
        else:
            image_start_b64 = image_start

        # 构建请求体
        request_body = {
            "model_name": model_name,
            "image": image_start_b64,
            "duration": duration,
            "mode": mode
        }

        # 如果提供了结束帧
        if image_end:
            if os.path.exists(image_end):
                image_end_b64 = self._image_to_base64(image_end)
                print(f"📷 结束帧已转换为Base64: {Path(image_end).name}")
            else:
                image_end_b64 = image_end

            request_body["image_tail"] = image_end_b64

        # 添加提示词
        if prompt:
            request_body["prompt"] = prompt

        if negative_prompt:
            request_body["negative_prompt"] = negative_prompt

        # V2.x模型不支持cfg_scale，只在V1.x中添加
        if not model_name.startswith("kling-v2"):
            request_body["cfg_scale"] = cfg_scale

        if callback_url:
            request_body["callback_url"] = callback_url

        # 发送请求
        url = f"{self.API_BASE_URL}{self.API_CREATE_TASK}"
        headers = self._get_auth_header()

        print(f"🚀 正在创建视频生成任务...")
        print(f"   模型: {model_name}")
        print(f"   模式: {mode}")
        print(f"   时长: {duration}秒")
        if image_end:
            print(f"   类型: 首尾帧过渡视频")
        else:
            print(f"   类型: 单帧动效视频")

        response = requests.post(url, json=request_body, headers=headers)

        if response.status_code != 200:
            raise Exception(
                f"❌ 创建任务失败！\n"
                f"   状态码: {response.status_code}\n"
                f"   响应: {response.text}"
            )

        result = response.json()

        if result.get("code") != 0:
            raise Exception(
                f"❌ 创建任务失败！\n"
                f"   错误码: {result.get('code')}\n"
                f"   错误信息: {result.get('message')}"
            )

        task_id = result["data"]["task_id"]
        task_status = result["data"]["task_status"]

        print(f"✅ 任务创建成功！")
        print(f"   任务ID: {task_id}")
        print(f"   状态: {task_status}")

        return result["data"]

    def query_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            task_data: 任务数据
        """
        url = f"{self.API_BASE_URL}{self.API_QUERY_TASK.format(task_id=task_id)}"
        headers = self._get_auth_header()

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(
                f"❌ 查询任务失败！\n"
                f"   状态码: {response.status_code}\n"
                f"   响应: {response.text}"
            )

        result = response.json()

        if result.get("code") != 0:
            raise Exception(
                f"❌ 查询任务失败！\n"
                f"   错误码: {result.get('code')}\n"
                f"   错误信息: {result.get('message')}"
            )

        return result["data"]

    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        等待任务完成（轮询）

        Args:
            task_id: 任务ID
            timeout: 超时时间（秒），默认300秒（5分钟）
            poll_interval: 轮询间隔（秒），默认5秒

        Returns:
            task_result: 任务结果
        """
        start_time = time.time()
        print(f"⏳ 等待任务完成（任务ID: {task_id}）...")

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > timeout:
                raise TimeoutError(
                    f"❌ 任务超时！已等待 {elapsed} 秒\n"
                    f"   任务ID: {task_id}"
                )

            task_data = self.query_task_status(task_id)
            status = task_data["task_status"]

            # 状态说明：submitted（已提交）、processing（处理中）、succeed（成功）、failed（失败）
            if status == "succeed":
                print(f"✅ 任务完成！耗时: {elapsed}秒")
                return task_data

            elif status == "failed":
                error_msg = task_data.get("task_status_msg", "未知错误")
                raise Exception(
                    f"❌ 任务失败！\n"
                    f"   任务ID: {task_id}\n"
                    f"   失败原因: {error_msg}"
                )

            elif status in ["submitted", "processing"]:
                print(f"   [{elapsed}s] 状态: {status}，继续等待...")
                time.sleep(poll_interval)

            else:
                raise Exception(f"❌ 未知任务状态: {status}")

    def download_video(self, video_url: str, save_path: str) -> str:
        """
        下载生成的视频

        Args:
            video_url: 视频URL
            save_path: 保存路径

        Returns:
            save_path: 实际保存路径
        """
        print(f"⬇️  正在下载视频...")
        print(f"   URL: {video_url}")
        print(f"   保存到: {save_path}")

        # 创建目录
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # 下载视频
        response = requests.get(video_url, stream=True)

        if response.status_code != 200:
            raise Exception(
                f"❌ 下载视频失败！\n"
                f"   状态码: {response.status_code}"
            )

        # 写入文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = os.path.getsize(save_path)
        file_size_mb = file_size / (1024 * 1024)

        print(f"✅ 视频下载完成！")
        print(f"   文件大小: {file_size_mb:.2f} MB")

        return save_path

    def generate_and_download(
        self,
        image_start: str,
        image_end: Optional[str],
        prompt: str,
        output_path: str,
        **kwargs
    ) -> str:
        """
        一键生成并下载视频（完整流程）

        Args:
            image_start: 起始帧图片路径
            image_end: 结束帧图片路径（可选）
            prompt: 提示词
            output_path: 输出路径
            **kwargs: 其他参数（model_name, duration, mode等）

        Returns:
            output_path: 视频保存路径
        """
        # 1. 创建任务
        task_data = self.create_video_task(
            image_start=image_start,
            image_end=image_end,
            prompt=prompt,
            **kwargs
        )

        task_id = task_data["task_id"]

        # 2. 等待完成
        result_data = self.wait_for_completion(task_id)

        # 3. 获取视频URL
        videos = result_data.get("task_result", {}).get("videos", [])
        if not videos:
            raise Exception("❌ 任务完成但未返回视频结果")

        video_url = videos[0]["url"]

        # 4. 下载视频
        self.download_video(video_url, output_path)

        return output_path


if __name__ == "__main__":
    """测试代码"""
    # 从环境变量加载
    generator = KlingVideoGenerator()

    # 测试JWT Token生成
    token = generator.generate_jwt_token()
    print(f"\n生成的JWT Token: {token[:50]}...")
