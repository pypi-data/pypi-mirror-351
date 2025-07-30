"""
Input utilities for Kritrima AI CLI.

This module provides utilities for processing and handling various types of input
including text, images, and file references for multi-modal AI interactions.
"""

import base64
import mimetypes
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from PIL import Image

from kritrima_ai.utils.file_utils import is_text_file, read_file_safe
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class InputProcessor:
    """
    Input processor for handling multi-modal input.

    Supports text processing, image handling, file inclusion,
    and context preparation for AI models.
    """

    def __init__(self, max_image_size: int = 1024 * 1024) -> None:
        """
        Initialize input processor.

        Args:
            max_image_size: Maximum image size in bytes
        """
        self.max_image_size = max_image_size
        self.supported_image_formats = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".bmp",
        }

    async def process_input(
        self,
        text: str,
        image_paths: Optional[List[Path]] = None,
        file_paths: Optional[List[Path]] = None,
        expand_file_tags: bool = True,
    ) -> Dict[str, Any]:
        """
        Process multi-modal input for AI consumption.

        Args:
            text: Input text
            image_paths: List of image file paths
            file_paths: List of file paths to include
            expand_file_tags: Whether to expand @file.txt tags

        Returns:
            Processed input dictionary
        """
        try:
            processed_input = {"type": "multi_modal", "content": [], "metadata": {}}

            # Process text content
            if text.strip():
                processed_text = await self._process_text(text, expand_file_tags)
                processed_input["content"].append(
                    {"type": "text", "content": processed_text}
                )

            # Process images
            if image_paths:
                for image_path in image_paths:
                    image_data = await self._process_image(image_path)
                    if image_data:
                        processed_input["content"].append(
                            {
                                "type": "image",
                                "content": image_data,
                                "metadata": {"path": str(image_path)},
                            }
                        )

            # Process additional files
            if file_paths:
                for file_path in file_paths:
                    file_data = await self._process_file(file_path)
                    if file_data:
                        processed_input["content"].append(
                            {
                                "type": "file",
                                "content": file_data,
                                "metadata": {"path": str(file_path)},
                            }
                        )

            # Add metadata
            processed_input["metadata"] = {
                "total_content_items": len(processed_input["content"]),
                "has_images": any(
                    item["type"] == "image" for item in processed_input["content"]
                ),
                "has_files": any(
                    item["type"] == "file" for item in processed_input["content"]
                ),
                "text_length": sum(
                    len(item["content"])
                    for item in processed_input["content"]
                    if item["type"] == "text"
                ),
            }

            return processed_input

        except Exception as e:
            logger.error(f"Error processing input: {e}")
            raise

    async def _process_text(self, text: str, expand_file_tags: bool = True) -> str:
        """
        Process text input with file tag expansion.

        Args:
            text: Input text
            expand_file_tags: Whether to expand @file.txt tags

        Returns:
            Processed text
        """
        if not expand_file_tags:
            return text

        # Find file tags (@filename.ext)
        file_tag_pattern = r"@([^\s@]+\.[a-zA-Z0-9]+)"
        matches = re.finditer(file_tag_pattern, text)

        processed_text = text
        for match in matches:
            file_path = Path(match.group(1))

            if file_path.exists() and is_text_file(file_path):
                try:
                    file_content = read_file_safe(file_path)
                    if file_content:
                        # Replace @filename with XML block
                        xml_block = f"""<file path="{file_path}">
{file_content}
</file>"""
                        processed_text = processed_text.replace(
                            match.group(0), xml_block
                        )
                        logger.info(f"Expanded file tag: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to expand file tag {file_path}: {e}")

        return processed_text

    async def _process_image(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process image file for AI consumption.

        Args:
            image_path: Path to image file

        Returns:
            Processed image data or None if failed
        """
        try:
            if not image_path.exists():
                logger.warning(f"Image file not found: {image_path}")
                return None

            # Check file extension
            if image_path.suffix.lower() not in self.supported_image_formats:
                logger.warning(f"Unsupported image format: {image_path.suffix}")
                return None

            # Check file size
            file_size = image_path.stat().st_size
            if file_size > self.max_image_size:
                logger.warning(f"Image too large ({file_size} bytes): {image_path}")
                # Try to resize
                resized_data = await self._resize_image(image_path)
                if resized_data:
                    return resized_data
                return None

            # Read and encode image
            async with aiofiles.open(image_path, "rb") as f:
                image_bytes = await f.read()

            # Encode to base64
            base64_data = base64.b64encode(image_bytes).decode("utf-8")

            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(image_path))
            if not mime_type:
                mime_type = "image/jpeg"  # Default

            return {
                "data": base64_data,
                "mime_type": mime_type,
                "size": len(image_bytes),
                "format": image_path.suffix.lower()[1:],  # Remove dot
            }

        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None

    async def _resize_image(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Resize image to fit within size limits.

        Args:
            image_path: Path to image file

        Returns:
            Resized image data or None if failed
        """
        try:
            with Image.open(image_path) as img:
                # Calculate new size to fit within limits
                original_size = img.size
                max_dimension = 1024  # Max width or height

                if max(original_size) > max_dimension:
                    ratio = max_dimension / max(original_size)
                    new_size = (
                        int(original_size[0] * ratio),
                        int(original_size[1] * ratio),
                    )
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Convert to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # Save to bytes
                import io

                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=85, optimize=True)
                img_bytes.seek(0)

                # Check if size is acceptable now
                if len(img_bytes.getvalue()) > self.max_image_size:
                    logger.warning(f"Image still too large after resize: {image_path}")
                    return None

                # Encode to base64
                base64_data = base64.b64encode(img_bytes.getvalue()).decode("utf-8")

                return {
                    "data": base64_data,
                    "mime_type": "image/jpeg",
                    "size": len(img_bytes.getvalue()),
                    "format": "jpeg",
                    "resized": True,
                    "original_size": original_size,
                    "new_size": img.size,
                }

        except Exception as e:
            logger.error(f"Error resizing image {image_path}: {e}")
            return None

    async def _process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process file for inclusion in context.

        Args:
            file_path: Path to file

        Returns:
            Processed file data or None if failed
        """
        try:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None

            if not is_text_file(file_path):
                logger.warning(f"Non-text file skipped: {file_path}")
                return None

            content = read_file_safe(file_path)
            if not content:
                logger.warning(f"Empty or unreadable file: {file_path}")
                return None

            # Get file metadata
            stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))

            return {
                "content": content,
                "mime_type": mime_type or "text/plain",
                "size": stat.st_size,
                "lines": content.count("\n") + 1,
                "extension": file_path.suffix.lower(),
                "name": file_path.name,
            }

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None

    def collapse_xml_blocks(self, text: str) -> str:
        """
        Collapse XML file blocks back to @file.txt format.

        Args:
            text: Text with XML blocks

        Returns:
            Text with collapsed file references
        """
        # Pattern to match XML file blocks
        xml_pattern = r'<file path="([^"]+)">\s*.*?\s*</file>'

        def replace_xml_block(match):
            file_path = match.group(1)
            return f"@{file_path}"

        return re.sub(xml_pattern, replace_xml_block, text, flags=re.DOTALL)

    def extract_file_references(self, text: str) -> List[str]:
        """
        Extract file references from text.

        Args:
            text: Input text

        Returns:
            List of file paths referenced in text
        """
        file_refs = []

        # Find @file.txt patterns
        file_tag_pattern = r"@([^\s@]+\.[a-zA-Z0-9]+)"
        matches = re.finditer(file_tag_pattern, text)

        for match in matches:
            file_refs.append(match.group(1))

        # Find XML file blocks
        xml_pattern = r'<file path="([^"]+)">'
        xml_matches = re.finditer(xml_pattern, text)

        for match in xml_matches:
            file_refs.append(match.group(1))

        return list(set(file_refs))  # Remove duplicates


# Convenience functions
async def create_input_item(
    text: str,
    image_paths: Optional[List[Path]] = None,
    file_paths: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    """
    Create a processed input item for AI consumption.

    Args:
        text: Input text
        image_paths: Optional list of image paths
        file_paths: Optional list of file paths

    Returns:
        Processed input item
    """
    processor = InputProcessor()
    return await processor.process_input(text, image_paths, file_paths)


async def expand_file_tags(text: str) -> str:
    """
    Expand @file.txt tags in text to XML blocks with file contents.

    Args:
        text: Input text with file tags

    Returns:
        Text with expanded file contents
    """
    processor = InputProcessor()
    return await processor._process_text(text, expand_file_tags=True)


def collapse_xml_blocks(text: str) -> str:
    """
    Collapse XML file blocks back to @file.txt format.

    Args:
        text: Text with XML blocks

    Returns:
        Text with collapsed file references
    """
    processor = InputProcessor()
    return processor.collapse_xml_blocks(text)


def extract_file_references(text: str) -> List[str]:
    """
    Extract file references from text.

    Args:
        text: Input text

    Returns:
        List of file paths referenced in text
    """
    processor = InputProcessor()
    return processor.extract_file_references(text)
