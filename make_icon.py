from PIL import Image

img = Image.open("assets/MoongNyangSnackBox_Icon.png").convert("RGBA")
s = max(img.size)                                  # 정사각형 캔버스
canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
canvas.paste(img, ((s - img.width) // 2, (s - img.height) // 2))
canvas.save("assets/MoongNyangSnackBox_Icon.ico",
            sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
print("done: assets/MoongNyangSnackBox_Icon.ico")