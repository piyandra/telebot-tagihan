# Bot Telegram Tagihan

## Fitur

- Mendappatkan Info SPK
- Mendapatkan Info Pelunasan
- Chat admin langsung jika terjadi problem
- Fitur lain akan ditambahkan


## SETUP

### Setup Bot

- Ke @BotFather di Telegram untuk mendapatkan Bot Token
- Dapatkan Token dan paste pada config.py
- Masukkan text berikut untuk Akses Cepat Menu
```
id - Untuk Melihat ID lawan bicara
izinkan - Izinkan member baru yang dapat menggunakan bot
spk - Untuk mencari SPK berdasarkan nama dan kantor
info - Untuk mendapatkan detail spk
pelunasan - Untuk mendapatkan detail pelunasan
```

### Setup Database

- Lihat pada database.uml untuk schema yang digunakan
- Lalu masukkan id anda pada tabel member dengan role admin dan masukkan masa berlaku dengan format epoch unix time.
- Isi variabel di config.py.


### Setup Python
- Install semua requirement di requirements.txt
- Jalankan main.py


