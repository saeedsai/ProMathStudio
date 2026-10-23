"""Embed src/data-tables.js into index.html for standalone offline distribution."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'index.html'
s=p.read_text(encoding='utf-8')
start='<script id="mathstudio-data-tables">'
i=s.index(start)+len(start);j=s.index('</script>',i)
s=s[:i]+'\n'+(root/'src/data-tables.js').read_text(encoding='utf-8')+'\n'+s[j:]
p.write_text(s,encoding='utf-8')
print('Updated standalone index.html')
