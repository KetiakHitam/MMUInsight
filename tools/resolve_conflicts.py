import re,os
root=os.path.dirname(os.path.dirname(__file__))
files=[
    r"static/css/base.css",
    r"static/css/dark.css",
    r".gitignore",
    r"reviews.py",
    r"Procfile",
    r"requirements.txt",
    r"templates/about_us.html",
]
fixed=[]
for f in files:
    path=os.path.join(root,f)
    if not os.path.exists(path):
        print('Missing',f)
        continue
    s=open(path,'r',encoding='utf-8').read()
    if '<<<<<<<' not in s:
        print('No conflict in',f)
        continue
    pattern=re.compile(r'<<<<<<< HEAD\n.*?\n=======\n(.*?)\n>>>>>>> .*?\n', re.S)
    new, n=pattern.subn(lambda m: m.group(1), s)
    if n>0:
        open(path,'w',encoding='utf-8').write(new)
        fixed.append((f,n))
        print(f'Fixed {n} conflict(s) in {f}')
    else:
        print('Pattern not matched in',f)

print('\nRescan for remaining markers...')
for dirpath,dirnames,filenames in os.walk(root):
    for name in filenames:
        p=os.path.join(dirpath,name)
        try:
            txt=open(p,'r',encoding='utf-8').read()
        except Exception:
            continue
        if '<<<<<<<' in txt:
            print('Still conflicted:', os.path.relpath(p,root))

print('\nDone')
