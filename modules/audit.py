import os
import re
import requests
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv
from zabbix_api import ZabbixAPI

# --- CONFIG ---
current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)
EOL_API = "https://endoflife.date/api"

try:
    zapi = ZabbixAPI(server=os.getenv("zabbix_host"))
    zapi.login(user=os.getenv("zabbix_user"), password=os.getenv("zabbix_password"))
except: zapi = None

# --- FONCTIONS ---
def get_eol_data(product):
    try:
        r = requests.get(f"{EOL_API}/{product}.json")
        return r.json() if r.status_code == 200 else None
    except: return None

def check_status(eol_value):
    if eol_value is False or eol_value is None: return "✅ SUPPORTÉ (Version Actuelle)"
    s_val = str(eol_value).strip()
    if s_val.lower() == "false": return "✅ SUPPORTÉ (Version Actuelle)"
    try:
        eol = datetime.strptime(s_val, "%Y-%m-%d").date()
        today = date.today()
        if today > eol: return f"🔴 OBSOLÈTE ({eol})"
        elif (eol - today).days < 180: return f"⚠️  FIN PROCHE ({eol})"
        else: return f"✅ OK ({eol})"
    except: return "❓ Date Inconnue"

def guess_product_and_version(s):
    if not s: return None, None
    s = s.lower()
    if "opnsense" in s:
        m = re.search(r'opnsense (\d+\.\d+)', s)
        if m: return "opnsense", m.group(1)
        m = re.search(r'(2\d\.\d+)', s)
        if m: return "opnsense", m.group(1)
    if "ubuntu" in s:
        m = re.search(r'(\d{2}\.\d{2})', s)
        if m: return "ubuntu", m.group(1)
    if "debian" in s:
        m = re.search(r'debian (\d+)', s)
        if m: return "debian", m.group(1)
    if "windows" in s:
        if "server" in s:
            if "2025" in s: return "windows-server", "2025"
            if "2022" in s: return "windows-server", "2022"
            if "2019" in s: return "windows-server", "2019"
            if "2016" in s: return "windows-server", "2016"
            if "2012" in s: return "windows-server", "2012-r2"
        else:
            if "10" in s: return "windows", "10"
            if "11" in s: return "windows", "11"
    if "alpine" in s:
        m = re.search(r'v(\d+\.\d+)', s)
        if m: return "alpine", m.group(1)
    return None, None

# --- FONCTION PRINCIPALE (Appelée par le main) ---
def run_audit_zabbix():
    if not zapi: return print("❌ Erreur Zabbix")
    print("\n🔍 Scan Zabbix...")
    hosts = zapi.host.get({"output": ["name"], "selectInventory": ["os"]})
    print(f"\n{'MACHINE':<20} | {'OS DÉTECTÉ':<20} | {'VERSION':<10} | {'DIAGNOSTIC EOL'}")
    print("=" * 90)
    for h in hosts:
        raw = "Inconnu"
        inventory = h.get('inventory')
        if isinstance(inventory, dict) and inventory.get('os'): raw = inventory['os']
        else:
            i = zapi.item.get({"output": ["lastvalue"], "hostids": h['hostid'], "search": {"key_": "system.sw.os"}, "limit": 1})
            if not i: i = zapi.item.get({"output": ["lastvalue"], "hostids": h['hostid'], "search": {"key_": "system.uname"}, "limit": 1})
            if not i: i = zapi.item.get({"output": ["lastvalue"], "hostids": h['hostid'], "search": {"key_": "system.descr"}, "limit": 1})
            if i: raw = i[0]['lastvalue']
        prod, ver = guess_product_and_version(raw)
        diag = "❓ OS Inconnu"
        if prod:
            data = get_eol_data(prod)
            found = False
            if data:
                for c in data:
                    if str(c['cycle']) == str(ver):
                        diag = check_status(c['eol'])
                        found = True
                        break
            if not found:
                try:
                    if prod == "opnsense" and float(ver) > 24.0: diag = "✅ SUPPORTÉ (Version Récente)"
                    else: diag = f"❓ Version {ver} inconnue API"
                except: diag = f"❓ Version {ver} inconnue API"
        print(f"{h['name']:<20} | {prod if prod else 'Autre':<20} | {ver if ver else '?':<10} | {diag}")