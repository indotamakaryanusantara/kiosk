#!/bin/bash

# Ambil nilai status dari JSON (menggunakan grep agar tanpa install library tambahan)
STATUS=$(grep -o '"status": "[^"]*' /home/pi/config.json | cut -d'"' -f4)

if [ "$STATUS" == "aktif" ]; then
    # Jika sudah aktif, langsung jalankan aplikasi Golf (RFID)
    /usr/bin/python3 /home/pi/main.py
else
    # Jika belum aktif, paksa masuk ke layar Setup
    /usr/bin/python3 /home/pi/setup_kiosk.py
fi