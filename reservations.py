import requests
import pytz
from datetime import datetime
from RPLCD.i2c import CharLCD

API_TOKEN = 'a92da464cdabe05920af8614bbc058fa9424737a'
SMILEY = (
    0b00000,
    0b01010,
    0b01010,
    0b00000,
    0b10001,
    0b10001,
    0b01110,
    0b00000,
)
MAN = (
    0b00100,
    0b01110,
    0b01110,
    0b00100,
    0b11111,
    0b00100,
    0b01010,
    0b10001,
)
TZ = pytz.timezone('Europe/Zurich')

def get_reservations():
    url = 'https://reservations.coredump.ch/api/v1/reservations'
    r = requests.get(url, headers={'Authorization': 'Token ' + API_TOKEN})
    return r.json()

lcd = CharLCD(0x27)
lcd.clear()

lcd.create_char(0, SMILEY)
lcd.create_char(1, MAN)

lcd.cursor_pos = (1, 5)
lcd.write_string('Loading...')
data = get_reservations()
lcd.clear()

if data['count'] == 0:
    lcd.write_string('Keine Reservation ' + chr(0))
    lcd.cursor_pos = (2, 0)
    lcd.write_string(chr(126) + ' reservations.')
    lcd.cursor_pos = (3, 9)
    lcd.write_string('coredump.ch')
else:
    res = data['results'][0]
    start = datetime.strptime(res['start'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc).astimezone(TZ)
    end = datetime.strptime(res['end'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc).astimezone(TZ)
    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(TZ)
    if start <= now:
        lcd.write_string('Aktive Reservation:')
    else:
        lcd.write_string('N' + chr(0b11100001) + 'chste Reservation:')
    lcd.cursor_pos = (1, 0)
    name_line = '%s %s' % (chr(1), res['owner'])
    lcd.write_string(name_line[:20])
    lcd.cursor_pos = (2, 0)
    lcd.write_string('Von %s' % start.strftime('%d.%m.%y %H:%M'))
    lcd.cursor_pos = (3, 0)
    lcd.write_string('Bis %s' % end.strftime('%d.%m.%y %H:%M'))
