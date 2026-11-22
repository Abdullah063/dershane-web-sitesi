from pathlib import Path
import re,base64,subprocess,json
root=Path.cwd();out=root/'assets/kuantum/optimized';mapping={}
p=root/'wp-content/uploads/2025/08/akademi-logo.svg';s=p.read_text();m=re.search(r'data:image/png;base64,([^"\s]+)',s);Path('/tmp/kuantum-logo-source.png').write_bytes(base64.b64decode(m[1]));subprocess.run(['cwebp','-quiet','-q','88','-resize','660','0','/tmp/kuantum-logo-source.png','-o','/tmp/kuantum-logo.webp'],check=True);s=s[:m.start()]+'data:image/webp;base64,'+base64.b64encode(Path('/tmp/kuantum-logo.webp').read_bytes()).decode()+s[m.end():];(out/'akademi-logo.svg').write_text(s);mapping[str(p.relative_to(root))]='assets/kuantum/optimized/akademi-logo.svg'
paths=['assets/kuantum/kuantum-amblem-seffaf.png','wp-content/uploads/2026/10/1900x800-gop-01.jpg-scaled.jpeg','wp-content/uploads/2026/10/33.jpg-scaled.jpeg','wp-content/uploads/2026/07/slider_2026.jpeg','wp-content/uploads/2026/02/1900x800-03-scaled-1.webp','wp-content/uploads/2026/02/akademi-denemeler.webp','wp-content/uploads/2026/02/1900x800-01-scaled-1.webp','wp-content/uploads/2026/02/1080-1350-01-scaled-1.webp','wp-content/uploads/2026/02/1080-1350-03-scaled-1.webp','wp-content/uploads/2026/02/1080-1350-02-scaled-1.webp']
for path in paths:
 p=root/path;dst=out/(p.name.replace('.','-')+'.webp');width=360 if 'amblem' in path else 720 if '1080-1350' in path else 1280
 subprocess.run(['cwebp','-quiet','-q','82','-m','6','-resize',str(width),'0',str(p),'-o',str(dst)],check=True);mapping[path]=str(dst.relative_to(root))
(root/'site-src/image-optimizations.json').write_text(json.dumps(mapping,indent=2)+'\n')
print('Image payload:',sum((root/p).stat().st_size for p in mapping),'->',sum((root/p).stat().st_size for p in mapping.values()))
