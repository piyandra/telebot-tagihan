import json
import query
import babel.numbers
import mysql.connector
import telebot
import time
import config

db = mysql.connector.connect(host=config.DB_HOST,
                             port="3306",
                             username=config.DB_USER,
                             password=config.DB_PASSWORD,
                             database=config.DB)

bot = telebot.TeleBot(config.API_KEY)
cursor = db.cursor()


@bot.message_handler(commands=['start'])
def start(message):
    try:
        data = query.cek_aktif(message.chat.id)
        if data[0] > time.time():
            bot.send_message(message.chat.id, "Akun Anda Aktif")
        else:
            bot.send_message(message.chat.id, "Akun Anda Sudah Kadaluarsa")
            try:
                query.delete_db(message.chat.id)
            except TypeError:
                print("Sudah Tidak Ada")
    except TypeError:
        bot.send_message(message.chat.id, "AKun Anda Tidak Ditemukan di Database")


@bot.message_handler(commands=['izinkan'])
def izinkan(message):
    try:
        if query.role(message.chat.id) is not None:
            try:
                identitas = message.text.split(' ')
                id_tele = identitas[1]
                role = query.role(message.chat.id)
                if role[1] == "admin":
                    try:
                        if query.addmember(id_tele) == 1:
                            bot.reply_to(message, "Berhasil Menambah {}".format(id_tele))
                        else:
                            bot.reply_to(message, "Gagal Ditambahkan")
                    except mysql.connector.errors.IntegrityError:
                        data = query.role(id_tele)
                        bot.reply_to(message, "Id {} Sudah ada. Berakhir pada {}".format(id_tele,
                                                                                         time.ctime(data[2])))
                else:
                    bot.reply_to(message, "Anda Bukan Admin. Tidak Bisa Menambah {}".format(id_tele))
            except IndexError:
                bot.send_message(message.chat.id, "Untuk Mengizinkan Member Baru")
        else:
            bot.reply_to(message, "Anda Bukan Admin")
    except mysql.connector.errors.ProgrammingError as err:
        bot.send_message(message.chat.id, "Kesalahan DataBase")
        print(err)
    except mysql.connector.errors.DatabaseError as err:
        bot.send_message(message.chat.id, "Error")
        print(err)


@bot.message_handler(commands=['spk'])
def spk(message):
    try:
        namanya = message.text.split(' ')
        nama = namanya[1]
        kantor = namanya[2]
        data = query.cek_aktif(message.chat.id)
        try:
            if data[0] > time.time():
                hasil = query.nama(nama, kantor)
                if len(hasil) > 0:
                    for i in hasil:
                        bot.reply_to(message, f'{10 * "-"}\n'
                                              f'Nama \t\t\t\t: <b>{i[0]}</b>\n'
                                              f'Alamat \t\t: {i[1]}\n'
                                              f'SPK \t\t\t\t\t\t\t\t: <code>{i[2]}</code>\n'
                                              f'Plafond \t: {babel.numbers.format_currency(int(i[3]), 'IDR',
                                                                                           locale="id_ID")}',
                                     parse_mode="HTML")
                else:
                    bot.reply_to(message, "Tidak Ditemukan")
            else:
                bot.reply_to(message, "Akun Anda Sudah Tidak Aktif, tidak bisa menggunakan perintah {}".format(message))
        except TypeError:
            bot.reply_to(message, "Anda Tidak Diizinkan")
    except IndexError:
        bot.reply_to(message, "Ini Untuk Mencari SPK Berdasarkan Nama dan Kantor\n"
                              "\nPenggunaa /spk {nama} {kode_kantor}")


@bot.message_handler(commands=['cekspk'])
def cek_spk(message):
    try:
        data = query.cek_aktif(message.chat.id)
        pesan = message.text.split(' ')
        no_pk = pesan[1]
        try:
            if data[0] > time.time():
                hasil = query.cek_pk(no_pk)
                try:
                    if len(hasil) > 0:
                        bot.reply_to(message,
                                     f'{10 * "-"}\nCIF\t: {hasil[0]}\nNo PK\t : {hasil[3]}\nProduk\t: {hasil[5]}\nNama '
                                     f'\t: {hasil[6]}\nAlamat\t: {hasil[7]}\nRL\t: {hasil[9]}\nJT'
                                     f': {hasil[10]}\nOD\t: {hasil[12]}\nPlafond\t: '
                                     f'{babel.numbers.format_currency(hasil[13], "IDR", locale="id_ID")}\nBD\t: '
                                     f'{babel.numbers.format_currency(hasil[14], "IDR", locale="id_ID")}')
                    else:
                        bot.reply_to(message, "Tidak Ditemukan")
                except TypeError:
                    bot.send_message(message.chat.id, "Tidak Ditemukan")
            else:
                bot.reply_to(message, "Akun Anda Tidak Aktif")
        except IndexError:
            bot.send_message(message.chat.id, "Untuk Detail SPK")
    except IndexError:
        bot.send_message(message.chat.id, "Untuk Mencari Detail SPK")


