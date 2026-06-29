"""
文件处理工具
提供文件读写、编码检测等功能
"""
from pathlib import Path
from typing import Optional, List
from loguru import logger


class FileHandler:
    def __init__(self):
        self.supported_extensions = {'.md', '.txt', '.rst', '.markdown'}

    def read_file(self, file_path: str) -> Optional[str]:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"文件不存在: {file_path}")
            return None
        return self._read_with_encoding(file_path)

    def _read_with_encoding(self, file_path: str) -> Optional[str]:
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, Exception):
                continue
        try:
            with open(file_path, 'rb') as f:
                return f.read().decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"所有编码尝试均失败: {e}")
            return None

    def write_file(self, file_path: str, content: str) -> bool:
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"成功写入文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"写入文件失败: {e}")
            return False

    def write_fixed_file(self, original_path: str, fixed_content: str) -> str:
        path = Path(original_path)
        fixed_path = path.parent / f"{path.stem}_fixed{path.suffix}"
        return str(fixed_path) if self.write_file(str(fixed_path), fixed_content) else original_path