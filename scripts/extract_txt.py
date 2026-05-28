#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def extract_txt(txt_path: str) -> dict:
    txt_file = Path(txt_path)

    if not txt_file.exists():
        raise FileNotFoundError(f"TXT file not found: {txt_path}")

    text = txt_file.read_text(encoding="utf-8", errors="replace")

    lines = text.splitlines()

    return {
        "file_name": txt_file.name,
        "file_path": str(txt_file),
        "file_type": "txt",
        "text": text.strip(),
        "has_text": bool(text.strip()),
        "has_images": False,
        "images": [],
        "lines": lines,
        "total_lines": len(lines),
        "total_characters": len(text),
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python3 extract_txt.py <txt_path>",
        }))
        sys.exit(1)

    txt_path = sys.argv[1]

    try:
        result = extract_txt(txt_path)
        result["success"] = True
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "file_path": txt_path,
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
