import os
import base64
import requests
from datetime import datetime
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def generate_image(prompt: str, size: str = "1024x1024", style: str = "natural") -> str:
    """
    使用MiniMax图像生成模型生成图片

    Args:
        prompt: 图片生成描述提示词
        size: 图片尺寸，支持 "512x512", "768x768", "1024x1024", "1536x1536"
        style: 风格类型，"natural" 或 "vivid"

    Returns:
        生成的图片保存路径或base64编码的图像数据
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return "错误: 未找到API密钥"

    url = "https://api.minimax.chat/v1/images/generations"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "image-01",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "style": style
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()

        if "data" in result and len(result["data"]) > 0:
            image_data = result["data"][0]

            # 保存图片
            images_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
            os.makedirs(images_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.png"
            filepath = os.path.join(images_dir, filename)

            if "b64_json" in image_data:
                # Base64编码的图片
                img_data = base64.b64decode(image_data["b64_json"])
                with open(filepath, 'wb') as f:
                    f.write(img_data)
            elif "url" in image_data:
                # URL形式的图片，下载保存
                img_response = requests.get(image_data["url"], timeout=30)
                img_response.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
            else:
                return f"警告: 响应中未找到图片数据 - {result}"

            return f"图片已生成并保存至: {filepath}"
        else:
            return f"错误: 未能生成图片 - {result}"

    except requests.exceptions.Timeout:
        return "错误: 图片生成请求超时，请稍后重试"
    except requests.exceptions.RequestException as e:
        return f"错误: 请求失败 - {str(e)}"
    except Exception as e:
        return f"错误: {str(e)}"

@tool
def edit_image(image_path: str, prompt: str, mask: str = None) -> str:
    """
    编辑现有图片（局部重绘）

    Args:
        image_path: 原始图片路径
        prompt: 编辑提示词
        mask: 蒙版图片路径（可选，白色区域将被重新生成）

    Returns:
        编辑后的图片保存路径
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return "错误: 未找到API密钥"

    url = "https://api.minimax.chat/v1/images/edits"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()

        files = {
            "image": ("image.png", image_data, "image/png"),
        }

        data = {"prompt": prompt, "n": 1}

        if mask:
            with open(mask, 'rb') as f:
                mask_data = f.read()
            files["mask"] = ("mask.png", mask_data, "image/png")

        response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        response.raise_for_status()
        result = response.json()

        if "data" in result and len(result["data"]) > 0:
            image_url = result["data"][0].get("url", "")

            images_dir = os.path.join(os.path.dirname(__file__), '..', 'images', 'edited')
            os.makedirs(images_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"edited_{timestamp}.png"
            filepath = os.path.join(images_dir, filename)

            if image_url:
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)

            return f"图片已编辑并保存至: {filepath}"

        return f"错误: 未能编辑图片 - {result}"

    except FileNotFoundError:
        return f"错误: 找不到图片文件 {image_path}"
    except requests.exceptions.RequestException as e:
        return f"错误: 请求失败 - {str(e)}"
    except Exception as e:
        return f"错误: {str(e)}"