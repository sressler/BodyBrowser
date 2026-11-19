import sys,os,gzip,json,struct,numpy as np
T={'char':'i1','int8':'i1','uchar':'u1','uint8':'u1','short':'i2','int16':'i2','ushort':'u2','uint16':'u2',
   'int':'i4','int32':'i4','uint':'u4','uint32':'u4','float':'f4','float32':'f4','double':'f8','float64':'f8'}
def read_ply(path):
    d=gzip.open(path).read() if path.endswith('.gz') else open(path,'rb').read()
    e=d.index(b'end_header');i=d.index(b'\n',e)+1
    fmt=None;els=[]
    for l in d[:e].decode('latin1').splitlines():
        w=l.split()
        if not w:continue
        if w[0]=='format':fmt=w[1]
        elif w[0]=='element':els.append([w[1],int(w[2]),[]])
        elif w[0]=='property':els[-1][2].append(w[1:])
    if fmt=='ascii':raise ValueError('ascii PLY not supported')
    bo='>' if fmt=='binary_big_endian' else '<'
    V=C=F=None
    for name,n,props in els:
        if all(p[0]!='list' for p in props):
            dt=np.dtype([(p[1],bo+T[p[0]]) for p in props]);a=np.frombuffer(d,dt,n,i);i+=n*dt.itemsize
            if name=='vertex':
                V=np.stack([a['x'],a['y'],a['z']],1).astype(np.float64)
                if all(k in a.dtype.names for k in('red','green','blue')):C=np.stack([a['red'],a['green'],a['blue']],1).astype('u1')
        else:
            p=props[0];ct,it=T[p[1]],T[p[2]]
            # fast path: every face a triangle
            dt=np.dtype([('n',bo+ct),('v',bo+it,(3,))])
            a=np.frombuffer(d,dt,n,i)
            if name=='face' and len(props)==1 and (a['n']==3).all():
                F=a['v'].astype(np.int64);i+=n*dt.itemsize
            else:
                cs,isz=np.dtype(ct).itemsize,np.dtype(it).itemsize;tris=[]
                for _ in range(n):
                    k=int(np.frombuffer(d,bo+ct,1,i)[0]);i+=cs
                    idx=np.frombuffer(d,bo+it,k,i);i+=k*isz
                    tris+= [(idx[0],idx[j],idx[j+1]) for j in range(1,k-1)]
                if name=='face':F=np.array(tris,np.int64)
    return V,C,F
def read_lnd(path):
    out=[]
    for l in open(path,errors='replace'):
        w=l.split()
        if len(w)>=8 and w[0].isdigit():
            try:x,y,z=map(float,w[4:7])
            except ValueError:continue
            if w[1]=='-999' or (x==0 and y==0 and z==0):continue   # landmark marked missing
            out.append((int(w[0])," ".join(w[7:]),x/1000,y/1000,z/1000))
    return out
def convert(ply,lndp,out):
    name=os.path.basename(ply).split('.')[0]
    V,C,F=read_ply(ply);nv=len(V)
    P=np.stack([V[:,0],V[:,2],-V[:,1]],1)   # Z-up scanner -> Y-up glTF
    fn=np.cross(P[F[:,1]]-P[F[:,0]],P[F[:,2]]-P[F[:,0]])
    N=np.zeros_like(P)
    for k in range(3):
        for c in range(3):N[:,c]+=np.bincount(F[:,k],fn[:,c],nv)
    ln=np.linalg.norm(N,axis=1);bad=ln==0;ln[bad]=1;N/=ln[:,None];N[bad]=[0,1,0]
    Pf=P.astype('<f4');Nf=N.astype('<f4');I=F.astype('<u4').ravel()
    attrs={"POSITION":0,"NORMAL":1};chunks=[(Pf.tobytes(),34962),(Nf.tobytes(),34962)]
    acc=[{"bufferView":0,"componentType":5126,"count":nv,"type":"VEC3","min":Pf.min(0).tolist(),"max":Pf.max(0).tolist()},
         {"bufferView":1,"componentType":5126,"count":nv,"type":"VEC3"}]
    if C is not None:
        C4=np.concatenate([C,np.full((nv,1),255,'u1')],1)
        chunks.append((C4.tobytes(),34962));attrs["COLOR_0"]=2
        acc.append({"bufferView":2,"componentType":5121,"normalized":True,"count":nv,"type":"VEC4"})
    chunks.append((I.tobytes(),34963))
    acc.append({"bufferView":len(chunks)-1,"componentType":5125,"count":len(I),"type":"SCALAR"})
    views=[];b=bytearray()
    for data,tgt in chunks:
        views.append({"buffer":0,"byteOffset":len(b),"byteLength":len(data),"target":tgt});b+=data;b+=b'\0'*((-len(b))%4)
    lms=read_lnd(lndp) if lndp and os.path.exists(lndp) else []
    nodes=[{"name":name,"children":[1]+([2] if lms else [])},{"name":name+"_scan","mesh":0}]
    if lms:
        nodes.append({"name":"landmarks","children":list(range(3,3+len(lms)))})
        for lid,lname,x,y,z in lms:
            ex={"landmark_id":lid}
            if lname.lower()=='crotch':ex["note"]="computed point, not on the scan surface"
            nodes.append({"name":f"{lid:02d} {lname}","translation":[x,z,-y],"extras":ex})
    src=os.path.relpath(ply,os.path.dirname(os.path.dirname(os.path.dirname(ply))))
    g={"asset":{"version":"2.0","generator":"CAESAR PLY to glTF converter",
        "extras":{"source":src,"units":"metres","note":"Scanner coordinates rotated from Z-up to glTF Y-up: (x,y,z)->(x,z,-y)",
                  "landmark_file":os.path.basename(lndp) if lms else None}},
       "scene":0,"scenes":[{"name":name,"nodes":[0]}],"nodes":nodes,
       "meshes":[{"name":name+"_scan","primitives":[{"attributes":attrs,"indices":len(acc)-1,"material":0,"mode":4}]}],
       "materials":[{"name":"scan_vertex_color","pbrMetallicRoughness":{"baseColorFactor":[1,1,1,1],"metallicFactor":0,"roughnessFactor":0.85},"doubleSided":True}],
       "accessors":acc,"bufferViews":views,"buffers":[{"byteLength":len(b)}]}
    j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
    tmp=out+'.part'
    with open(tmp,'wb') as f:
        f.write(struct.pack('<III',0x46546C67,2,28+len(j)+len(b)));f.write(struct.pack('<II',len(j),0x4E4F534A));f.write(j)
        f.write(struct.pack('<II',len(b),0x004E4942));f.write(b)
    os.replace(tmp,out)
    return nv,len(F),len(lms)
if __name__=='__main__':
    root=sys.argv[1]
    for ply in sys.argv[2:]:
        d=os.path.dirname(os.path.dirname(ply));name=os.path.basename(ply).split('.')[0]
        out=os.path.join(d,'gltf',name+'.glb')
        if os.path.exists(out):print('skip',name,flush=True);continue
        try:nv,nf,nl=convert(ply,os.path.join(d,'landmarks',name+'.lnd'),out);print('ok',name,nv,nf,nl,flush=True)
        except Exception as ex:print('FAIL',name,repr(ex),flush=True)
