import json


def list_pages(root_dir):
    pages = []
    for concept_dir in root_dir.iterdir():
        if concept_dir.name == 'raw' or not concept_dir.is_dir():
            continue
        for filename in concept_dir.glob('*.md'):
            pages.append(f'{concept_dir.name}/{filename.stem}')
    return pages


def _deepmerge(dst, src):
    for k, v in src.items():
        if k in dst:
            if isinstance(dst[k], dict) and isinstance(v, dict):
                dst[k] = _deepmerge(dst[k], v)
            if isinstance(dst[k], list) and isinstance(v, list):
                dst[k] += v
            else:
                dst[k] = v
        else:
            dst[k] = v
    return dst


def list_contents(root_dir):
    contents = {}
    for repo_dir in root_dir.iterdir():
        contents_file = repo_dir / 'contents.json'
        if not contents_file.is_file():
            continue
        with open(contents_file) as f:
            contents = _deepmerge(contents, json.load(f))
    return contents
