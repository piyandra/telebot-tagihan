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
                        bot.reply_to(message, "Id {} Sudah ada. Berakhir pada {}".format(id_tele, time.ctime(data[2])))
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
                                              f'Nama \t\t\t\t: {i[0]}\n'
                                              f'Alamat \t\t: {i[1]}\n'
                                              f'SPK \t\t\t\t\t\t\t\t: {i[2]}\n'
                                              f'Plafond \t: {babel.numbers.format_currency(int(i[3]), 'IDR',
                                                                                           locale="id_ID")}')
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
