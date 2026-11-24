import json,wave,numpy as np,sys,subprocess,os
SR=48000
VO='/tmp/claude-0/-home-user-EnesAksesuar/57d0c4c9-193d-564a-89af-bb1d6e48178e/scratchpad/vo'
MUSIC=sys.argv[1]; OUT=sys.argv[2]; DUR=float(sys.argv[3])
# caption/VO start times, locked to the edit
STARTS=[0.20,4.05,7.60,10.25,11.65,15.00,17.05,19.60]
lines=json.load(open(os.path.join(VO,'lines.json')))
N=int(DUR*SR)
def rd(p):
    tmp=p+'.48k.wav'
    subprocess.run(['ffmpeg','-y','-v','error','-i',p,'-ar',str(SR),'-ac','1',tmp],check=True)
    with wave.open(tmp,'rb') as w:
        a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64)/32768
    os.remove(tmp); return a
voice=np.zeros(N); duck=np.zeros(N)
for ln,st in zip(lines,STARTS):
    a=rd(os.path.join(VO,ln['id']+'.wav'))
    # light de-ess / warmth: gentle high shelf cut via 1-pole
    b=np.zeros_like(a); pv=0.0
    for i in range(len(a)): pv=pv+0.62*(a[i]-pv); b[i]=pv
    a=a*0.55+b*0.45
    i0=int(st*SR); n=min(len(a),N-i0)
    if n<=0: continue
    f=int(0.012*SR)
    a=a[:n].copy(); a[:f]*=np.linspace(0,1,f); a[-f:]*=np.linspace(1,0,f)
    voice[i0:i0+n]+=a*1.0
    d=np.zeros(N); j0=max(0,i0-int(0.22*SR)); j1=min(N,i0+n+int(0.34*SR))
    d[j0:j1]=1.0
    duck=np.maximum(duck,d)
# smooth the duck envelope
k=int(0.16*SR); ker=np.ones(k)/k
duck=np.convolve(duck,ker,mode='same'); duck=np.clip(duck,0,1)
with wave.open(MUSIC,'rb') as w:
    m=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64)/32768
m=m.reshape(-1,2)
if len(m)<N: m=np.vstack([m,np.zeros((N-len(m),2))])
m=m[:N]
gain=(1.0-0.56*duck)[:,None]
mix=m*gain*0.95
pk=np.abs(voice).max() or 1.0
v=(voice/pk)*0.80
mix[:,0]+=v; mix[:,1]+=v
mix=np.tanh(mix*1.25)/1.25
pk=np.abs(mix).max(); mix*=0.94/pk
st=np.empty(N*2); st[0::2]=mix[:,0]; st[1::2]=mix[:,1]
with wave.open(OUT,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype('<i2').tobytes())
print('mix ->',OUT)
