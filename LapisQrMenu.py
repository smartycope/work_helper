from textual.containers import *
from textual.widgets import *
from Menu import Menu
import io
import qrcode


class LapisQrMenu(Menu):
    require_case = False

    def compose(self):
        self.qr = qrcode.QRCode()
        self.qr.add_data("https://link.irobot.com/acc4816")
        f = io.StringIO()
        self.qr.print_ascii(out=f)
        f.seek(0)
        yield Static(f.read())
        yield Button('Close', action='close')
