import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from zabbix_api import ZabbixAPI

# --- SETUP ---
current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

try:
    zapi = ZabbixAPI(server=os.getenv("zabbix_host"))
    zapi.login(user=os.getenv("zabbix_user"), password=os.getenv("zabbix_password"))
except Exception as e:
    zapi = None

# --- OUTILS ---
def format_uptime(seconds):
    try:
        sec = int(float(seconds))
        d = timedelta(seconds=sec)
        return str(d).split('.')[0]
    except: return "N/A"

def get_item_value(host_id, key_search):
    items = zapi.item.get({
        "output": ["lastvalue", "units"],
        "hostids": host_id,
        "search": {"key_": key_search},
        "sortfield": "name",
        "limit": 1
    })
    if items and items[0]['lastvalue'] is not None:
        val = items[0]['lastvalue']
        units = items[0].get('units', '')
        try: return f"{round(float(val), 1)} {units}"
        except: return f"{val} {units}"
    return "N/A"

def get_disk_usage(host_id):
    items = zapi.item.get({"output": ["key_", "lastvalue"], "hostids": host_id, "search": {"key_": "vfs.fs"}})
    found = "N/A"
    for item in items:
        key = item['key_']
        val = item['lastvalue']
        if "pused" in key and val is not None:
            if "[/,pused]" in key or "C:" in key: return f"{round(float(val), 1)} %"
            if found == "N/A": found = f"{round(float(val), 1)} %"
    return found

# --- FONCTION PRINCIPALE ---
def run_diagnostic():
    if not zapi:
        print("⛔ Erreur : Impossible de connecter à Zabbix.")
        return

    hosts = zapi.host.get({"output": ["hostid", "name"], "sortfield": "name"})
    print("\n" + "="*120)
    print(f"{'MACHINE':<15} | {'OS SYSTEM':<20} | {'UPTIME':<12} | {'CPU':<8} | {'RAM':<8} | {'DISK':<8} | {'SERVICES CRITIQUES'}")
    print("="*120)

    for host in hosts:
        h_id = host['hostid']
        h_name = host['name']
        
        os_ver = get_item_value(h_id, "system.sw.os")
        if os_ver == "N/A": os_ver = get_item_value(h_id, "system.uname")
        if os_ver == "N/A": os_ver = get_item_value(h_id, "system.descr") # Ajout SNMP

        os_display = "Inconnu"
        if "Windows" in os_ver: os_display = "Windows Server"
        elif "Linux" in os_ver: os_display = "Ubuntu / Linux"
        elif "BSD" in os_ver or "OPNsense" in os_ver: os_display = "OPNsense (BSD)"

        uptime = format_uptime(get_item_value(h_id, "system.uptime").split()[0])
        cpu = get_item_value(h_id, "system.cpu.util") 
        if cpu == "N/A": cpu = get_item_value(h_id, "system.cpu.load")
        ram = get_item_value(h_id, "vm.memory.utilization")
        disk = get_disk_usage(h_id)

        service_status = ""
        if "OPNsense" in os_display or "OPNSENSE" in h_name:
            net = get_item_value(h_id, "net.if.status[1]")
            service_status = "✅ Network UP" if "1" in net else "⚠️  Net Check"
            if cpu == "N/A": cpu = "-"
            if ram == "N/A": ram = "-"
            if disk == "N/A": disk = "-"
        elif "DB" in h_name or "SQL" in h_name:
            ping = get_item_value(h_id, "mysql.ping")
            service_status = "✅ MySQL UP" if "1" in ping else "🔴 MySQL DOWN"
        elif "AD" in h_name or "DNS" in h_name:
            dns = get_item_value(h_id, "net.tcp.listen[53]")
            service_status = "✅ DNS Actif" if "1" in dns else "⚠️  DNS Inactif"

        print(f"{h_name:<15} | {os_display:<20} | {uptime:<12} | {cpu:<8} | {ram:<8} | {disk:<8} | {service_status}")
    print("="*120 + "\n")