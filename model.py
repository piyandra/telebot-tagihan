import datetime

def months(d1, d2):
    d1 = datetime.datetime(year=int(d1[-4:]), month=int(d1[3:5]), day=int(d1[:2]))
    d2 = datetime.datetime(year=int(d2[-4:]), month=int(d2[3:5]), day=int(d2[:2]))
    return d1.month - d2.month + 12*(d1.year - d2.year)

def days(d1, d2):
    d1 = datetime.datetime(year=int(d1[-4:]), month=int(d1[3:5]), day=int(d1[:2]))
    d2 = datetime.datetime(year=int(d2[-4:]), month=int(d2[3:5]), day=int(d2[:2]))
    return d1.day - d2.day + 30*(d1.month - d2.month)



