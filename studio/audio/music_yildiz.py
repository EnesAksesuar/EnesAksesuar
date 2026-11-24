import numpy as np, sys, wave
SR=48000
DUR=24.6; BOOM=10.62; HEART=19.30
OUT=sys.argv[1] if len(sys.argv)>1 else 'music.wav'
N=int(DUR*SR); t=np.arange(N)/SR
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(11)

def nf(n): return 440.0*(2**((n-69)/12.0))
A1,A2,E3,A3,C4,D4,E4,G4,A4,C5,E5=[nf(x) for x in (33,45,52,57,60,62,64,67,69,72,76)]

def note(f,start,dur,amp=.2,decay=2.2,attack=.006,pan=.5,harm=(1,.4,.2,.1,.05)):
    i0=int(start*SR)
    if i0>=N: return
    n=min(int(dur*SR),N-i0); tt=np.arange(n)/SR
    env=np.exp(-tt*decay); a=int(attack*SR)
    if 0<a<n: env[:a]*=np.linspace(0,1,a)
    s=np.zeros(n)
    for k,h in enumerate(harm,1):
        s+=h*np.sin(2*np.pi*f*k*tt)+h*.45*np.sin(2*np.pi*(f*k+.35)*tt)
    s*=env*amp/sum(harm)
    L[i0:i0+n]+=s*(1-pan); R[i0:i0+n]+=s*pan

def pad(f,start,dur,amp=.09,attack=1.5,release=2.2,pan=.5):
    i0=int(start*SR)
    if i0>=N: return
    n=min(int(dur*SR),N-i0); tt=np.arange(n)/SR
    env=np.ones(n); a=min(int(attack*SR),n); r=min(int(release*SR),n)
    env[:a]*=np.linspace(0,1,a)**1.6; env[n-r:]*=np.linspace(1,0,r)**1.3
    s=(np.sin(2*np.pi*f*tt)+.5*np.sin(2*np.pi*f*2*tt)+.28*np.sin(2*np.pi*(f*1.5+.3)*tt))
    s*=(1+.05*np.sin(2*np.pi*.17*tt))*env*amp
    L[i0:i0+n]+=s*(1-pan); R[i0:i0+n]+=s*pan

# --- act 1: low drone, something vast and old
pad(A1,0.0,BOOM+0.4,amp=.11,attack=2.0,release=.35)
pad(E3,1.2,BOOM-0.9,amp=.035,attack=3.0,release=.6,pan=.36)
for k,(f,st) in enumerate([(A3,1.0),(C4,2.6),(E4,4.4),(A3,6.2),(C4,7.6)]):
    note(f,st,3.4,amp=.075,decay=1.5,pan=.35+.1*(k%3))

# --- riser into the blast
rs=int(3.6*SR); i0=max(0,int((BOOM-3.6)*SR)); ln=min(rs,N-i0)
u=np.arange(ln)/SR; fr=np.linspace(70,760,ln)
sw=np.sin(2*np.pi*np.cumsum(fr)/SR)*(u/u[-1])**2.6*.16
sw+=rng.normal(0,1,ln)*(u/u[-1])**4*.07
L[i0:i0+ln]+=sw*.5; R[i0:i0+ln]+=sw*.5

# --- the blast: sub drop + noise body
i0=int(BOOM*SR); ln=min(int(3.2*SR),N-i0); u=np.arange(ln)/SR
sub=np.sin(2*np.pi*np.cumsum(np.linspace(78,24,ln))/SR)*np.exp(-u*1.9)*.62
nz=rng.normal(0,1,ln)
for _ in range(3): nz=np.convolve(nz,np.ones(9)/9,mode='same')
nz*=np.exp(-u*2.6)*.30
L[i0:i0+ln]+=(sub+nz)*.5; R[i0:i0+ln]+=(sub+nz*0.92)*.5

# --- act 2: drifting debris, sparse and cold
for f,st,p in [(E4,12.1,.3),(C5,13.3,.68),(A4,14.4,.42),(G4,15.6,.6),(E5,16.6,.36)]:
    note(f,st,3.2,amp=.065,decay=1.7,pan=p)
pad(A2,11.6,HEART-11.0,amp=.055,attack=2.4,release=1.8)

# --- act 3: it is you. warm resolve + heartbeat
pad(A2,HEART-1.0,DUR-HEART+1.0,amp=.085,attack=1.6,release=3.0)
pad(C4,HEART-0.6,DUR-HEART+0.6,amp=.055,attack=1.8,release=3.0,pan=.62)
pad(E4,HEART+0.4,DUR-HEART-0.4,amp=.042,attack=2.0,release=2.8,pan=.38)
for f,st,p in [(A3,HEART,.35),(C4,HEART+.5,.5),(E4,HEART+1.0,.65),(A4,HEART+1.5,.5),(C5,HEART+2.6,.44)]:
    note(f,st,3.6,amp=.10,decay=1.15,pan=p)
# heartbeat locked to the visual pulse (0.92 s)
per=0.92; k=0
while HEART+k*per < DUR:
    for off,g in ((0.0,1.0),(0.26,0.60)):
        s0=int((HEART+k*per+off)*SR)
        if s0>=N: continue
        ln=min(int(0.19*SR),N-s0); u=np.arange(ln)/SR
        fq=np.linspace(66,32,ln)
        h=np.sin(2*np.pi*np.cumsum(fq)/SR)*np.exp(-u*14)*g*.40
        L[s0:s0+ln]+=h*.5; R[s0:s0+ln]+=h*.5
    k+=1

# --- reverb
IR=int(1.8*SR)
ir=rng.normal(0,1,IR)*np.exp(-np.arange(IR)/SR*3.0); ir[:int(.014*SR)]=0; ir/=np.abs(ir).sum()
def verb(x,mix=.30):
    return x*(1-mix)+np.convolve(x,ir,mode='full')[:len(x)]*mix*3.0
L=verb(L); R=verb(R)

def fin(x):
    x=np.tanh(x*1.45)/1.45
    f=int(.5*SR); x[:f]*=np.linspace(0,1,f)
    g=int(1.8*SR); x[-g:]*=np.linspace(1,0,g)**1.2
    return x
L=fin(L); R=fin(R)
pk=max(np.abs(L).max(),np.abs(R).max()); L*=.80/pk; R*=.80/pk
st=np.empty(N*2); st[0::2]=L; st[1::2]=R
with wave.open(OUT,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype('<i2').tobytes())
print('music ->',OUT,DUR,'s')
