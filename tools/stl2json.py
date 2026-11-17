import sys,struct,json,collections
d=open(sys.argv[1],'rb').read()
n=struct.unpack('<I',d[80:84])[0]
tris=[]
for i in range(n):
    v=struct.unpack('<9f',d[84+50*i+12:84+50*i+48]); tris.append((v[0:3],v[3:6],v[6:9]))
key=lambda p:(round(p[0],3),round(p[1],3),round(p[2],3))
parent={}
def f(x):
    while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
    return x
for t in tris:
    ks=[key(p) for p in t]
    for k in ks: parent.setdefault(k,k)
    for a,b in ((ks[0],ks[1]),(ks[1],ks[2])):
        a,b=f(a),f(b)
        if a!=b: parent[a]=b
comp=collections.defaultdict(list)
for t in tris: comp[f(key(t[0]))].append(t)
objs=[]
for c,ts in comp.items():
    ps=[p for t in ts for p in t]
    mn=[min(p[j] for p in ps) for j in range(3)]; mx=[max(p[j] for p in ps) for j in range(3)]
    cx,cy=(mn[0]+mx[0])/2,(mn[1]+mx[1])/2
    idx={}; pos=[]; ind=[]
    for t in ts:
        for p in t:
            k=key(p)
            if k not in idx:
                idx[k]=len(idx); pos += [round(p[0]-cx,2), round(p[2]-mn[2],2), round(-(p[1]-cy),2)]
            ind.append(idx[k])
    objs.append({'y':cy,'tris':len(ts),'size':[round(mx[0]-mn[0],1),round(mx[2]-mn[2],1),round(mx[1]-mn[1],1)],'pos':pos,'idx':ind})
objs.sort(key=lambda o:o['y'])
for i,o in enumerate(objs): o['id']=i; del o['y']; print(i,o['tris'],o['size'])
json.dump({'objects':objs},open(sys.argv[2],'w'),separators=(',',':'))
