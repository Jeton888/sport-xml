from flask import Flask, Response
import re, ssl, urllib.request, base64, urllib.parse
from datetime import datetime

app = Flask(__name__)

XML_URLS = [
    "https://raw.githubusercontent.com/Jeton888/sport-xml/main/sportsstreamz.xml",
    "https://raw.githubusercontent.com/Jeton888/sport-xml/main/CASA.xml",
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"

# ============================================================
# AlbKanale CH Channels
# ============================================================
DEVICE_ID = "02ea0169b854ba15"
CIP       = "95.107.162.193"
MODEL     = "vivo V2218A"
VERSION   = "9"

ALBKANALE_CHANNELS = {
    "CH01": "nBe3U99o36", "CH02": "g52l7ShD2I", "CH03": "FcWR1z00O9",
    "CH05": "03d1i16JwK", "CH06": "6bC989Cx9x", "CH08": "6RuwZ880ek",
    "CH10": "7Akp64LaYc", "CH11": "29WM16sxT6", "CH14": "4X3GxvrxX4",
    "CH16": "9wE90i3V1a", "CH20": "hnL5c7a62C", "CH21": "834WQrfFqC",
    "CH22": "Quq9Q10C11", "CH23": "feWOU63p1M", "CH24": "8Cj344oLoG",
    "CH25": "96N6I7Gz5c", "CH26": "9ka6IT2pev", "CH27": "qS74bX5R7y",
    "CH28": "bTX8Z89NBu", "CH29": "33EX0lMzvh", "CH30": "6XQZ906tBS",
    "CH31": "IcXNh9284T", "CH32": "1TEHxpbp54", "CH33": "784RZSQmXm",
    "CH34": "8e0BGWq3QP", "CH35": "0CCmi55kum", "CH36": "OAeZf45PR4",
    "CH37": "9T75vF1eJp", "CH38": "h0x5O8McS7", "CH39": "KH9MLji71Y",
    "CH40": "GqHb8D4Km5", "CH44": "2or278E3Lk", "CH45": "25Sr0DRtbT",
    "CH46": "Sf6z10W4Qf", "CH48": "N18Cssc3Eu", "CH49": "Qu50r407Je",
    "CH50": "KEd2Y7227a", "CH52": "DE6BVk19q5", "CH53": "8e0sWQP5s3",
    "CH54": "Re872AxokO", "CH55": "Ge8n8zEN3W", "CH56": "PEP63cVM0z",
    "CH57": "DLY51cr1a3", "CH58": "90VNMnd2uo", "CH59": "82DGfEz7ks",
    "CH60": "6Sa5y6pUjq", "CH61": "GSi34TpOb4", "CH64": "WD05byd3M7",
    "CH65": "4Y68IKGJzz", "CH66": "84U3Nw8MhE", "CH67": "M7cGHCT5f4",
    "CH68": "30FG2Wipsn", "CH69": "00GDt93a9S",
}

def generate_albkanale_url(file_id):
    now        = datetime.now()
    date_str   = now.strftime("%d:%m:%Y")
    time_str   = now.strftime("%H:%M:%S")
    time_param = f"{date_str}&{time_str}"
    sig_raw    = f"{DEVICE_ID}&{time_param}"
    signature  = base64.b64encode(sig_raw.encode()).decode()
    url = (f"https://app-measurement.fastlycache.com/out/190126/EQZV32L053X/"
           f"{file_id}.js?cid={DEVICE_ID}&time={time_param}"
           f"&cip={CIP}&v={VERSION}&m={urllib.parse.quote(MODEL)}"
           f"&signature={signature}")
    return url

def get_albkanale_lines():
    lines = []
    for ch_name, file_id in sorted(ALBKANALE_CHANNELS.items()):
        url = generate_albkanale_url(file_id)
        lines.append(f'#EXTINF:-1 tvg-logo="" group-title="AlbKanale Live",{ch_name}')
        lines.append(f'#EXTVLCOPT:http-user-agent={UA}')
        lines.append(f'#EXTVLCOPT:http-referrer=https://aliez.tv/')
        lines.append(f'#EXTVLCOPT:http-cookie=passport=IG2GpFng03_23122025')
        lines.append(url)
    return lines

# ============================================================
# Funksionet origjinale
# ============================================================
def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            return r.read().decode('utf-8', errors='ignore')
    except:
        return ""

def xml_to_m3u(xml):
    items = re.findall(r'<item>(.*?)</item>', xml, re.DOTALL)
    lines = []
    for item in items:
        t  = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
        l  = re.search(r'<link>(.*?)</link>',  item, re.DOTALL)
        th = re.search(r'<thumbnail>(.*?)</thumbnail>', item, re.DOTALL)
        if not t or not l: continue
        title_raw = t.group(1).strip()
        link      = l.group(1).strip()
        thumb     = th.group(1).strip() if th else ''
        if not link.startswith('http') or 'Ignoreme' in link or 'google.com' in link: continue
        title = re.sub(r'\[COLOR [^\]]+\]|\[/COLOR\]|\[B\]|\[/B\]', '', title_raw).strip()
        tup = title_raw.upper()
        group = 'Sport Live'
        if 'PL:' in tup or 'PL]' in tup:          group = 'Premier League'
        elif 'CL:' in tup or 'CHAMPIONS' in tup:  group = 'Champions League'
        elif 'NATIONS' in tup:                     group = 'Nations League'
        elif 'SERIE A' in tup:                     group = 'Serie A'
        elif 'LALIGA' in tup or 'LA LIGA' in tup: group = 'La Liga'
        elif 'BUNDESLIGA' in tup:                  group = 'Bundesliga'
        elif 'LIGUE' in tup:                       group = 'Ligue 1'
        elif 'FA CUP' in tup:                      group = 'FA Cup'
        elif 'EUROPA' in tup:                      group = 'Europa League'
        ua = UA
        if '|User-Agent=' in link:
            parts = link.split('|User-Agent=')
            link = parts[0].strip()
            ua   = parts[1].strip()
        lines.append(f'#EXTINF:-1 tvg-logo="{thumb}" group-title="{group}",{title}')
        lines.append(f'#EXTVLCOPT:http-user-agent={ua}')
        lines.append(link)
    return lines

# ============================================================
# Routes
# ============================================================
@app.route('/')
@app.route('/live.m3u')
def playlist():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    all_lines = [f'#EXTM3U (Updated: {now})']

    # Sport streams nga XML
    for url in XML_URLS:
        content = fetch(url)
        if content:
            all_lines.extend(xml_to_m3u(content))

    # AlbKanale CH channels me signature te fresket
    all_lines.extend(get_albkanale_lines())

    response = Response('\n'.join(all_lines), mimetype='text/plain')
    response.headers['Content-Disposition'] = 'attachment; filename=live.m3u'
    return response
