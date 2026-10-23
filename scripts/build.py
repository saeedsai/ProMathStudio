"""Rebuild standalone index.html by embedding both source modules."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
index=root/'index.html'
text=index.read_text(encoding='utf-8')
for tag,source in [('mathstudio-data-tables','src/data-tables.js'),('promath-advanced-features','src/advanced-features.js'),('promath-numerical-data','src/numerical-data.js')]:
    start=f'<script id="{tag}">\n'
    i=text.index(start)+len(start)
    end=text.index('</script>',i)
    text=text[:i]+(root/source).read_text(encoding='utf-8').rstrip('\n')+'\n\n'+text[end:]
index.write_text(text,encoding='utf-8')
print('Rebuilt standalone index.html')
