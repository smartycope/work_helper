from textual.containers import *
from textual.widgets import *
from helper.menus.Menu import Menu
import io
import qrcode

qr = qrcode.QRCode()
qr.add_data("https://link.irobot.com/acc4816")
f = io.StringIO()
qr.print_ascii(out=f)
f.seek(0)
qr_text = f.read()

class LapisQrMenu(Menu):
    require_case = False

    def compose(self):
        yield Static(qr_text)
        yield Button('Close', action='close')
