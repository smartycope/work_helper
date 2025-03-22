import streamlit as st
import qrcode
import qrcode.image.svg

img = qrcode.make("https://link.irobot.com/acc4816", image_factory=qrcode.image.svg.SvgFillImage)
st.image(str(img.to_string(), 'utf-8'), width=600)
