import time
import re
from playwright.sync_api import Playwright, sync_playwright

EMAIL = "isi gmail"
PASSWORD = "pass gmail"

SAVE_BUTTONS = ["Save", "Simpan", "Guardar", "Enregistrer"]
PUBLISH_BUTTONS = ["Publish", "Terbitkan", "Publier", "Publicar"]
LOGIN_EMAIL_BUTTONS = [
    "Log in with Email", "Log in with your email",
    "Masuk dengan Email", "Masuk dengan email Anda",
    "Se connecter avec l'email", "Connexion avec votre e-mail",
    "Iniciar sesión con tu email", "Anmelden mit Ihrer E-Mail",
    "Accedi con la tua email", "Entrar com seu e-mail",
]
LOGIN_BUTTONS = ["Log in", "Masuk", "Iniciar sesión", "Se connecter", "Anmelden", "Accedi", "Entrar"]
REGISTER_TO_LOGIN_LINKS = [
    "Iniciar sesión", "Log in", "Masuk", "Connexion", "Anmelden", "Accedi", "Entrar",
]
REGISTER_KEYWORDS = ["register", "Sign up", "daftar", "inscription", "registrarse"]
REGISTER_TITLES = ["Regístrate", "Sign up", "Daftar", "Inscription", "Registrieren", "Iscriviti"]
EMAIL_FIELD_LABELS = [
    "Email", "Correo electrónico", "Alamat email", "Adresse e-mail",
    "E-Mail", "E-mail", "Indirizzo email", "Endereço de e-mail"
]
PASSWORD_FIELD_LABELS = [
    "Password", "Contraseña", "Kata sandi", "Mot de passe",
    "Passwort", "Senha"
]
COMMENT_BUTTON_LABELS = [
    "Write a comment", "Tulis komentar", "Escribe un comentario", "Écrire un commentaire",
    "Komentar", "Comentar", "Comment", "留言", "コメントを書く"
]

def load_keywords(filepath="brand.txt"):
    keywords = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if '|' in line:
                    keyword, url = line.strip().split('|', 1)
                    keywords.append((keyword.strip(), url.strip()))
    except FileNotFoundError:
        print("[X] File brand.txt tidak ditemukan.")
    return keywords

def click_first_found_button(page, labels):
    for label in labels:
        regex = re.compile(label, re.I)
        for role in ["button", "link"]:
            try:
                page.get_by_role(role, name=regex).click(timeout=3000)
                return True
            except:
                continue
        try:
            el = page.locator(f'text="{label}"')
            if el.first.is_visible():
                el.first.click(timeout=3000)
                return True
        except:
            continue
    return False

def find_comment_area(page):
    for label in COMMENT_BUTTON_LABELS:
        try:
            btn = page.get_by_role("button", name=re.compile(label, re.I))
            if btn.first.is_visible():
                btn.first.click()
                return True
        except:
            continue
    for label in COMMENT_BUTTON_LABELS:
        try:
            textarea = page.locator(f'textarea[placeholder*="{label}"]')
            if textarea.first.is_visible():
                textarea.first.click()
                return True
        except:
            continue
    for label in COMMENT_BUTTON_LABELS:
        try:
            inputbox = page.locator(f'input[placeholder*="{label}"]')
            if inputbox.first.is_visible():
                inputbox.first.click()
                return True
        except:
            continue
    try:
        editable_divs = page.locator('div[contenteditable="true"]')
        count = editable_divs.count()
        for i in range(count):
            el = editable_divs.nth(i)
            try:
                text = el.inner_text()
                if any(lbl.lower() in text.lower() for lbl in COMMENT_BUTTON_LABELS):
                    el.click()
                    return True
            except:
                continue
    except:
        pass
    return False

def clean_keyword(keyword):
    return re.sub(r'\s+', ' ', keyword).strip()

def post_comment(page, keyword, link_url):
    try:
        editor = page.locator('div[contenteditable="true"]')
        clean_kw = clean_keyword(keyword)
        editor.first.type(f"{clean_kw}\n", delay=30)
        page.keyboard.press("ControlOrMeta+Shift+ArrowLeft")
        page.keyboard.press("ControlOrMeta+Shift+ArrowLeft")
        page.keyboard.press("ControlOrMeta+K")
        page.get_by_role("textbox", name=re.compile("URL", re.I)).fill(link_url)
        click_first_found_button(page, SAVE_BUTTONS)
        editor.first.press("ArrowRight")
    except Exception as e:
        print(f"[!] Gagal masukkan keyword '{keyword}': {e}")

