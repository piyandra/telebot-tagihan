import time

import mysql.connector

import config

db = mysql.connector.connect(host=config.DB_HOST,
                             port="3306",
                             username=config.DB_USER,
                             password=config.DB_PASSWORD,
                             database=config.DB)

cursor = db.cursor()
chat = '6860012691'
def role(chat_id): # Query Role ID
    cursor.execute("SELECT * FROM member WHERE id= {} LIMIT 1".format(chat_id))
    hasil = cursor.fetchone()
    return hasil

def cek_admin(idadmin):
    cursor.execute("SELECT * from member WHERE id= {} AND role = 'admin' LIMIT 1".format(idadmin))
    hashil = cursor.fetchone()
    if hashil == None:
        return False
    else:
        for row in hashil:
            return row

def addmember(idmember):
    insert = "INSERT INTO member(id, role, exp) VALUES (%s, 'member', %s)"
    value = (idmember, time.time() + 60*60*24*30)
    cursor.execute(insert, value)
    db.commit()
    return cursor.rowcount

def cek_aktif(id_tele):
    cursor.execute("SELECT exp FROM member WHERE id={} LIMIT 1".format(id_tele))
    hasil = cursor.fetchone()
    return hasil

def delete_db(id):
    cursor.execute("DELETE FROM member WHERE id={}".format(id))
    db.commit()

def nama(nama, kantor):
    cursor.execute("SELECT nama, alamat, spk, bd FROM dakol where nama LIKE '%{}%' AND kantor = {} LIMIT 5".format(nama, kantor))
    hasil = cursor.fetchall()
    return hasil


def cek_pk(nopk):
    cursor.execute("SELECT * FROM dakol WHERE spk = '{}' LIMIT 1".format(nopk))
    hasil = cursor.fetchone()
    return hasil