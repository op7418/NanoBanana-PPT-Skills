#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI 客户端模块
用于调用 ComfyUI 的工作流生成图片

功能：
- 支持加载和修改工作流 JSON
- 支持提交工作流到 ComfyUI 队列
- 支持轮询获取生成结果
- 自动下载生成的图片

参考: agent-kaichi/scripts/comfyUIClient.js
"""

import os
import sys
import json
import time
import uuid
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# 设置标准输出编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def load_env_file(env_path='.env'):
    """加载 .env 文件到环境变量"""
    env_file = Path(env_path)
    if not env_file.exists():
        # 尝试在项目根目录查找
        project_root = Path(__file__).parent.parent.parent.parent
        env_file = project_root / '.env'
        if not env_file.exists():
            return
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # 如果环境变量不存在，则设置它（.env 文件的优先级低于系统环境变量）
                    if key and key not in os.environ:
                        os.environ[key] = value
    except Exception as e:
        print(f"警告: 加载 .env 文件失败: {e}")


# 在导入其他模块前加载 .env 文件
load_env_file()


class ComfyUIClient:
    """ComfyUI API 客户端"""
    
    # 默认节点 ID (基于 z_image_turbo 工作流)
    DEFAULT_PROMPT_NODE = "45"  # CLIPTextEncode
    DEFAULT_SIZE_NODE = "41"    # EmptySD3LatentImage
    
    # 非执行节点类型（不需要转换）
    NON_EXECUTABLE_TYPES = ["MarkdownNote", "Note", "NoteText"]
    
    # Widget 值映射表（GUI 格式到 API 格式）
    WIDGET_MAPPINGS = {
        "KSampler": {
            "values": ["seed", "_control_after_generate", "steps", "cfg", "sampler_name", "scheduler", "denoise"],
            "skip_fields": ["_control_after_generate"]
        },
        "KSamplerAdvanced": {
            "values": ["add_noise", "noise_seed", "_control_after_generate", "steps", "cfg", "sampler_name", "scheduler", "start_at_step", "end_at_step", "return_with_leftover_noise"],
            "skip_fields": ["_control_after_generate"]
        },
        "CLIPTextEncode": {
            "values": ["text"]
        },
        "EmptySD3LatentImage": {
            "values": ["width", "height", "batch_size"]
        },
        "EmptyLatentImage": {
            "values": ["width", "height", "batch_size"]
        },
        "CLIPLoader": {
            "values": ["clip_name", "type", "device"]
        },
        "VAELoader": {
            "values": ["vae_name"]
        },
        "UNETLoader": {
            "values": ["unet_name", "weight_dtype"]
        },
        "CheckpointLoaderSimple": {
            "values": ["ckpt_name"]
        },
        "SaveImage": {
            "values": ["filename_prefix"]
        },
        "ModelSamplingAuraFlow": {
            "values": ["shift"]
        },
        "ConditioningZeroOut": {
            "values": []
        },
        "VAEDecode": {
            "values": []
        }
    }

    def __init__(
        self,
        server_url: str = None,
        workflow_file: str = None,
        output_dir: str = None,
        prompt_node: str = None,
        size_node: str = None,
        timeout: int = 600,
        poll_interval: float = 1.0
    ):
        """
        初始化 ComfyUI 客户端
        
        Args:
            server_url: ComfyUI 服务器地址
            workflow_file: 工作流 JSON 文件路径
            output_dir: 输出目录
            prompt_node: Prompt 节点 ID
            size_node: 尺寸节点 ID
            timeout: 超时时间（秒）
            poll_interval: 轮询间隔（秒）
        """
        self.server_url = server_url or os.environ.get("COMFYUI_SERVER_URL", "http://127.0.0.1:8188")
        self.workflow_file = workflow_file
        self.output_dir = output_dir or "./outputs"
        self.prompt_node = prompt_node or self.DEFAULT_PROMPT_NODE
        self.size_node = size_node or self.DEFAULT_SIZE_NODE
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.client_id = self._generate_client_id()
        
        # 加载工作流
        self.workflow = None
        if self.workflow_file:
            self.workflow = self._load_workflow(self.workflow_file)
    
    def _generate_client_id(self) -> str:
        """生成唯一的客户端 ID"""
        return f"ppt_gen_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def _load_workflow(self, workflow_file: str) -> dict:
        """加载工作流 JSON 文件"""
        with open(workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _http_request(
        self,
        url: str,
        method: str = "GET",
        data: dict = None,
        timeout: int = 30
    ) -> Tuple[int, Any]:
        """
        发送 HTTP 请求
        
        Returns:
            (status_code, response_data)
        """
        headers = {"Content-Type": "application/json"}
        
        if data is not None:
            data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                try:
                    return status_code, json.loads(response_data)
                except json.JSONDecodeError:
                    return status_code, response_data
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode('utf-8')
        except urllib.error.URLError as e:
            raise ConnectionError(f"无法连接到 ComfyUI 服务器: {e.reason}")
    
    def _download_file(self, url: str, output_path: str) -> str:
        """下载文件到指定路径"""
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            urllib.request.urlretrieve(url, output_path)
            return output_path
        except Exception as e:
            raise RuntimeError(f"下载文件失败: {e}")
    
    def convert_workflow_to_api_format(self, workflow: dict) -> dict:
        """
        转换 ComfyUI GUI 格式为 API 格式
        
        GUI 格式包含 nodes 数组和 links 数组
        API 格式以节点 ID 为 key
        """
        # 检查是否已经是 API 格式
        if "nodes" not in workflow:
            # 检查第一个 key 是否是数字（节点 ID）
            first_key = next(iter(workflow.keys()), None)
            if first_key and first_key.isdigit():
                print("✅ 工作流已经是 API 格式")
                return workflow
        
        # 如果是 GUI 格式（包含 nodes 数组），需要转换
        if "nodes" not in workflow or not isinstance(workflow.get("nodes"), list):
            print("⚠️  无法识别工作流格式，使用原格式")
            return workflow
        
        print("🔄 转换工作流格式：从 GUI 格式转换为 API 格式...")
        
        api_workflow = {}
        nodes = workflow["nodes"]
        links = workflow.get("links", [])
        
        for node in nodes:
            # 跳过非执行节点
            if node.get("type") in self.NON_EXECUTABLE_TYPES:
                print(f"⏭️  跳过非执行节点: {node['type']} (ID: {node['id']})")
                continue
            
            node_id = str(node["id"])
            node_data = {
                "class_type": node["type"],
                "inputs": {}
            }
            
            # 处理输入连接
            if node.get("inputs"):
                for inp in node["inputs"]:
                    if inp.get("link") is not None:
                        # 查找对应的 link
                        # links 格式: [linkId, sourceNodeId, sourceSlot, targetNodeId, targetSlot, dataType]
                        link = next(
                            (l for l in links if l[0] == inp["link"] and l[3] == node["id"]),
                            None
                        )
                        if link:
                            source_node_id, source_slot = str(link[1]), link[2]
                            node_data["inputs"][inp["name"]] = [source_node_id, source_slot]
            
            # 处理 widgets_values
            if node.get("widgets_values"):
                self._map_widget_values(node, node_data)
            
            api_workflow[node_id] = node_data
        
        # 清理和修复特殊值
        self._cleanup_workflow_values(api_workflow)
        
        print(f"✅ 已转换 {len(api_workflow)} 个节点")
        return api_workflow
    
    def _map_widget_values(self, node: dict, node_data: dict):
        """映射 widget values 到节点输入"""
        widgets_values = node.get("widgets_values", [])
        node_type = node.get("type", "")
        
        mapping = self.WIDGET_MAPPINGS.get(node_type)
        
        if mapping:
            skip_fields = mapping.get("skip_fields", [])
            value_index = 0
            
            for field_name in mapping.get("values", []):
                if value_index >= len(widgets_values):
                    break
                
                if field_name in skip_fields or field_name.startswith("_"):
                    value_index += 1
                    continue
                
                node_data["inputs"][field_name] = widgets_values[value_index]
                value_index += 1
        else:
            # 对于未知节点类型，尝试基于 inputs 定义的方法
            if node.get("inputs"):
                widget_index = 0
                for inp in node["inputs"]:
                    if inp.get("link") is None and inp.get("widget"):
                        if widget_index < len(widgets_values):
                            node_data["inputs"][inp["name"]] = widgets_values[widget_index]
                            widget_index += 1
    
    def _cleanup_workflow_values(self, workflow: dict):
        """清理和修复工作流中的特殊值"""
        for node_id, node_data in workflow.items():
            class_type = node_data.get("class_type", "")
            
            if class_type in ["KSampler", "KSamplerAdvanced"]:
                inputs = node_data.get("inputs", {})
                
                # 处理 steps
                if not isinstance(inputs.get("steps"), (int, float)):
                    inputs["steps"] = 20
                
                # 处理 cfg
                if not isinstance(inputs.get("cfg"), (int, float)):
                    inputs["cfg"] = 7
                
                # 处理 denoise
                if not isinstance(inputs.get("denoise"), (int, float)):
                    inputs["denoise"] = 1.0
                
                # 处理 seed
                if not isinstance(inputs.get("seed"), (int, float)):
                    import random
                    inputs["seed"] = random.randint(0, 2**32 - 1)
    
    def modify_workflow_prompt(self, workflow: dict, node_id: str, prompt_text: str) -> dict:
        """修改工作流中的 prompt 节点"""
        if not node_id or not prompt_text:
            return workflow
        
        node_id_str = str(node_id)
        
        print(f"📝 修改节点 {node_id_str} 的 prompt...")
        
        if node_id_str in workflow and "inputs" in workflow[node_id_str]:
            # 查找可能的 prompt 字段
            prompt_fields = ["text", "prompt", "positive", "negative"]
            modified = False
            
            for field in prompt_fields:
                if field in workflow[node_id_str]["inputs"]:
                    workflow[node_id_str]["inputs"][field] = prompt_text
                    modified = True
                    print(f"✅ 已更新字段 \"{field}\"")
                    break
            
            if not modified:
                # 如果没有找到标准字段，直接设置 text
                workflow[node_id_str]["inputs"]["text"] = prompt_text
                print(f"✅ 已添加新字段 \"text\"")
        else:
            print(f"⚠️  节点 {node_id_str} 不存在或没有 inputs")
            print(f"   可用节点: {', '.join(workflow.keys())}")
        
        return workflow
    
    def modify_workflow_size(self, workflow: dict, node_id: str, width: int, height: int) -> dict:
        """修改工作流中的尺寸节点"""
        if not node_id:
            return workflow
        
        node_id_str = str(node_id)
        
        print(f"📐 修改节点 {node_id_str} 的尺寸为 {width}x{height}...")
        
        if node_id_str in workflow and "inputs" in workflow[node_id_str]:
            workflow[node_id_str]["inputs"]["width"] = width
            workflow[node_id_str]["inputs"]["height"] = height
            print(f"✅ 已更新尺寸")
        else:
            print(f"⚠️  节点 {node_id_str} 不存在或没有 inputs")
        
        return workflow
    
    def queue_prompt(self, workflow: dict) -> str:
        """提交工作流到 ComfyUI 队列"""
        print("\n📤 提交工作流到队列...")
        
        url = f"{self.server_url}/prompt"
        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }
        
        status_code, response = self._http_request(url, method="POST", data=payload)
        
        if status_code != 200:
            raise RuntimeError(f"API 返回错误: {status_code} - {response}")
        
        if isinstance(response, dict) and "error" in response:
            raise RuntimeError(f"工作流错误: {response['error']}")
        
        prompt_id = response.get("prompt_id")
        print(f"✅ 工作流已提交，Prompt ID: {prompt_id}")
        
        return prompt_id
    
    def get_history(self, prompt_id: str = None) -> dict:
        """获取历史记录"""
        url = f"{self.server_url}/history/{prompt_id or ''}"
        status_code, response = self._http_request(url)
        
        if status_code != 200:
            raise RuntimeError(f"获取历史失败: {status_code}")
        
        return response
    
    def get_queue_status(self) -> dict:
        """查询队列状态"""
        url = f"{self.server_url}/queue"
        status_code, response = self._http_request(url)
        
        if status_code != 200:
            raise RuntimeError(f"查询队列失败: {status_code}")
        
        return response
    
    def wait_for_completion(self, prompt_id: str) -> dict:
        """等待任务完成"""
        print("\n⏳ 等待任务完成...")
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < self.timeout:
            try:
                # 检查历史记录
                history = self.get_history(prompt_id)
                
                if prompt_id in history:
                    prompt_data = history[prompt_id]
                    
                    # 检查是否完成
                    if prompt_data.get("status", {}).get("completed"):
                        print("✅ 任务已完成")
                        return prompt_data
                    
                    # 检查是否有输出
                    if prompt_data.get("outputs"):
                        print("✅ 检测到输出，任务完成")
                        return prompt_data
                
                # 检查队列状态
                queue_status = self.get_queue_status()
                current_status = json.dumps(queue_status)
                
                if current_status != last_status:
                    running = len(queue_status.get("queue_running", []))
                    pending = len(queue_status.get("queue_pending", []))
                    print(f"📊 队列状态: 运行中={running}, 等待中={pending}")
                    last_status = current_status
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"⚠️  轮询错误: {e}")
                time.sleep(self.poll_interval)
        
        raise TimeoutError(f"任务超时 ({self.timeout}秒)")
    
    def download_outputs(self, history: dict, output_path: str) -> str:
        """下载生成的图片"""
        print("\n📥 获取生成结果...")
        
        for prompt_id, prompt_data in history.items():
            if not prompt_data.get("outputs"):
                continue
            
            for node_id, node_output in prompt_data["outputs"].items():
                if not node_output.get("images"):
                    continue
                
                for image in node_output["images"]:
                    filename = image.get("filename")
                    subfolder = image.get("subfolder", "")
                    img_type = image.get("type", "output")
                    
                    # 构建下载 URL
                    params = urllib.parse.urlencode({
                        "filename": filename,
                        "subfolder": subfolder,
                        "type": img_type
                    })
                    view_url = f"{self.server_url}/view?{params}"
                    
                    print(f"⬇️  下载: {filename}")
                    
                    try:
                        self._download_file(view_url, output_path)
                        print(f"✅ 已保存: {output_path}")
                        return output_path
                    except Exception as e:
                        print(f"❌ 下载失败 {filename}: {e}")
        
        return None
    
    def generate_image(
        self,
        prompt: str,
        output_path: str,
        width: int = 1920,
        height: int = 1080,
        workflow: dict = None
    ) -> Optional[str]:
        """
        完整的图片生成流程
        
        Args:
            prompt: 图片生成提示词
            output_path: 输出文件路径
            width: 图片宽度
            height: 图片高度
            workflow: 可选的工作流（不提供则使用初始化时加载的）
        
        Returns:
            生成的图片路径，失败返回 None
        """
        try:
            # 使用提供的工作流或默认工作流
            wf = workflow or self.workflow
            if not wf:
                raise ValueError("未提供工作流")
            
            # 深拷贝工作流
            wf = json.loads(json.dumps(wf))
            
            # 转换为 API 格式
            wf = self.convert_workflow_to_api_format(wf)
            
            # 修改 prompt
            wf = self.modify_workflow_prompt(wf, self.prompt_node, prompt)
            
            # 修改尺寸
            wf = self.modify_workflow_size(wf, self.size_node, width, height)
            
            # 提交工作流
            prompt_id = self.queue_prompt(wf)
            
            # 等待完成
            result = self.wait_for_completion(prompt_id)
            
            # 获取完整历史记录
            history = self.get_history(prompt_id)
            
            # 下载输出
            downloaded_path = self.download_outputs(history, output_path)
            
            if downloaded_path:
                print(f"\n🎉 图片生成成功: {downloaded_path}")
                return downloaded_path
            else:
                print("\n❌ 未找到生成的图片")
                return None
            
        except Exception as e:
            print(f"\n❌ 图片生成失败: {e}")
            return None


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ComfyUI 客户端 - 调用 ComfyUI 生成图片',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--workflow', '-w',
        required=True,
        help='工作流 JSON 文件路径'
    )
    parser.add_argument(
        '--prompt', '-p',
        required=True,
        help='生成提示词'
    )
    parser.add_argument(
        '--output', '-o',
        default='./output.png',
        help='输出文件路径 (默认: ./output.png)'
    )
    parser.add_argument(
        '--server', '-s',
        default='http://127.0.0.1:8188',
        help='ComfyUI 服务器地址 (默认: http://127.0.0.1:8188)'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=1920,
        help='图片宽度 (默认: 1920)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=1080,
        help='图片高度 (默认: 1080)'
    )
    parser.add_argument(
        '--prompt-node',
        default='45',
        help='Prompt 节点 ID (默认: 45)'
    )
    parser.add_argument(
        '--size-node',
        default='41',
        help='尺寸节点 ID (默认: 41)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=600,
        help='超时时间，秒 (默认: 600)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ComfyUI 客户端")
    print("=" * 60)
    print(f"服务器: {args.server}")
    print(f"工作流: {args.workflow}")
    print(f"尺寸: {args.width}x{args.height}")
    print(f"输出: {args.output}")
    print("=" * 60)
    
    client = ComfyUIClient(
        server_url=args.server,
        workflow_file=args.workflow,
        prompt_node=args.prompt_node,
        size_node=args.size_node,
        timeout=args.timeout
    )
    
    result = client.generate_image(
        prompt=args.prompt,
        output_path=args.output,
        width=args.width,
        height=args.height
    )
    
    if result:
        print(f"\n✅ 完成！图片已保存到: {result}")
        sys.exit(0)
    else:
        print("\n❌ 生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