def is_register_page(page):
    for title in REGISTER_TITLES:
        try:
            if page.locator(f"text={title}").first.is_visible():
                return True
        except:
            continue
    return False

def click_go_to_login_from_register(page):
    print("[i] Mencari tautan atau tombol untuk log in dari halaman register...")
    for label in REGISTER_TO_LOGIN_LINKS:
        try:
            for role in ["button", "link"]:
                locator = page.get_by_role(role, name=re.compile(label, re.I))
                if locator.first.is_visible():
                    locator.first.click()
                    page.wait_for_timeout(2000)
                    return True
            locator = page.locator(f"text={label}")
            if locator.first.is_visible():
                locator.first.click()
                page.wait_for_timeout(2000)
                return True
        except:
            continue
    print("[!] Tidak ditemukan tautan login di halaman register.")
    return False

def click_login_with_email(page):
    print("[i] Mencari tombol 'Log in dengan Email'...")
    for label in LOGIN_EMAIL_BUTTONS:
        try:
            locator = page.get_by_role("button", name=re.compile(label, re.I))
            if locator.first.is_visible():
                locator.first.click()
                page.wait_for_timeout(2000)
                return True
        except:
            continue
    return False

def handle_login(page):
    try:
        print("[i] Mendeteksi halaman Log in...")

        if is_register_page(page):
            click_go_to_login_from_register(page)
            page.wait_for_timeout(2000)

        click_login_with_email(page)

        email_input = None
        for label in EMAIL_FIELD_LABELS:
            try:
                email_input = page.get_by_role("textbox", name=re.compile(label, re.I))
                if email_input.first.is_visible():
                    break
            except:
                continue
        if not email_input or not email_input.first.is_visible():
            try:
                email_input = page.locator('input[type="email"]')
            except:
                email_input = None

        if email_input:
            email_input.first.fill(EMAIL, timeout=3000)
        else:
            print("[!] Kolom email tidak ditemukan.")

        password_input = None
        for label in PASSWORD_FIELD_LABELS:
            try:
                input_candidate = page.get_by_role("textbox", name=re.compile(label, re.I))
                if input_candidate.first.get_attribute("type") == "password":
                    password_input = input_candidate
                    break
            except:
                continue
        if not password_input or not password_input.first.is_visible():
            try:
                password_input = page.locator('input[type="password"]')
            except:
                password_input = None

        if password_input:
            password_input.first.fill(PASSWORD, timeout=3000)
        else:
            print("[!] Kolom password tidak ditemukan.")

        if not click_first_found_button(page, LOGIN_BUTTONS):
            print("[!] Tombol Log in tidak ditemukan.")
        else:
            page.wait_for_timeout(3000)

    except Exception as e:
        print(f"[!] Gagal Log in: {e}")

def handle_site(playwright: Playwright, url: str, keywords):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    try:
        print(f"\n[•] Membuka: {url}")
        page.goto(url, timeout=30000)
        page.wait_for_timeout(3000)

        for _ in range(4):
            page.mouse.wheel(0, 500)
            time.sleep(1)

        if is_register_page(page) or any(x in page.url.lower() for x in REGISTER_KEYWORDS):
            print("[i] Halaman register terdeteksi di awal. Mengarahkan ke Log in...")
            click_go_to_login_from_register(page)
            page.wait_for_timeout(3000)

        if not find_comment_area(page):
            print("[!] Kolom komentar tidak ditemukan.")
            return

        for keyword, link in keywords:
            post_comment(page, keyword, link)

        if not click_first_found_button(page, PUBLISH_BUTTONS):
            print("[!] Tombol Publish tidak ditemukan.")
        page.wait_for_timeout(2000)

        if any(x in page.url.lower() for x in ["Log in", "auth", "sign in", "register", "sign up"]) or is_register_page(page):
            print("[i] Setelah Publish diarahkan ke halaman login/register, mencoba Log in...")
            handle_login(page)
            page.wait_for_timeout(3000)

        print(f"[✓] Berhasil posting di: {url}")

    except Exception as e:
        print(f"[X] Gagal mengakses {url}: {e}")
    finally:
        context.close()
        browser.close()

def main():
    try:
        with open("list.txt", "r") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[X] File list.txt tidak ditemukan.")
        return

    keywords = load_keywords()
    if not keywords:
        print("[X] Tidak ada keyword yang dimuat.")
        return

    with sync_playwright() as playwright:
        for url in urls:
            handle_site(playwright, url, keywords)

if __name__ == "__main__":
    main()
