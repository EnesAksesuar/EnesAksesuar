#!/usr/bin/env python3
"""YouTube Shorts yükleyici — resmi YouTube Data API v3.

Kurulum (tek sefer):  python3 yetki_al.py
Kullanim:             python3 yukle_youtube.py [--kuru]

Kimlik bilgileri ortam degiskenlerinden okunur; hicbiri bu dosyada tutulmaz:
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
"""
import json, os, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
KUYRUK = pathlib.Path(__file__).with_name('kuyruk.json')
KURU = '--kuru' in sys.argv

def cred():
    from google.oauth2.credentials import Credentials
    eksik = [k for k in ('YT_CLIENT_ID','YT_CLIENT_SECRET','YT_REFRESH_TOKEN')
             if not os.environ.get(k)]
    if eksik:
        sys.exit('Eksik ortam degiskeni: ' + ', '.join(eksik) +
                 '\nOnce studio/yayinci/yetki_al.py calistirin.')
    return Credentials(
        token=None,
        refresh_token=os.environ['YT_REFRESH_TOKEN'],
        client_id=os.environ['YT_CLIENT_ID'],
        client_secret=os.environ['YT_CLIENT_SECRET'],
        token_uri='https://oauth2.googleapis.com/token',
        scopes=['https://www.googleapis.com/auth/youtube.upload'])

def main():
    data = json.loads(KUYRUK.read_text(encoding='utf-8'))
    bekleyen = [v for v in data['kuyruk'] if v['durum'] == 'bekliyor']
    if not bekleyen:
        print('Kuyrukta bekleyen video yok.'); return
    v = bekleyen[0]
    yol = ROOT / v['dosya']
    if not yol.exists():
        sys.exit(f'Video bulunamadi: {yol}')
    y = v['youtube']
    print(f"Yuklenecek : {yol.name}  ({yol.stat().st_size/1e6:.1f} MB)")
    print(f"Baslik     : {y['baslik']}")
    print(f"Gizlilik   : {y['gizlilik']}")
    if KURU:
        print('\n[kuru calisma] Hicbir sey yuklenmedi.'); return

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    yt = build('youtube', 'v3', credentials=cred(), cache_discovery=False)
    istek = yt.videos().insert(
        part='snippet,status',
        body={'snippet': {'title': y['baslik'], 'description': y['aciklama'],
                          'tags': y['etiketler'], 'categoryId': y['kategori']},
              'status': {'privacyStatus': y['gizlilik'],
                         'selfDeclaredMadeForKids': False}},
        media_body=MediaFileUpload(str(yol), chunksize=4*1024*1024,
                                   resumable=True, mimetype='video/mp4'))
    yanit = None
    while yanit is None:
        durum, yanit = istek.next_chunk()
        if durum:
            print(f'  yukleniyor... %{int(durum.progress()*100)}')
    vid = yanit['id']
    link = f'https://www.youtube.com/shorts/{vid}'
    print('YAYINLANDI:', link)

    v['durum'] = 'yayinlandi'
    v['link'] = link
    v['yayin_tarihi'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    KUYRUK.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    kayit = ROOT / 'yayin' / 'KAYIT.csv'
    if kayit.exists():
        with kayit.open('a', encoding='utf-8') as f:
            f.write(f"{datetime.date.today()},{v['id']},YouTube Shorts,yayinlandi,"
                    f"\"{y['baslik']}\",{link},,,,,otomatik yukleme\n")
    print('kuyruk.json ve KAYIT.csv guncellendi.')

if __name__ == '__main__':
    main()
