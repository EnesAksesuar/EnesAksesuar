import numpy as np, sys, wave

SR=48000
DUR=float(sys.argv[1]) if len(sys.argv)>1 else 23.0
TURN=float(sys.argv[2]) if len(sys.argv)>2 else 12.6   # when hope arrives
LONELY=float(sys.argv[3]) if len(sys.argv)>3 else 8.0  # when the heartbeat starts
OUT=sys.argv[4] if len(sys.argv)>4 else 'music.wav'
N=int(DUR*SR); t=np.arange(N)/SR
L=np.zeros(N); R=np.zeros(N)

def note(f,start,dur,amp=0.25,harm=(1,.42,.22,.12,.06),decay=2.6,attack=0.006,pan=0.5,detune=0.4):
    i0=int(start*SR); n=int(dur*SR)
    if i0>=N: return
    n=min(n,N-i0); tt=np.arange(n)/SR
    env=np.exp(-tt*decay)
    a=int(attack*SR);  env[:a]*=np.linspace(0,1,a) if a>0 and a<=n else 1
    s=np.zeros(n)
    for k,h in enumerate(harm,1):
        s+=h*np.sin(2*np.pi*f*k*tt+np.sin(2*np.pi*f*k*tt*0.5)*0.12)
        s+=h*0.5*np.sin(2*np.pi*(f*k+detune)*tt)
    s*=env*amp/sum(harm)
    L[i0:i0+n]+=s*(1-pan); R[i0:i0+n]+=s*pan

def pad(f,start,dur,amp=0.1,attack=1.4,release=2.0,pan=0.5):
    i0=int(start*SR); n=int(dur*SR)
    if i0>=N: return
    n=min(n,N-i0); tt=np.arange(n)/SR
    env=np.ones(n); a=min(int(attack*SR),n); r=min(int(release*SR),n)
    env[:a]*=np.linspace(0,1,a)**1.6; env[n-r:]*=np.linspace(1,0,r)**1.3
    s=(np.sin(2*np.pi*f*tt)+0.5*np.sin(2*np.pi*f*2*tt)
       +0.3*np.sin(2*np.pi*(f*1.5+0.3)*tt)+0.22*np.sin(2*np.pi*(f*3+0.5)*tt))
    s*=(1+0.05*np.sin(2*np.pi*0.18*tt))      # slow breathing
    s*=env*amp
    L[i0:i0+n]+=s*(1-pan); R[i0:i0+n]+=s*pan

def heart(start,dur,amp=0.5,bpm=52):
    i0=int(start*SR); n=min(int(dur*SR),N-i0)
    if i0>=N or n<=0: return
    tt=np.arange(n)/SR; out=np.zeros(n); per=60.0/bpm
    k=0
    while k*per<dur:
        for off,g in ((0.0,1.0),(0.26,0.62)):
            s0=int((k*per+off)*SR)
            if s0>=n: continue
            ln=min(int(0.17*SR),n-s0); u=np.arange(ln)/SR
            f=np.linspace(62,34,ln)
            out[s0:s0+ln]+=g*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-u*16)
        k+=1
    fade=np.clip(np.minimum(np.arange(n)/(1.2*SR),(n-np.arange(n))/(1.2*SR)),0,1)
    out*=amp*fade; L[i0:i0+n]+=out*0.5; R[i0:i0+n]+=out*0.5

def nf(n): return 440.0*(2**((n-69)/12.0))
A2,C3,E3,F3,G3,A3,C4,D4,E4,F4,G4,A4,C5,E5 = [nf(x) for x in (45,48,52,53,55,57,60,62,64,65,67,69,72,76)]

# ---- bed: A minor drone that opens up at the turn
pad(A2*0.5,0.0,DUR,amp=0.085,attack=2.2,release=3.0)
pad(E3,0.0,TURN+1.5,amp=0.045,attack=3.0,release=2.0,pan=0.35)
pad(C4,TURN-0.6,DUR-TURN+0.6,amp=0.055,attack=2.0,release=3.2,pan=0.62)
pad(G3,TURN+1.0,DUR-TURN-1.0,amp=0.040,attack=2.4,release=3.0,pan=0.4)

# ---- arpeggio: Am - F - C - G, sparse before the turn, blooming after
prog=[(0.0,[A3,C4,E4]),(3.2,[F3,A3,C4]),(6.4,[C4,E4,G4]),(9.6,[G3,C4,E4]),
      (12.8,[A3,C4,E4]),(16.0,[F3,A3,C4]),(19.2,[C4,E4,G4])]
for bar,ch in prog:
    if bar>=DUR: break
    for j,f in enumerate(ch):
        st=bar+j*0.58
        if st>=DUR: break
        bright = st>=TURN-0.4
        note(f,st,3.0,amp=0.15 if bright else 0.10,
             decay=1.9 if bright else 2.6,pan=0.34+0.16*j)
        if bright:   # upper octave sparkle only after the turn
            note(f*2,st+0.29,2.2,amp=0.055,decay=2.8,pan=0.66-0.14*j)

# ---- the lonely heartbeat
heart(LONELY,TURN-LONELY+0.4,amp=0.44)

# ---- the lift at the turn: rising swell + resolving chord
sw=int(1.9*SR); i0=max(0,int((TURN-1.9)*SR)); ln=min(sw,N-i0)
if ln>0:
    u=np.arange(ln)/SR
    f=np.linspace(130,520,ln)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*(u/u[-1])**2.1*0.10
    s+=np.random.default_rng(7).normal(0,1,ln)*(u/u[-1])**3*0.035
    L[i0:i0+ln]+=s*0.5; R[i0:i0+ln]+=s*0.5
for f,p in ((A3,0.3),(C4,0.5),(E4,0.7),(A4,0.5)):
    note(f,TURN,4.2,amp=0.13,decay=1.25,pan=p)

# ---- final resolve
if DUR-2.6>0:
    for f,p in ((A3,0.35),(E4,0.5),(A4,0.65)):
        note(f,DUR-2.6,2.6,amp=0.10,decay=1.5,pan=p)

# ---- reverb (exponentially decaying noise convolution)
rng=np.random.default_rng(3); IR=int(1.5*SR)
ir=rng.normal(0,1,IR)*np.exp(-np.arange(IR)/SR*3.4); ir[:int(0.012*SR)]=0; ir/=np.abs(ir).sum()
def verb(x,mix=0.30):
    w=np.convolve(x,ir,mode='full')[:len(x)]
    return x*(1-mix)+w*mix*3.0
L=verb(L); R=verb(R)

# ---- gentle low-pass before the turn (muffled = emotionally closed), opens after
op=np.clip((t-(TURN-1.2))/2.4,0,1)
a=0.22+0.70*op
def lp(x,a):
    y=np.zeros_like(x); prev=0.0
    for i in range(len(x)):
        prev=prev+a[i]*(x[i]-prev); y[i]=prev
    return y
try:
    import scipy.signal  # noqa
    L=lp(L,a); R=lp(R,a)
except Exception:
    L=lp(L,a); R=lp(R,a)

# ---- master: soft limit + fades
def fin(x):
    x=np.tanh(x*1.5)/1.5
    f=int(0.6*SR); x[:f]*=np.linspace(0,1,f)
    g=int(1.6*SR); x[-g:]*=np.linspace(1,0,g)**1.2
    return x
L=fin(L); R=fin(R)
pk=max(np.abs(L).max(),np.abs(R).max()); L*=0.82/pk; R*=0.82/pk

st=np.empty(N*2); st[0::2]=L; st[1::2]=R
with wave.open(OUT,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype('<i2').tobytes())
print('music ->',OUT,round(DUR,2),'s')
