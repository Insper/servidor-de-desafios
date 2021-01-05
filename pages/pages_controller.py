
def list_pages(root_dir):
    pages = []
    for concept_dir in root_dir.iterdir():
        if concept_dir.name == 'raw' or not concept_dir.is_dir():
            continue
        for filename in concept_dir.glob('*.md'):
            pages.append(f'{concept_dir.name}/{filename.stem}')
    return pages
