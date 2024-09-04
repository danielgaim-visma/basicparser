import re
import json
import zipfile
import io

def sanitize_filename(filename):
    sanitized = re.sub(r'[^\w\-_\. ]', '', filename).replace(' ', '_')
    return sanitized[:50]

def create_zip_file(all_results):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for original_filename, sections in all_results.items():
            for i, section in enumerate(sections):
                section_filename = sanitize_filename(f"{original_filename}_section_{i + 1}")
                json_str = json.dumps(section, indent=4, ensure_ascii=False)
                zip_file.writestr(f"{section_filename}.json", json_str)
    zip_buffer.seek(0)
    return zip_buffer