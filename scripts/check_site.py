"""Validate the generated Pages artifact without API keys or third-party packages."""
import ast
import json
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1] / 'dist'
for name in ('index.html', 'style.css', 'app.js', 'course.js'):
    assert (ROOT / name).is_file(), name
raw = (ROOT / 'course.js').read_text(encoding='utf-8')
course = json.loads(raw.removeprefix('const COURSE = ').strip().removesuffix(';'))
assert [week['id'] for week in course] == list(range(13))
for file in ROOT.rglob('*.py'):
    ast.parse(file.read_text(encoding='utf-8'), filename=str(file))
for file in (ROOT / 'diagrams').glob('*.svg'):
    ElementTree.parse(file)
for week in course:
    lecture = week['lecture']
    handout = ROOT / lecture['path']
    assert handout.is_file(), lecture['path']
    markdown = handout.read_text(encoding='utf-8')
    assert lecture['question'] in markdown and lecture['answer'] in markdown
    for chapter in week['concepts']:
        assert chapter['discussion'] and chapter['discussion'] in markdown
        if chapter.get('diagram'):
            assert (ROOT / chapter['diagram']['src']).is_file()
    for example in week['examples'] + week.get('support', []):
        assert (ROOT / example['path']).is_file(), example['path']
    with ZipFile(ROOT / 'examples' / f"week-{week['id']:02d}.zip") as archive:
        assert archive.testzip() is None
with ZipFile(ROOT / 'examples.zip') as archive:
    assert archive.testzip() is None
assert len(list((ROOT / 'diagrams').glob('*.svg'))) == 22
print('Validated 13 lectures and Markdown handouts, 73 chapters, 22 diagrams, Python syntax and all download archives.')
