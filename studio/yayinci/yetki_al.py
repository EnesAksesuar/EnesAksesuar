#!/usr/bin/env python3
"""YouTube yetkisini bir kez alir ve refresh token'i ekrana yazar.

Once Google Cloud'da bir OAuth istemcisi olusturun (bkz. KURULUM.md), sonra:
  YT_CLIENT_ID=... YT_CLIENT_SECRET=... python3 yetki_al.py
"""
import os, sys
from google_auth_oauthlib.flow import InstalledAppFlow

cid, cs = os.environ.get('YT_CLIENT_ID'), os.environ.get('YT_CLIENT_SECRET')
if not cid or not cs:
    sys.exit('YT_CLIENT_ID ve YT_CLIENT_SECRET ortam degiskenlerini verin.')

flow = InstalledAppFlow.from_client_config(
    {'installed': {'client_id': cid, 'client_secret': cs,
                   'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                   'token_uri': 'https://oauth2.googleapis.com/token',
                   'redirect_uris': ['http://localhost']}},
    scopes=['https://www.googleapis.com/auth/youtube.upload'])

# Tarayicisi olmayan makinelerde konsol akisi
creds = flow.run_local_server(port=0, open_browser=True) \
    if os.environ.get('DISPLAY') or os.name == 'nt' else flow.run_console()

print('\nBu satiri guvenli bir yere kaydedin:\n')
print('YT_REFRESH_TOKEN=' + creds.refresh_token)
