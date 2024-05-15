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
            bot.send_message(message.chat.id, "<b>✔Bot Aktif.</b>\n"
                                              "Akun anda dengan ID <b>{}</b> berakhir pada\n"
                                              "{}\n"
                                              "<b>Silahakan ketik /tolong untuk minta bantuan</b>".format(message.chat.id, time.ctime(data[2], )), parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "Akune rika kadaluarsa yung, ora teyeng nganggo. tek hapus bae ya")
            try:
                query.delete_db(message.chat.id)
            except TypeError:
                bot.send_message(message.chat.id, "Akune rika uis ilang")
    except TypeError:
        bot.send_message(message.chat.id, "Akune rika domongi wis ilang")


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
                            bot.reply_to(message, "Gagal menabah {}".format(id_tele))
                    except mysql.connector.errors.IntegrityError:
                        data = query.role(id_tele)
                        bot.reply_to(message, "Id {} Sudah ada. Berakhir pada {}".format(id_tele,
                                                                                         time.ctime(data[2])))
                else:
                    bot.reply_to(message, "Anda bukan admin. Tidak bisa menambah {}\nSilahkan hubungi admin anda".format(id_tele))
            except IndexError:
                bot.send_message(message.chat.id, "Menu ini digunakan untuk menambah member baru...")
        else:
            bot.reply_to(message, "<strong>Anda Bukan Admin!!!</strong>", parse_mode="HTML")
    except mysql.connector.errors.ProgrammingError as err:
        bot.send_message(message.chat.id, "Kesalahan database, silahkan hubugi admin anda")
    except mysql.connector.errors.DatabaseError as err:
        bot.send_message(message.chat.id, "Error")


@bot.message_handler(commands=['spk'])
def spk(message):
    try:
        namanya = message.text.split(' ')
        nama = namanya[1:len(namanya)-1]
        hasil_nama = ' '.join(nama)
        kantor = namanya[-1]
        data = query.cek_aktif(message.chat.id)
        print(len(hasil_nama))
        try:
            if data[0] > time.time():
                hasil = query.nama(hasil_nama, kantor)
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
                    bot.reply_to(message, "Rika nggolet jenenge <b><code>{}</code>\n</b> ora ketemu nang kantor {}\n"
                                          "Jajal dikoreh koreh maning".format(hasil_nama, kantor), parse_mode="HTML")
            else:
                bot.reply_to(message, "Akune rika uis ora aktif ndean, dadi ora bisa nggolet {}. Jajal jongkongna sing nduwe".format(message))
        except TypeError:
            bot.reply_to(message, "Anda tidak diizinkan menggunakan perintah ini")
    except IndexError:
        bot.reply_to(message, "Kie kue nggo nggolet no spk, jajal si\n"
                              "Kie Carane <b>/spk {nama} {kantor}</b>\n"
                              "Mesti ketemu, nek ora ketemu ya anu spk mandiri mbok, apa bri", parse_mode="HTML")
    except mysql.connector.errors.ProgrammingError:
        bot.send_message(message.chat.id, "Kie kue nggo nggolet no spk, jajal si\n"
                                          "Kie Carane <b>/spk {nama} {kantor}</b>\n"
                                          "Mesti ketemu, nek ora ketemu ya anu spk mandiri mbok, apa bri", parse_mode="HTML")


@bot.message_handler(commands=['pelunasan'])
def cek_lunas(message):
    global bunga_text
    try:
        data = message.text.split(' ')
        spk = data[1]
        lunas = query.pelunasan(spk)
        try:
            if "LM" in lunas[1]:
                if lunas[15] > 12:
                    bunga_text = "Penalty B+1"
                    penalty = lunas[7]
                else:
                    bunga_text = "Penalty B+3"
                    penalty = lunas[7]*3
            elif "DG" in lunas[1]:
                bunga_text = "Penalty B+1"
                penalty = lunas[7]
            else:
                penalty = 0
            bot.send_message(message.chat.id, f'<b>SPK :</b> {lunas[0]}\n'
                                              f'<b>Produk :</b> {lunas[1]}\n'
                                              f'<b>Nama :</b> {lunas[2]}\n'
                                              f'<b>Alamat :</b> {lunas[3]}\n\n'
                                              f'{10*"="}\n'
                                              f'<b>Bakidebet :</b> {babel.numbers.format_currency(lunas[4], "IDR", locale="id_ID")}\n'
                                              f'<b>Tunggakan Bunga :</b> {babel.numbers.format_currency(lunas[5], "IDR", locale="id_ID")}\n'
                                              f'<b>Penalty {bunga_text} :</b> {babel.numbers.format_currency(penalty, "IDR", locale="id_ID")}\n'
                                              f'<b>Denda :</b> {babel.numbers.format_currency(lunas[8], "IDR", locale="id_ID")}\n\n'
                                              f'{10*"="}\n'
                                              f'<b>Total Pelunasan :</b> {babel.numbers.format_currency(lunas[4]+lunas[5]+penalty+lunas[8], "IDR", locale="id_ID")}', parse_mode="HTML")
        except TypeError:
            bot.send_message(message.chat.id, "SPK Tidak Ditemukan. <b>Periksa Nomor SPK ANDA</b>", parse_mode="HTML")
    except IndexError:
        bot.send_message(message.chat.id, "Menu ini digunakan untuk menghitung pelunasan kredit\n"
                                          "<b>Disclaimer:</b>\n"
                                          "Menu ini tidak bisa menghitung pelunasan dengan kriteria:\n"
                                          "<b>1. Kredit Potong Gaji</b>\n"
                                          "<b>2. Kredit Flat Murni dengan jangka waktu 1 tahun atau kurang</b>\n"
                                          "<b>3. Kredit RC</b>\n"
                                          "<b>4. Kredit Bank Mandiri</b>", parse_mode="HTML")

