import os
import sys
import json
import subprocess
import threading
import webbrowser
from datetime import datetime
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".github_pro_studio")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
HISTORY_FILE = os.path.join(CONFIG_DIR, "history.json")

DEFAULT_GITHUB_USERNAME = ""
DEFAULT_GITHUB_TOKEN = ""
DEFAULT_GEMINI_API_KEY = ""

GITIGNORE_TEMPLATES = {
    "Unity (C# / Oyun)": "\n".join([
        "[Ll]ibrary/", "[Tt]emp/", "[Oo]bj/", "[Bb]uild/", "[Bb]uilds/",
        "[Ll]ogs/", "[Uu]ser[Ss]ettings/", "*.csproj", "*.unityproj",
        "*.sln", "*.suo", "*.tmp", "*.user", "*.userprefs", "*.pidb",
        "*.booproj", "*.svd", "*.pdb", "*.mdb", "*.opendb", "*.VC.db",
        "sysinfo.txt", "*.apk", "*.aab", "*.unitypackage", ".DS_Store"
    ]),
    "Unreal Engine / 3D": "\n".join([
        "Binaries/", "DerivedDataCache/", "Intermediate/", "Saved/",
        "Build/", ".vs/", "*.VC.db", "*.opensdf", "*.opendb", "*.sdf",
        "*.sln", "*.suo", "*.xcodeproj", "*.xcworkspace", "*.blend1", ".DS_Store"
    ]),
    "Python / AI & Data": "\n".join([
        "__pycache__/", "*.py[cod]", "*$py.class", "*.so", ".Python",
        "env/", "venv/", ".venv/", "build/", "dist/", "*.egg-info/",
        ".ipynb_checkpoints", "*.h5", "*.keras", "*.pt", "*.pth", ".env", ".DS_Store"
    ]),
    "C++ / Arduino / ESP32": "\n".join([
        "build/", ".pio/", ".vscode/", "*.o", "*.out", "*.exe",
        "*.elf", "*.bin", "*.hex", "*.map", "*.d", "*.lib", "*.a", ".DS_Store"
    ]),
    "Web / Full-Stack": "\n".join([
        "node_modules/", "dist/", "build/", ".next/", ".nuxt/",
        ".env", ".env.local", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*", ".DS_Store"
    ]),
    "Genel (Standart)": "\n".join([
        ".DS_Store", "Thumbs.db", ".vscode/", ".idea/", "*.log", "*.tmp", ".env", "build/", "dist/"
    ])
}


class GitHubProStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GitHub Pro Studio - Otomatik Proje Yukleyici & Dokumantasyon Paneli")
        self.geometry("1180x800")
        self.minsize(1020, 720)

        # İkon Yükleme Bölümü
        self.set_app_icon()

        self.ensure_config_dir()
        self.config_data = self.load_json(CONFIG_FILE, {
            "username": DEFAULT_GITHUB_USERNAME,
            "token": DEFAULT_GITHUB_TOKEN,
            "gemini_key": DEFAULT_GEMINI_API_KEY,
            "default_template": "Unity (C# / Oyun)",
            "default_visibility": "Public (Herkese Acik)"
        })
        if DEFAULT_GITHUB_USERNAME and not self.config_data.get("username"):
            self.config_data["username"] = DEFAULT_GITHUB_USERNAME
        if DEFAULT_GITHUB_TOKEN and not self.config_data.get("token"):
            self.config_data["token"] = DEFAULT_GITHUB_TOKEN
        if DEFAULT_GEMINI_API_KEY and not self.config_data.get("gemini_key"):
            self.config_data["gemini_key"] = DEFAULT_GEMINI_API_KEY

        self.history_data = self.load_json(HISTORY_FILE, [])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_views()
        self.show_view("deploy")

        try:
            subprocess.run(
                ["git", "--version"], capture_output=True, check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
        except FileNotFoundError:
            if messagebox.askyesno("Git Kurulu Degil", "Bu uygulamanin calismasi icin bilgisayarinizda Git kurulu olmalidir.\n\nSimdi resmi indirme sayfasini acmak ister misiniz?"):
                webbrowser.open("https://git-scm.com/downloads")

    def set_app_icon(self):
        """Çift tıklamayla veya exe ile çalışırken uygulama sol üst ve görev çubuğu ikonunu yükler"""
        icon_name = "app_icon.ico"
        
        # PyInstaller'ın geçici dizin yolunu veya mevcut dizini bulur
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        icon_path = os.path.join(base_path, icon_name)
        
        # Eğer ikon o an dizinde yoksa yerel klasörden kontrol et
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.getcwd(), icon_name)

        if os.path.exists(icon_path):
            try:
                # Windows & Linux / macOS uyumlu ikon yükleme
                if sys.platform.startswith('win'):
                    self.iconbitmap(icon_path)
                else:
                    self.iconphoto(False, ctk.CTkImage(icon_path))
            except Exception:
                pass # İkon yüklenemezse varsayılan pencere ile açılır

    def ensure_config_dir(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)

    def load_json(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def format_github_repo_name(self, raw_name):
        tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ ", "cgiosuCGIOSU-")
        clean = raw_name.strip().translate(tr_map)
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
        clean = "".join(c if c in allowed else "-" for c in clean)
        while "--" in clean:
            clean = clean.replace("--", "-")
        return clean.strip("-")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            self.sidebar, text="GitHub Pro\nStudio",
            font=ctk.CTkFont(size=22, weight="bold"), justify="center"
        ).grid(row=0, column=0, padx=20, pady=(25, 10))

        ctk.CTkLabel(
            self.sidebar, text="Otomatik Deploy & AI Docs",
            font=ctk.CTkFont(size=11), text_color="gray70"
        ).grid(row=1, column=0, padx=20, pady=(0, 25))

        self.nav_deploy_btn = ctk.CTkButton(
            self.sidebar, text="Proje Yukle (Deploy)", height=42, anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"), command=lambda: self.show_view("deploy")
        )
        self.nav_deploy_btn.grid(row=2, column=0, padx=15, pady=6, sticky="ew")

        self.nav_history_btn = ctk.CTkButton(
            self.sidebar, text="Yuklenen Projeler", height=42, anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"), command=lambda: self.show_view("history")
        )
        self.nav_history_btn.grid(row=3, column=0, padx=15, pady=6, sticky="ew")

        self.nav_settings_btn = ctk.CTkButton(
            self.sidebar, text="Ayarlar & Hafiza", height=42, anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"), command=lambda: self.show_view("settings")
        )
        self.nav_settings_btn.grid(row=4, column=0, padx=15, pady=6, sticky="ew")

        self.status_badge = ctk.CTkLabel(self.sidebar, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.status_badge.grid(row=6, column=0, padx=15, pady=(10, 20))
        self.update_sidebar_status()

    def update_sidebar_status(self):
        if self.config_data.get("username") and self.config_data.get("token"):
            self.status_badge.configure(text=f"Bagli: @{self.config_data['username']}", text_color="#4ade80")
        else:
            self.status_badge.configure(text="Ayarlar Eksik (Ayarlara Gidin)", text_color="#fb923c")

    def show_view(self, view_name):
        self.deploy_view.grid_forget()
        self.history_view.grid_forget()
        self.settings_view.grid_forget()

        default_color = ["#3B8ED0", "#1F6AA5"]
        self.nav_deploy_btn.configure(fg_color=default_color if view_name == "deploy" else "transparent")
        self.nav_history_btn.configure(fg_color=default_color if view_name == "history" else "transparent")
        self.nav_settings_btn.configure(fg_color=default_color if view_name == "settings" else "transparent")

        if view_name == "deploy":
            self.update_url_preview()
            self.deploy_view.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        elif view_name == "history":
            self.refresh_history_list()
            self.history_view.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        elif view_name == "settings":
            self.settings_view.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

    def _build_main_views(self):
        self._build_deploy_view()
        self._build_history_view()
        self._build_settings_view()

    def _build_deploy_view(self):
        self.deploy_view = ctk.CTkFrame(self, fg_color="transparent")
        self.deploy_view.grid_columnconfigure(0, weight=5)
        self.deploy_view.grid_columnconfigure(1, weight=6)
        self.deploy_view.grid_rowconfigure(0, weight=1)

        left_box = ctk.CTkFrame(self.deploy_view, corner_radius=12)
        left_box.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left_box, text="Proje & Isimlendirme Paneli",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")

        ctk.CTkLabel(left_box, text="1. Yuklenecek Proje Klasoru:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, columnspan=2, padx=15, pady=(5, 2), sticky="w")
        self.folder_entry = ctk.CTkEntry(left_box, placeholder_text="Klasor secmek icin Gozat'a tiklayin...")
        self.folder_entry.grid(row=2, column=0, padx=(15, 5), pady=(0, 10), sticky="ew")
        ctk.CTkButton(left_box, text="Gozat", width=85, command=self.browse_folder).grid(row=2, column=1, padx=(0, 15), pady=(0, 10))

        ctk.CTkLabel(
            left_box, text="2. GitHub'da Gorunecek Proje Adi (Siz Yazin):",
            font=ctk.CTkFont(weight="bold"), text_color="#60a5fa"
        ).grid(row=3, column=0, columnspan=2, padx=15, pady=(5, 2), sticky="w")

        self.repo_entry = ctk.CTkEntry(
            left_box, placeholder_text="Projenin GitHub'daki adini buraya yazin (Bos birakirsaniz sorulur)"
        )
        self.repo_entry.grid(row=4, column=0, columnspan=2, padx=15, pady=(0, 2), sticky="ew")
        self.repo_entry.bind("<KeyRelease>", self.update_url_preview)

        self.url_preview_lbl = ctk.CTkLabel(
            left_box, text="Gorunecek Adres: (Proje adi bekleniyor...)",
            font=ctk.CTkFont(size=11), text_color="gray70"
        )
        self.url_preview_lbl.grid(row=5, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="w")

        ctk.CTkLabel(left_box, text="3. Proje Amaci / Kisa Aciklama (Opsiyonel - AI kullanir):", font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, columnspan=2, padx=15, pady=(5, 2), sticky="w")
        self.desc_entry = ctk.CTkEntry(left_box, placeholder_text="Orn: Unity C# ile gelistirdigim 3D hayatta kalma oyunu...")
        self.desc_entry.grid(row=7, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        opts_frame = ctk.CTkFrame(left_box, fg_color="transparent")
        opts_frame.grid(row=8, column=0, columnspan=2, padx=15, pady=5, sticky="ew")
        opts_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(opts_frame, text="Proje Turu (.gitignore):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(0, 5), pady=2, sticky="w")
        self.gitignore_opt = ctk.CTkOptionMenu(opts_frame, values=list(GITIGNORE_TEMPLATES.keys()))
        self.gitignore_opt.set(self.config_data.get("default_template", "Unity (C# / Oyun)"))
        self.gitignore_opt.grid(row=1, column=0, padx=(0, 5), pady=(0, 10), sticky="ew")

        ctk.CTkLabel(opts_frame, text="Depo Gizliligi:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=(5, 0), pady=2, sticky="w")
        self.visibility_opt = ctk.CTkOptionMenu(opts_frame, values=["Public (Herkese Acik)", "Private (Gizli)"])
        self.visibility_opt.set(self.config_data.get("default_visibility", "Public (Herkese Acik)"))
        self.visibility_opt.grid(row=1, column=1, padx=(5, 0), pady=(0, 10), sticky="ew")

        self.mit_license_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(left_box, text="Otomatik MIT Lisansi (LICENSE) Olustur", variable=self.mit_license_var).grid(row=9, column=0, columnspan=2, padx=15, pady=4, sticky="w")

        self.large_file_guard_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(left_box, text="100 MB Ustu Dosya Korumasi (GitHub cokmesini onler)", variable=self.large_file_guard_var).grid(row=10, column=0, columnspan=2, padx=15, pady=4, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(left_box)
        self.progress_bar.grid(row=11, column=0, columnspan=2, padx=15, pady=(12, 5), sticky="ew")
        self.progress_bar.set(0)

        self.ai_btn = ctk.CTkButton(
            left_box, text="1. Projeyi Tara & Profesyonel README Yaz",
            fg_color="#7e22ce", hover_color="#6b21a8", height=42,
            font=ctk.CTkFont(size=14, weight="bold"), command=self.start_readme_generation
        )
        self.ai_btn.grid(row=12, column=0, columnspan=2, padx=15, pady=(8, 8), sticky="ew")

        self.deploy_btn = ctk.CTkButton(
            left_box, text="2. Isim Onayi Al ve GitHub'a Yukle",
            fg_color="#15803d", hover_color="#166534", height=50,
            font=ctk.CTkFont(size=15, weight="bold"), command=self.start_deployment
        )
        self.deploy_btn.grid(row=13, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        right_box = ctk.CTkFrame(self.deploy_view, corner_radius=12)
        right_box.grid(row=0, column=1, sticky="nsew")
        right_box.grid_columnconfigure(0, weight=1)
        right_box.grid_rowconfigure(1, weight=3)
        right_box.grid_rowconfigure(3, weight=2)

        ctk.CTkLabel(
            right_box, text="README.md Dokuman Editoru (Yuklemeden Once Duzenlenebilir)",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(12, 4), sticky="w")

        self.readme_textbox = ctk.CTkTextbox(right_box, font=ctk.CTkFont(family="Consolas", size=12))
        self.readme_textbox.grid(row=1, column=0, padx=15, pady=4, sticky="nsew")

        ctk.CTkLabel(
            right_box, text="Canli Islem & Git Konsolu",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=2, column=0, padx=15, pady=(8, 4), sticky="w")

        self.log_textbox = ctk.CTkTextbox(
            right_box, font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#090d16", text_color="#4ade80"
        )
        self.log_textbox.grid(row=3, column=0, padx=15, pady=(4, 15), sticky="nsew")
        self.log("Sistem hazir. Klasor sectikten sonra projenizin GitHub'da gorunecegi ismi belirleyebilirsiniz.")

    def update_url_preview(self, event=None):
        raw_name = self.repo_entry.get().strip()
        username = self.config_data.get("username") or "kullanici_adi"
        if raw_name:
            clean_name = self.format_github_repo_name(raw_name)
            self.url_preview_lbl.configure(
                text=f"Gorunecek Adres: https://github.com/{username}/{clean_name}",
                text_color="#4ade80"
            )
        else:
            self.url_preview_lbl.configure(
                text="Gorunecek Adres: (Proje adi yazmaniz bekleniyor...)",
                text_color="gray70"
            )

    def _build_history_view(self):
        self.history_view = ctk.CTkFrame(self, corner_radius=12)
        self.history_view.grid_columnconfigure(0, weight=1)
        self.history_view.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.history_view, text="Yuklenen Projeler Gecmisi",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.history_scroll = ctk.CTkScrollableFrame(self.history_view, corner_radius=8)
        self.history_scroll.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.history_scroll.grid_columnconfigure(0, weight=1)

    def refresh_history_list(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        if not self.history_data:
            ctk.CTkLabel(
                self.history_scroll, text="Henuz bu panel uzerinden yuklenmis bir proje bulunmuyor.",
                text_color="gray70", font=ctk.CTkFont(size=14)
            ).grid(row=0, column=0, pady=40)
            return

        for idx, item in enumerate(reversed(self.history_data)):
            card = ctk.CTkFrame(self.history_scroll, corner_radius=8)
            card.grid(row=idx, column=0, padx=10, pady=6, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            title_text = f"{item.get('repo_name')}  ({item.get('visibility')})  -  {item.get('date')}"
            ctk.CTkLabel(card, text=title_text, font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
            ctk.CTkLabel(card, text=item.get("description", ""), text_color="gray80").grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

            url = item.get("url", "")
            if url:
                ctk.CTkButton(
                    card, text="Tarayicida Ac", width=130,
                    command=lambda u=url: webbrowser.open(u)
                ).grid(row=0, column=1, rowspan=2, padx=15, pady=10)

    def _build_settings_view(self):
        self.settings_view = ctk.CTkFrame(self, corner_radius=12)
        self.settings_view.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.settings_view, text="Kalici Uygulama Ayarlari & Hesap Hafizasi",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, padx=25, pady=(25, 5), sticky="w")

        ctk.CTkLabel(
            self.settings_view,
            text="Buraya girdiginiz bilgiler bilgisayarinizda guvenli olarak saklanir. Uygulamayi her actiginizda tekrar girmeniz gerekmez.",
            text_color="gray70"
        ).grid(row=1, column=0, padx=25, pady=(0, 20), sticky="w")

        form = ctk.CTkFrame(self.settings_view, corner_radius=10)
        form.grid(row=2, column=0, padx=25, pady=10, sticky="ew")
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="GitHub Kullanici Adiniz:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=(15, 2), sticky="w")
        self.set_username = ctk.CTkEntry(form, placeholder_text="Orn: kullaniciadiniz")
        self.set_username.insert(0, self.config_data.get("username", ""))
        self.set_username.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form, text="GitHub Personal Access Token ('repo' yetkili):", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=20, pady=(5, 2), sticky="w")
        self.set_token = ctk.CTkEntry(form, placeholder_text="ghp_xxxxxxxxxxxxxxxxxxxxxxxx", show="*")
        self.set_token.insert(0, self.config_data.get("token", ""))
        self.set_token.grid(row=3, column=0, padx=20, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(form, text="Gemini API Key (Otomatik AI README yazimi icin):", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=20, pady=(5, 2), sticky="w")
        self.set_gemini = ctk.CTkEntry(form, placeholder_text="AIzaSyxxxxxxxxxxxxxxxxxxxxxx", show="*")
        self.set_gemini.insert(0, self.config_data.get("gemini_key", ""))
        self.set_gemini.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")

        ctk.CTkButton(
            self.settings_view, text="Ayarlari Bilgisayara Kaydet",
            fg_color="#15803d", hover_color="#166534", height=45,
            font=ctk.CTkFont(size=15, weight="bold"), command=self.save_settings
        ).grid(row=3, column=0, padx=25, pady=15, sticky="w")

    def save_settings(self):
        self.config_data["username"] = self.set_username.get().strip()
        self.config_data["token"] = self.set_token.get().strip()
        self.config_data["gemini_key"] = self.set_gemini.get().strip()
        self.config_data["default_template"] = self.gitignore_opt.get()
        self.config_data["default_visibility"] = self.visibility_opt.get()

        self.save_json(CONFIG_FILE, self.config_data)
        self.update_sidebar_status()
        self.log("Kullanici ayarlari ve API anahtarlari kalici hafizaya kaydedildi.")
        messagebox.showinfo("Kaydedildi", "Ayarlariniz basariyla kaydedildi!")
        self.show_view("deploy")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder_selected)

            self.repo_entry.delete(0, "end")
            self.update_url_preview()
            self.repo_entry.focus()
            self.log(f"Klasor secildi: {folder_selected}")
            self.log("Lutfen 2. kutucuga projenin GitHub'da gorunecegi ismi yazin.")

            files_in_dir = os.listdir(folder_selected)
            if "Assets" in files_in_dir and "ProjectSettings" in files_in_dir:
                self.gitignore_opt.set("Unity (C# / Oyun)")
                self.log("Unity projesi algilandi! '.gitignore' otomatik olarak ayarlandi.")
            elif any(f.endswith(".uproject") for f in files_in_dir):
                self.gitignore_opt.set("Unreal Engine / 3D")
                self.log("Unreal Engine projesi algilandi!")
            elif "package.json" in files_in_dir:
                self.gitignore_opt.set("Web / Full-Stack")
                self.log("Web / Node.js projesi algilandi!")
            elif any(f.endswith((".ino", "platformio.ini")) for f in files_in_dir):
                self.gitignore_opt.set("C++ / Arduino / ESP32")
                self.log("Gomulu Sistem (Arduino/ESP32) projesi algilandi!")
            elif any(f.endswith((".py", ".ipynb")) for f in files_in_dir):
                self.gitignore_opt.set("Python / AI & Data")
                self.log("Python / AI projesi algilandi!")

    def ask_repo_name_if_empty(self):
        raw_name = self.repo_entry.get().strip()
        if not raw_name:
            dialog = ctk.CTkInputDialog(
                text="Projeniz GitHub'da hangi isimle gorunsun?\n(Orn: Benim Oyun Projem veya siber-analiz-araci):",
                title="Proje Ismi Belirleyin"
            )
            user_input = dialog.get_input()
            if not user_input or not user_input.strip():
                return None
            raw_name = user_input.strip()

        clean_name = self.format_github_repo_name(raw_name)
        self.repo_entry.delete(0, "end")
        self.repo_entry.insert(0, clean_name)
        self.update_url_preview()
        return clean_name

    def scan_project_structure(self, root_dir):
        ignore_dirs = {
            '.git', 'node_modules', 'Library', 'Temp', 'Obj', 'Build', 'Builds',
            '__pycache__', 'venv', '.venv', '.pio', '.vscode', '.idea', 'Binaries', 'Intermediate'
        }
        file_tree = []
        extensions = set()
        oversized_files = []

        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            rel_path = os.path.relpath(root, root_dir)
            level = 0 if rel_path == "." else rel_path.count(os.sep) + 1

            if level <= 3:
                indent = "  " * level
                folder_name = os.path.basename(root) if rel_path != "." else os.path.basename(root_dir)
                file_tree.append(f"{indent}[DIR] {folder_name}/")

            sub_indent = "  " * (level + 1)
            for idx, f in enumerate(files):
                full_p = os.path.join(root, f)
                try:
                    size_mb = os.path.getsize(full_p) / (1024 * 1024)
                    if size_mb > 95:
                        rel_file = os.path.relpath(full_p, root_dir).replace("\\", "/")
                        oversized_files.append((rel_file, round(size_mb, 1)))
                except OSError:
                    pass

                if level <= 3 and idx < 15:
                    file_tree.append(f"{sub_indent}- {f}")
                _, ext = os.path.splitext(f)
                if ext:
                    extensions.add(ext)

        return "\n".join(file_tree[:85]), ", ".join(sorted(extensions)), oversized_files

    def start_readme_generation(self):
        folder = self.folder_entry.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Uyari", "Lutfen once gecerli bir proje klasoru secin!")
            return

        repo_name = self.ask_repo_name_if_empty()
        if not repo_name:
            self.log("README olusturmak icin proje ismi girilmesi gerekiyor.")
            return

        threading.Thread(target=self._generate_readme_worker, args=(repo_name,), daemon=True).start()

    def _generate_readme_worker(self, repo_name):
        folder = self.folder_entry.get().strip()
        short_desc = self.desc_entry.get().strip() or "Modern yazilim ve teknoloji projesi."
        api_key = self.config_data.get("gemini_key", "").strip()
        username = self.config_data.get("username", "kullanici_adi").strip()
        proj_type = self.gitignore_opt.get()

        self.ai_btn.configure(state="disabled", text="Proje Analiz Ediliyor...")
        self.progress_bar.set(0.3)
        self.log(f"'{repo_name}' icin proje dosyalari analiz ediliyor...")
        tree_str, ext_str, oversized = self.scan_project_structure(folder)

        bt = chr(96) * 3

        if api_key and GEMINI_AVAILABLE:
            try:
                self.log("Gemini AI ile projeye ozel README.md olusturuluyor...")
                client = genai.Client(api_key=api_key)
                prompt_lines = [
                    "Sen kidemli bir yazilim muhendisisin. Asagidaki proje icin Turkce, son derece profesyonel, GitHub standartlarinda kusursuz bir README.md hazirla.",
                    f"Proje Adi (GitHub'daki Isim): {repo_name}",
                    f"Gelistirici GitHub Kullanici Adi: {username}",
                    f"Proje Kategorisi: {proj_type}",
                    f"Proje Aciklamasi: {short_desc}",
                    f"Projede Bulunan Dosya Uzantilari: {ext_str}",
                    "Klasor Agaci Ozeti:",
                    tree_str,
                    "README sunlari icersin: Baslik, Shields.io rozetleri, Proje Hakkinda, Temel Ozellikler, Kullanilan Teknolojiler, Proje Dizin Yapisi, Kurulum ve Lisans.",
                    "Sadece dogrudan README.md icine kaydedilecek Markdown metnini dondur."
                ]
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="\n".join(prompt_lines)
                )
                readme_content = response.text.strip()
                if readme_content.startswith(bt + "markdown"):
                    readme_content = readme_content[len(bt + "markdown"):].strip()
                elif readme_content.startswith(bt):
                    readme_content = readme_content[3:].strip()
                if readme_content.endswith(bt):
                    readme_content = readme_content[:-3].strip()

                self.readme_textbox.delete("1.0", "end")
                self.readme_textbox.insert("1.0", readme_content)
                self.progress_bar.set(1.0)
                self.log("Yapay zeka destekli README.md basariyla olusturuldu!")
                self.ai_btn.configure(state="normal", text="1. Projeyi Tara & Profesyonel README Yaz")
                return
            except Exception as e:
                self.log(f"Gemini API uyarisi ({e}). Standart profesyonel sablona geciliyor...")

        badge_type = proj_type.split("(")[0].strip().replace(" ", "%20")
        ext_info = ext_str if ext_str else "Standart Proje Dosyalari"
        fallback_lines = [
            f"# {repo_name}",
            "",
            f"![Kategori](https://img.shields.io/badge/Kategori-{badge_type}-blue?style=for-the-badge)",
            "![Lisans](https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge)",
            "![Durum](https://img.shields.io/badge/Durum-Aktif-success?style=for-the-badge)",
            "",
            "## Proje Hakkinda",
            f"**{repo_name}**, {short_desc}",
            "",
            "Bu proje modern yazilim gelistirme standartlari ve temiz dosya mimarisiyle yapilandirilmistir.",
            "",
            "---",
            "",
            "## Teknoloji Yigini & Dosya Yapisi",
            f"* **Proje Altyapisi:** `{proj_type}`",
            f"* **Tespit Edilen Kaynak Uzantilari:** `{ext_info}`",
            "",
            "---",
            "",
            "## Proje Dizin Agaci",
            f"{bt}text",
            tree_str,
            bt,
            "",
            "---",
            "",
            "## Kurulum ve Calistirma",
            "Projeyi yerel ortaminiza klonlamak icin:",
            f"{bt}bash",
            f"git clone https://github.com/{username}/{repo_name}.git",
            f"cd {repo_name}",
            bt,
            "",
            "---",
            "",
            "## Lisans",
            "Bu proje **MIT Lisansi** altinda lisanslanmistir."
        ]
        fallback_readme = "\n".join(fallback_lines)
        self.readme_textbox.delete("1.0", "end")
        self.readme_textbox.insert("1.0", fallback_readme)
        self.progress_bar.set(1.0)
        self.log("Profesyonel README.md hazirlandi.")
        self.ai_btn.configure(state="normal", text="1. Projeyi Tara & Profesyonel README Yaz")

    def run_git_cmd(self, args, cwd):
        cmd_str = "git " + " ".join(args)
        safe_log = cmd_str if "@" not in cmd_str else "git remote (Kimlik dogrulama baglantisi)"
        self.log(f"Calistiriliyor: {safe_log}")

        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        process = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creation_flags
        )
        if process.returncode != 0:
            err_msg = process.stderr.strip() or process.stdout.strip()
            raise RuntimeError(f"Git Komut Hatasi ({safe_log}):\n{err_msg}")
        return process.stdout.strip()

    def start_deployment(self):
        username = self.config_data.get("username", "").strip()
        token = self.config_data.get("token", "").strip()
        folder = self.folder_entry.get().strip()

        if not username or not token:
            messagebox.showwarning(
                "Hesap Bilgisi Eksik",
                "Lutfen sol menudeki 'Ayarlar & Hafiza' sekmesine giderek GitHub Kullanici Adi ve Token bilginizi kaydedin!"
            )
            self.show_view("settings")
            return

        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Eksik Bilgi", "Lutfen once yuklenecek Proje Klasorunu secin!")
            return

        repo_name = self.ask_repo_name_if_empty()
        if not repo_name:
            self.log("Proje ismi belirlenmedigi icin yukleme iptal edildi.")
            return

        confirm = messagebox.askyesno(
            "GitHub Proje Ismi Onayi",
            f"Projeniz GitHub'da asagidaki isim ve adresle yayinlanacaktir:\n\n"
            f"Proje Adi:  {repo_name}\n"
            f"GitHub Adresi:  https://github.com/{username}/{repo_name}\n\n"
            f"Bu isimle yuklemeyi baslatmak istiyor musunuz?"
        )
        if not confirm:
            self.log("Isim onayi iptal edildi. 2. kutucuktan ismi degistirip tekrar deneyebilirsiniz.")
            self.repo_entry.focus()
            return

        threading.Thread(target=self._deploy_worker, args=(repo_name,), daemon=True).start()

    def _deploy_worker(self, repo_name):
        username = self.config_data.get("username", "").strip()
        token = self.config_data.get("token", "").strip()
        folder = self.folder_entry.get().strip()
        short_desc = self.desc_entry.get().strip()
        is_private = "Private" in self.visibility_opt.get()
        gitignore_type = self.gitignore_opt.get()

        self.deploy_btn.configure(state="disabled", text="GitHub'a Yukleniyor...")
        self.progress_bar.set(0.1)

        try:
            self.log("==========================================")
            self.log(f"'{repo_name}' adiyla otomatik yukleme baslatildi...")

            readme_text = self.readme_textbox.get("1.0", "end").strip()
            if not readme_text:
                self._generate_readme_worker(repo_name)
                readme_text = self.readme_textbox.get("1.0", "end").strip()

            with open(os.path.join(folder, "README.md"), "w", encoding="utf-8") as f:
                f.write(readme_text)
            self.progress_bar.set(0.25)

            _, _, oversized_files = self.scan_project_structure(folder)
            gitignore_path = os.path.join(folder, ".gitignore")

            base_gitignore = GITIGNORE_TEMPLATES.get(gitignore_type, GITIGNORE_TEMPLATES["Genel (Standart)"])
            if os.path.exists(gitignore_path):
                with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                    base_gitignore = f.read()

            if self.large_file_guard_var.get() and oversized_files:
                guard_lines = [""]
                for rel_f, mb in oversized_files:
                    if rel_f not in base_gitignore:
                        guard_lines.append(rel_f)
                        self.log(f"Koruma: '{rel_f}' ({mb} MB) 100MB sinirini asmamak icin filtrelendi.")
                base_gitignore += "\n" + "\n".join(guard_lines) + "\n"

            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(base_gitignore)
            self.progress_bar.set(0.4)

            if self.mit_license_var.get():
                license_path = os.path.join(folder, "LICENSE")
                if not os.path.exists(license_path):
                    with open(license_path, "w", encoding="utf-8") as f:
                        f.write(f"MIT License\n\nCopyright (c) {datetime.now().year} {username}\n")

            self.log(f"GitHub sunucusunda '{repo_name}' deposu olusturuluyor...")
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            payload = {
                "name": repo_name,
                "description": short_desc,
                "private": is_private,
                "auto_init": False
            }
            resp = requests.post("https://api.github.com/user/repos", json=payload, headers=headers, timeout=15)

            if resp.status_code == 201:
                self.log(f"GitHub'da '{repo_name}' deposu acildi.")
            elif resp.status_code == 422:
                self.log(f"'{repo_name}' deposu zaten mevcut, uzerine guncellenecek.")
            elif resp.status_code == 401:
                raise RuntimeError("GitHub Token hatali veya suresi dolmus! Ayarlar sekmesinden kontrol edin.")
            else:
                raise RuntimeError(f"GitHub API Hatasi ({resp.status_code}): {resp.text}")

            self.progress_bar.set(0.6)

            if not os.path.exists(os.path.join(folder, ".git")):
                self.run_git_cmd(["init"], folder)

            try:
                self.run_git_cmd(["config", "user.name"], folder)
            except Exception:
                self.run_git_cmd(["config", "user.name", username], folder)
                self.run_git_cmd(["config", "user.email", f"{username}@users.noreply.github.com"], folder)

            self.run_git_cmd(["branch", "-M", "main"], folder)
            self.run_git_cmd(["add", "."], folder)

            status_out = self.run_git_cmd(["status", "--porcelain"], folder)
            if status_out:
                self.run_git_cmd(["commit", "-m", f"chore: deploy {repo_name} via GitHub Pro Studio"], folder)
            self.progress_bar.set(0.8)

            auth_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
            clean_url = f"https://github.com/{username}/{repo_name}.git"

            remotes = self.run_git_cmd(["remote"], folder).splitlines()
            if "origin" in remotes:
                self.run_git_cmd(["remote", "set-url", "origin", auth_url], folder)
            else:
                self.run_git_cmd(["remote", "add", "origin", auth_url], folder)

            self.log("Dosyalar GitHub'a yukleniyor (Push)...")
            self.run_git_cmd(["push", "-u", "origin", "main", "--force"], folder)
            self.run_git_cmd(["remote", "set-url", "origin", clean_url], folder)

            self.progress_bar.set(1.0)
            self.log(f"BASARILI! Proje adresi: {clean_url}")

            self.history_data.append({
                "repo_name": repo_name,
                "description": short_desc or "Aciklama girilmedi",
                "visibility": "Private" if is_private else "Public",
                "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "url": clean_url
            })
            self.save_json(HISTORY_FILE, self.history_data)

            if messagebox.askyesno("Yukleme Tamamlandi!", f"Projeniz '{repo_name}' adiyla GitHub'a yuklendi!\n\n{clean_url}\n\nSimdi tarayicida acmak ister misiniz?"):
                webbrowser.open(clean_url)

        except Exception as e:
            self.progress_bar.set(0)
            self.log(f"HATA: {e}")
            messagebox.showerror("Hata Olustu", str(e))
        finally:
            self.deploy_btn.configure(state="normal", text="2. Isim Onayi Al ve GitHub'a Yukle")


if __name__ == "__main__":
    app = GitHubProStudio()
    app.mainloop()