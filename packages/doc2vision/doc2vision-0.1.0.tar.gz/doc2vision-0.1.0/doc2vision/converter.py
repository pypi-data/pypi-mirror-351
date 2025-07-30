import os
import io
import sys
import tempfile
from typing import List, Union
from PIL import Image, ImageOps
import cv2
import numpy as np
from pdf2image import convert_from_path, pdfinfo_from_path



def convert_to_llm_ready_images(file_path: str, correct_skew: bool = False, resize_to: int = None) -> List[Image.Image]:
    """
    Converts PDF, JPG, PNG, or TIF files into high-quality, LLM-compatible images.
    Returns a list of RGB Pillow Images, preserving original resolution unless `resize_to` is specified.

    Parameters:
        file_path (str): Input file path.
        correct_skew (bool): Whether to attempt skew correction (default False).
        resize_to (int): Optional height to resize images to, preserving aspect ratio.
    """

    def is_image_file(path):
        return path.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff'))

    def enhance_image(pil_img: Image.Image) -> Image.Image:
        """Prepare image: convert to RGB, correct skew if enabled, resize if specified."""
        img = pil_img.convert("RGB")
        cv_img = np.array(img)
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)

        if correct_skew:
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            coords = np.column_stack(np.where(gray > 0))
            if len(coords) > 0:
                angle = cv2.minAreaRect(coords)[-1]
                if abs(angle) > 1.0:  # Skip tiny skews
                    if angle < -45:
                        angle = -(90 + angle)
                    else:
                        angle = -angle
                    (h, w) = cv_img.shape[:2]
                    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
                    cv_img = cv2.warpAffine(cv_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        if resize_to:
            h, w = cv_img.shape[:2]
            scale = resize_to / h
            cv_img = cv2.resize(cv_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

        return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

    output_images = []

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File does not exist: {file_path}")

    try:
        if is_image_file(file_path):
            with Image.open(file_path) as img:
                output_images.append(enhance_image(img))

        elif file_path.lower().endswith('.pdf'):
            pdf_info = pdfinfo_from_path(file_path)
            dpi = 300
            images = convert_from_path(file_path, dpi=dpi)
            for page_img in images:
                output_images.append(enhance_image(page_img))

        else:
            raise ValueError(f"Unsupported file type: {file_path}")

    except Exception as e:
        raise RuntimeError(f"Error processing file '{file_path}': {e}")

    if not output_images:
        raise ValueError("No images generated from file. Check if the file contains visible content.")

    return output_images

# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    test_file = "samples/sample.pdf"  # or .jpg, .png, .tif
    try:
        images = convert_to_llm_ready_images(test_file)
        print(f"Processed {len(images)} image(s) from file.")
        # Optional display
        for img in images:
            plt.imshow(img)
            plt.axis('off')
            plt.show()
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)

    test_file = "samples/sample.jpg"  # or .jpg, .png, .tif
    try:
        images = convert_to_llm_ready_images(test_file)
        print(f"Processed {len(images)} image(s) from file.")
        # Optional display
        for img in images:
            plt.imshow(img)
            plt.axis('off')
            plt.show()
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