@bot.message_handler(commands=['id'])
def lapor_min(message):
    try:
        bot.send_message(message.chat.id, message.json['reply_to_message']['forward_from']['id'])
    except KeyError:
        bot.send_message(message.chat.id, "Jangan Dikerjain Bang, Servernya Kecil, Kasian")


@bot.message_handler(commands=['info'])
def info(message):

        data = query.cek_aktif(message.chat.id)  # Cari Data Member
        if data[0] > time.time():  # Data Member Aktif
            try:
                split = message.text.split(' ')  # Query From text
                no_pk = split[1]  # Query From text/info
                kueri = query.cek_pk(no_pk)  # Query From text
                if kueri is not None:  # Hasil Tidak Kosong
                    bot.send_message(message.chat.id,
                                     f'{10*"="}\n'
                                     f'<b>CIF</b> : {kueri[0]}\nNama \t: {kueri[6]}\nNo SPK: {kueri[3]}\nProduk : {kueri[5]}\n'
                                     f'<b>Alamat</b> : {kueri[7]}\n\n'
                                     f'{10*"="}\n'
                                     f'<b>Plafond</b> : {babel.numbers.format_currency(kueri[13], "IDR", locale="id_ID")}\n'
                                     f'<b>Bakidebet</b> : {babel.numbers.format_currency(kueri[14], "IDR", locale="id_ID")}\n'
                                     f'<b>RL</b> : {kueri[9]}\n'
                                     f'<b>JT</b> : {kueri[10]}\n\n'
                                     f'{10*"="}\n'
                                     f'<b>Lama Tunggakan</b> : {kueri[12]}\n'
                                     f'<b>Pokok</b> : {babel.numbers.format_currency(kueri[15], "IDR", locale="id_ID")}\n'
                                     f'<b>Bunga</b> : {babel.numbers.format_currency(kueri[16], "IDR", locale="id_ID")}\n'
                                     f'<b>Angsuran</b> : {babel.numbers.format_currency(kueri[17], "IDR", locale="id_ID")}\n'
                                     f'<b>Tunggakan Pokok</b> : {babel.numbers.format_currency(kueri[18], "IDR", locale="id_ID")}\n'
                                     f'<b>Tunggakan Bunga</b> : {babel.numbers.format_currency(kueri[19], "IDR", locale="id_ID")}\n\n'
                                     f'{10*"="}\n'
                                     f'<b>Minimal Pokok</b>: {babel.numbers.format_currency(kueri[22], "IDR", locale="id_ID")}\n'
                                     f'<b>Minimal Bunga</b> : {babel.numbers.format_currency(kueri[23], "IDR", locale="id_ID")}\n'
                                     f'<b>Denda</b> : {babel.numbers.format_currency(kueri[24] + kueri[25], "IDR", locale="id_ID")}\n'
                                     f'<b>AO</b> : {kueri[26]}', parse_mode='HTML')
                else:  # Hasil Kosong
                    bot.reply_to(message, "Kosong Mad")
            except IndexError:  # Tidak ada Text, Hanya Command
                bot.send_message(message.chat.id, "Untuk Mencari Detail SPK")
        else:  # Waktu di DB sudah lewat
            bot.reply_to(message, "Akun Anda Sudah Tidak Aktif")


@bot.message_handler(func=lambda message: True, content_types=['photo'])
def id_gen(message):
    if message.chat.id != 6777074285:
        try:
            bot.forward_message(chat_id=6777074285, from_chat_id=message.chat.id, message_id=message.id)
        except ConnectionAbortedError:
            print("gagal")
    else:
        json_data = json.dumps(message.json, indent=4)
        print(json_data)
        print(message.text)
        bot.send_message(chat_id=message.json['reply_to_message']['forward_from']['id'], text=message.text)


@bot.message_handler(func=lambda message: True)
def id_gen(message):
    if message.chat.id != 6777074285:
        try:
            bot.forward_message(chat_id=6777074285, from_chat_id=message.chat.id, message_id=message.id)
        except ConnectionAbortedError:
            print("gagal")
    else:
        json_data = json.dumps(message.json, indent=4)
        print(json_data)
        print(message.text)
        bot.send_message(chat_id=message.json['reply_to_message']['forward_from']['id'], text=message.text)


while True:
    try:
        bot.polling()
    except ConnectionAbortedError:
        continue
