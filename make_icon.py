from PIL import Image, ImageDraw

S = 1024
im = Image.new("RGBA", (S, S), "#FFFFFF")
d = ImageDraw.Draw(im)
d.ellipse((40, 40, S - 40, S - 40), fill="#1B1464")
box = (120, 120, S - 120, S - 120)
d.ellipse(box, fill="white")
for a, b, c in [(-90, 0, "#FF6B6B"), (0, 35, "#FFD166"), (35, 150, "#3CD6C4"), (150, 180, "#A5B4F0")]:
    d.pieslice(box, a, b, fill=c)
d.pieslice(box, 180, 270, fill="white")
C = S // 2
for a in range(12):  # tick dots
    import math
    x, y = C + 340 * math.cos(a * math.pi / 6), C + 340 * math.sin(a * math.pi / 6)
    d.ellipse((x - 9, y - 9, x + 9, y + 9), fill="#1B1464")
d.line((C, C, C - 190, C - 120), fill="#1B1464", width=26)
d.line((C, C, C + 250, C - 190), fill="#1B1464", width=26)
d.line((C, C, C - 260, C + 150), fill="#FF3B3B", width=9)
d.ellipse((C - 26, C - 26, C + 26, C + 26), fill="#FF3B3B")
# calendar badge (top-right)
d.rounded_rectangle((650, 90, 930, 300), 28, fill="#EEF3FF", outline="#1B1464", width=14)
d.rectangle((664, 104, 916, 150), fill="#FFD166")
for i in range(3):
    for j in range(3):
        d.rectangle((690 + i * 80, 175 + j * 38, 720 + i * 80, 195 + j * 38), fill="#FF6B6B" if (i + j) % 2 else "#A5B4F0")
# check badge (bottom-right)
d.ellipse((760, 700, 930, 870), fill="#3CD6C4")
d.line((800, 785, 840, 825, 895, 750), fill="white", width=22, joint="curve")
im.convert("RGB").resize((512, 512), Image.LANCZOS).save("icon.png")
