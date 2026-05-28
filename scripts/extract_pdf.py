#!/usr/bin/env python3

import fitz
import json
import sys
from pathlib import Path


# Minimum image requirements for Gemini Vision
MIN_IMAGE_WIDTH = 300
MIN_IMAGE_HEIGHT = 300
MIN_IMAGE_BYTES = 20_000

# Where extracted images will be saved
OUTPUT_IMAGES_DIR = Path("/home/node/.n8n-files/extracted_images")


def should_send_image(width, height, size_bytes):
    if not width or not height:
        return False

    if width < MIN_IMAGE_WIDTH:
        return False

    if height < MIN_IMAGE_HEIGHT:
        return False

    if size_bytes < MIN_IMAGE_BYTES:
        return False

    return True


def normalize_mime_type(ext: str) -> str:
    ext = ext.lower()

    if ext in ("jpg", "jpeg"):
        return "image/jpeg"

    if ext == "png":
        return "image/png"

    return f"image/{ext}"


def extract_pdf(pdf_path: str) -> dict:
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    result = {
        "file_name": pdf_file.name,
        "file_path": str(pdf_file),
        "file_type": "pdf",
        "text": "",
        "has_text": False,
        "has_images": False,
        "images": [],
        "skipped_images": [],
        "pages": [],
        "total_pages": 0,
        "total_images": 0,
        "total_skipped_images": 0,
    }

    seen_xrefs = set()

    with fitz.open(pdf_path) as doc:

        for page_index, page in enumerate(doc):
            page_number = page_index + 1

            # Extract page text
            page_text = page.get_text("text") or ""

            page_data = {
                "page": page_number,
                "text": page_text,
                "images": [],
                "skipped_images": [],
            }

            if page_text.strip():
                result["text"] += f"\n\n--- Page {page_number} ---\n{page_text}"

            # Extract images
            for image_index, image_info in enumerate(page.get_images(full=True)):
                xref = image_info[0]

                # Skip duplicate images
                if xref in seen_xrefs:
                    continue

                seen_xrefs.add(xref)

                try:
                    extracted_image = doc.extract_image(xref)

                    image_bytes = extracted_image["image"]
                    image_ext = extracted_image["ext"]

                    width = extracted_image.get("width")
                    height = extracted_image.get("height")
                    size_bytes = len(image_bytes)

                    file_name = (
                        f"{pdf_file.stem}_page_{page_number}_img_{image_index + 1}.{image_ext}"
                    )

                    image_base = {
                        "page": page_number,
                        "index": image_index + 1,
                        "file_name": file_name,
                        "extension": image_ext,
                        "mime_type": normalize_mime_type(image_ext),
                        "width": width,
                        "height": height,
                        "size_bytes": size_bytes,
                    }

                    # Filter small/unimportant images
                    if not should_send_image(width, height, size_bytes):

                        skipped = {
                            **image_base,
                            "reason": "image_too_small",
                            "should_send_to_vision": False,
                        }

                        result["skipped_images"].append(skipped)
                        page_data["skipped_images"].append(skipped)

                        continue

                    # Save image to disk
                    image_path = OUTPUT_IMAGES_DIR / file_name

                    with open(image_path, "wb") as f:
                        f.write(image_bytes)

                    image_json = {
                        **image_base,
                        "file_path": str(image_path),
                        "should_send_to_vision": True,
                    }

                    result["images"].append(image_json)
                    page_data["images"].append(image_json)

                except Exception as e:

                    error_image = {
                        "page": page_number,
                        "index": image_index + 1,
                        "error": str(e),
                        "should_send_to_vision": False,
                    }

                    result["skipped_images"].append(error_image)
                    page_data["skipped_images"].append(error_image)

            result["pages"].append(page_data)

    result["text"] = result["text"].strip()

    result["has_text"] = bool(result["text"])
    result["has_images"] = len(result["images"]) > 0

    result["total_pages"] = len(result["pages"])
    result["total_images"] = len(result["images"])
    result["total_skipped_images"] = len(result["skipped_images"])

    return result


def main():

    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python3 extract_pdf.py <pdf_path>",
        }))
        sys.exit(1)

    pdf_path = sys.argv[1]

    try:
        result = extract_pdf(pdf_path)

        result["success"] = True

        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:

        print(json.dumps({
            "success": False,
            "error": str(e),
            "file_path": pdf_path,
        }))

        sys.exit(1)


if __name__ == "__main__":
    main()