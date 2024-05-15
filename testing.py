import mysql.connector
import config
from datetime import datetime
from dateutil import relativedelta

db = mysql.connector.connect(host=config.DB_HOST,
                             port="3306",
                             username=config.DB_USER,
                             password=config.DB_PASSWORD,
                             database=config.DB)

cursor = db.cursor()
no_spk = 117204000512

cursor.execute('select *, CURRENT_DATE(), DATEDIFF(CURRENT_DATE(), rl)/30 AS data from pelunasan WHERE spk = "{}"'.format(no_spk))
hasil = cursor.fetchone()
print(int(hasil[15]))
