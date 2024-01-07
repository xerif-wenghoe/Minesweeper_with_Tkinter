from PIL import Image

im = Image.open("C:/Users/Xerif/Downloads/smile_icon.png")

new_im = im.resize((32,32))

new_im.save("res/images/smile_icon_w_bg.png")
