"""
通用辅助函数

提供项目中使用的各种工具函数：
- 文件系统操作
- 字符串处理
- 时间格式化
- 数据验证
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建

    Args:
        path: 目录路径

    Returns:
        Path: 目录路径对象
    """
    path_obj = Path(path)

    try:
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
            print(f"📁 已创建目录: {path_obj.absolute()}")
        return path_obj
    except Exception as e:
        print(f"❌ 创建目录失败 {path}: {e}")
        # 如果创建失败，尝试使用当前目录
        fallback_path = Path.cwd() / "tavily_results"
        fallback_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 使用备用目录: {fallback_path.absolute()}")
        return fallback_path


def clean_filename(filename: str, max_length: int = 50) -> str:
    """
    清理文件名，移除不安全字符

    Args:
        filename: 原始文件名
        max_length: 最大长度

    Returns:
        清理后的文件名
    """
    if not filename:
        return "unnamed"

    # 移除或替换不安全字符
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", filename)
    cleaned = re.sub(r"[^\w\-_. ]", "", cleaned)
    cleaned = re.sub(r"\s+", "_", cleaned.strip())

    # 移除连续的下划线
    cleaned = re.sub(r"_+", "_", cleaned)

    # 限制长度
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip("_")

    # 确保不为空
    if not cleaned:
        cleaned = "unnamed"

    return cleaned


def format_timestamp(dt: Optional[datetime] = None, format_type: str = "filename") -> str:
    """
    格式化时间戳

    Args:
        dt: 日期时间对象，默认为当前时间
        format_type: 格式类型 ("filename", "display", "iso")

    Returns:
        格式化的时间字符串
    """
    if dt is None:
        dt = datetime.now()

    if format_type == "filename":
        return dt.strftime("%Y%m%d_%H%M%S")
    elif format_type == "display":
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "iso":
        return dt.isoformat()
    else:
        return dt.strftime("%Y%m%d_%H%M%S")


def safe_json_load(filepath: Union[str, Path], default: Any = None) -> Any:
    """
    安全地加载JSON文件

    Args:
        filepath: JSON文件路径
        default: 加载失败时的默认值

    Returns:
        JSON数据或默认值
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  文件不存在: {filepath}")
        return default
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return default
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return default


def safe_json_save(
    data: Any, filepath: Union[str, Path], indent: int = 2, ensure_ascii: bool = False
) -> bool:
    """
    安全地保存JSON文件

    Args:
        data: 要保存的数据
        filepath: 保存路径
        indent: 缩进空格数
        ensure_ascii: 是否确保ASCII编码

    Returns:
        是否保存成功
    """
    try:
        # 确保目录存在
        ensure_directory(Path(filepath).parent)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

        print(f"✅ JSON文件已保存: {filepath}")
        return True

    except Exception as e:
        print(f"❌ 保存JSON文件失败: {e}")
        return False


def validate_url(url: str) -> bool:
    """
    验证URL格式是否正确

    Args:
        url: 要验证的URL

    Returns:
        是否为有效URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本到指定长度

    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        格式化的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0

    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def get_file_info(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    获取文件信息

    Args:
        filepath: 文件路径

    Returns:
        文件信息字典
    """
    path_obj = Path(filepath)

    if not path_obj.exists():
        return {"exists": False}

    try:
        stat_info = path_obj.stat()
        return {
            "exists": True,
            "size": stat_info.st_size,
            "size_formatted": format_file_size(stat_info.st_size),
            "created": datetime.fromtimestamp(stat_info.st_ctime),
            "modified": datetime.fromtimestamp(stat_info.st_mtime),
            "is_file": path_obj.is_file(),
            "is_directory": path_obj.is_dir(),
            "extension": path_obj.suffix,
            "name": path_obj.name,
            "parent": str(path_obj.parent),
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}


def sanitize_html(text: str) -> str:
    """
    简单的HTML清理函数

    Args:
        text: 包含HTML的文本

    Returns:
        清理后的文本
    """
    # 移除HTML标签
    clean_text = re.sub(r"<[^>]+>", "", text)

    # 解码HTML实体
    html_entities = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
        "&nbsp;": " ",
    }

    for entity, char in html_entities.items():
        clean_text = clean_text.replace(entity, char)

    return clean_text.strip()


def create_backup_filename(original_path: Union[str, Path]) -> str:
    """
    创建备份文件名

    Args:
        original_path: 原始文件路径

    Returns:
        备份文件名
    """
    path_obj = Path(original_path)
    timestamp = format_timestamp()

    stem = path_obj.stem
    suffix = path_obj.suffix

    return f"{stem}_backup_{timestamp}{suffix}"


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个字典

    Args:
        *dicts: 要合并的字典

    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result