@bot.message_handler(commands=['id'])
def lapor_min(message):
    try:
        bot.send_message(message.chat.id, message.json['reply_to_message']['forward_from']['id'])
    except KeyError:
        bot.send_message(message.chat.id, "Ini digunakan untuk mengetahui ID telegram.")


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
                                     f'<b>CIF</b> : {kueri[0]}\n<b>Nama</b> \t: {kueri[6]}\n<b>No SPK</b>: {kueri[3]}\n<b>Produk</b> : {kueri[5]}\n'
                                     f'<b>Alamat</b> : {kueri[7]}\n\n'
                                     f'{10*"="}\n'
                                     f'<b>Plafond</b> : {babel.numbers.format_currency(kueri[13], "IDR", locale="id_ID")}\n'
                                     f'<b>Bakidebet</b> : {babel.numbers.format_currency(kueri[14], "IDR", locale="id_ID")}\n'
                                     f'<b>RL</b> : {kueri[9]}\n'
                                     f'<b>JT</b> : {kueri[10]}\n\n'
                                     f'{10*"="}\n'
                                     f'<b>Lama Tunggakan</b> : {kueri[12]}\n'
                                     f'<b>Pokok</b> : {babel.numbers.format_currency(kueri[16], "IDR", locale="id_ID")}\n'
                                     f'<b>Bunga</b> : {babel.numbers.format_currency(kueri[15], "IDR", locale="id_ID")}\n'
                                     f'<b>Angsuran</b> : {babel.numbers.format_currency(kueri[17], "IDR", locale="id_ID")}\n\n'
                                     f'{10*"="}\n'
                                     f'<b>Tunggakan Pokok</b> : {babel.numbers.format_currency(kueri[19], "IDR", locale="id_ID")}\n'
                                     f'<b>Tunggakan Bunga</b> : {babel.numbers.format_currency(kueri[18], "IDR", locale="id_ID")}\n\n'
                                     f'{10*"="}\n'
                                     f'<b>Minimal Pokok</b>: {babel.numbers.format_currency(kueri[22], "IDR", locale="id_ID")}\n'
                                     f'<b>Minimal Bunga</b> : {babel.numbers.format_currency(kueri[23], "IDR", locale="id_ID")}\n'
                                     f'<b>Denda</b> : {babel.numbers.format_currency(kueri[24] + kueri[25], "IDR", locale="id_ID")}\n'
                                     f'<b>AO</b> : {kueri[26]}', parse_mode='HTML')
                else:  # Hasil Kosong
                    bot.reply_to(message, "Hasile ora ana, ndean urung cair, ndean sing gawe sing agi mumet. Gawekna Kopi Sit")
            except IndexError:  # Tidak ada Text, Hanya Command
                bot.send_message(message.chat.id, "Menu Ini digunakan untuk mencari pinjaman yang masih aktif. Jika tidak aktif ya ora ana sinyal\n"
                                                  "<b>Carane Kaya Kie: </b>"
                                                  "<b>/info {no pk}</b>\n\n"
                                                  "Gampang mbok? Sing angel li nek agi ora ana sinyal", parse_mode="HTML")
        else:  # Waktu di DB sudah lewat
            bot.reply_to(message, "Akun Anda Sudah Tidak Aktif. Aktifin Ulang dong. sewu!!!")


@bot.message_handler(func=lambda message: True, content_types=['photo'])
def id_gen(message):
    if message.chat.id != config.SUPER_USER:
        try:
            bot.forward_message(chat_id=config.SUPER_USER, from_chat_id=message.chat.id, message_id=message.id)
        except ConnectionAbortedError:
            print("gagal")
    else:
        json_data = json.dumps(message.json, indent=4)
        bot.send_message(chat_id=message.json['reply_to_message']['forward_from']['id'], text=message.text)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def id_gen(message):
    if message.chat.id != config.SUPER_USER:
        try:
            bot.forward_message(chat_id=config.SUPER_USER, from_chat_id=message.chat.id, message_id=message.id)
        except ConnectionAbortedError:
            print("gagal")
    else:
        json_data = json.dumps(message.json, indent=4)
        try:
            bot.send_message(chat_id=message.json['reply_to_message']['forward_from']['id'], text=message.text)
        except KeyError:
            bot.send_message(message.chat.id, "Menune urung digawe. Agi mandan bengel")

while True:
    try:
        bot.polling()
    except ConnectionAbortedError:
        continue
