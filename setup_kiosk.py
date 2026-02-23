import tkinter as tk
import subprocess
import time
import json
import os

CONFIG_FILE = "/home/pi/config.json"

class SetupApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.config(cursor="none")

        self.frame = tk.Frame(self.root, bg='black')
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_status = tk.Label(self.frame, text="Memulai Sistem...", fg="#00FF00", bg="black", font=("Helvetica", 20, "bold"))
        self.lbl_status.pack(pady=20)

        # Mulai pengecekan setelah 1 detik
        self.root.after(1000, self.check_network)

    def check_network(self):
        self.lbl_status.config(text="Mengecek Koneksi Internet...")
        self.root.update()

        # Ping ke Cloudflare DNS
        try:
            subprocess.check_output(["ping", "-c", "1", "1.1.1.1"], timeout=3)
            # Jika tembus, langsung ke layar aktivasi
            self.show_activation()
        except Exception:
            # Jika gagal, masuk ke setup Wi-Fi
            self.show_wifi_setup()

    def show_wifi_setup(self):
        self.clear_frame()
        tk.Label(self.frame, text="KONEKSI TERPUTUS", fg="red", bg="black", font=("Helvetica", 24, "bold")).pack(pady=(0, 20))
        tk.Label(self.frame, text="Mencari jaringan Wi-Fi...", fg="yellow", bg="black", font=("Helvetica", 14)).pack()
        self.root.update()

        # Scan Wi-Fi menggunakan nmcli
        ssid_list = []
        try:
            scan = subprocess.check_output(["nmcli", "-t", "-f", "SSID", "dev", "wifi", "list"], timeout=10).decode('utf-8')
            ssid_list = list(set([s for s in scan.split('\n') if s.strip() != ""]))
        except:
            ssid_list = ["Gagal scan Wi-Fi"]

        self.clear_frame()
        tk.Label(self.frame, text="PILIH WI-FI", fg="white", bg="black", font=("Helvetica", 24, "bold")).pack(pady=(0, 20))

        self.var_ssid = tk.StringVar(self.frame)
        if ssid_list: self.var_ssid.set(ssid_list[0])

        tk.OptionMenu(self.frame, self.var_ssid, *ssid_list).pack(pady=10)

        tk.Label(self.frame, text="Password:", fg="white", bg="black", font=("Helvetica", 14)).pack(pady=(10,0))
        self.ent_pwd = tk.Entry(self.frame, show="*", font=("Helvetica", 14), width=30, justify="center")
        self.ent_pwd.pack(pady=10)
        self.ent_pwd.focus()

        tk.Button(self.frame, text="HUBUNGKAN", font=("Helvetica", 14, "bold"), bg="#2e8b57", fg="white", command=self.connect_wifi).pack(pady=20)

    def connect_wifi(self):
        ssid = self.var_ssid.get()
        pwd = self.ent_pwd.get()

        self.clear_frame()
        tk.Label(self.frame, text=f"Menghubungkan ke '{ssid}'...", fg="yellow", bg="black", font=("Helvetica", 20)).pack(pady=20)
        self.root.update()

        try:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid, "password", pwd]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                self.check_network() # Cek ulang internet
            else:
                tk.Label(self.frame, text="Gagal Terhubung!", fg="red", bg="black", font=("Helvetica", 20)).pack(pady=20)
                tk.Button(self.frame, text="Coba Lagi", command=self.show_wifi_setup).pack()
        except Exception as e:
            tk.Label(self.frame, text=f"Error: {e}", fg="red", bg="black").pack()

    def show_activation(self):
        self.clear_frame()
        tk.Label(self.frame, text="INTERNET TERHUBUNG", fg="#00FF00", bg="black", font=("Helvetica", 18)).pack(pady=(0, 10))
        tk.Label(self.frame, text="AKTIVASI PERANGKAT", fg="white", bg="black", font=("Helvetica", 28, "bold")).pack(pady=(0, 20))

        tk.Label(self.frame, text="Masukkan Kode Cabang / Aktivasi:", fg="white", bg="black", font=("Helvetica", 14)).pack(pady=(10,0))
        self.ent_code = tk.Entry(self.frame, font=("Helvetica", 24, "bold"), width=15, justify="center")
        self.ent_code.pack(pady=10)
        self.ent_code.focus()

        tk.Button(self.frame, text="AKTIFKAN", font=("Helvetica", 16, "bold"), bg="#0066cc", fg="white", command=self.process_activation).pack(pady=20)

    def process_activation(self):
        kode = self.ent_code.get()
        # Logika integrasi ke Cloudflare D1 nantinya ada di sini.
        # Untuk testing, kita anggap kode "12345" adalah valid.
        if kode == "12345":
            self.clear_frame()
            tk.Label(self.frame, text="AKTIVASI BERHASIL!", fg="#00FF00", bg="black", font=("Helvetica", 24, "bold")).pack(pady=20)
            self.root.update()

            # Tulis ke config.json agar mesin ingat
            data = {"device_id": "TD-GOLF-001", "status": "aktif"}
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)

            time.sleep(2)
            self.root.destroy() # Tutup aplikasi setup, kembalikan kontrol ke bash
        else:
            tk.Label(self.frame, text="Kode Tidak Valid!", fg="red", bg="black", font=("Helvetica", 14)).pack()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SetupApp(root)
    root.bind("<Escape>", lambda e: root.destroy())
    root.mainloop()