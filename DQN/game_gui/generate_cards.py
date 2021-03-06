#!/bin/bash
from PIL import Image, ImageDraw, ImageFont
path_to_empty = "empty.png"



fnt1 = ImageFont.truetype('/Library/Fonts/Arial.ttf', 20)
fnt2 = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
red    = (200, 0, 0)
green  = (0, 200, 0)
blue   = (0, 0, 200)
yellow = (230, 230, 0)
color_names = ["Red", "Green", "Blue", "Yellow"]

for p, color in enumerate([red, green, blue, yellow]):
	for j in range(1, 16):
		img = Image.open(path_to_empty)
		d = ImageDraw.Draw(img)
		rest = ImageDraw.Draw(img)
		if j%2==1:
			rest.rectangle([90, 130, 90+20, 130+20], fill = color, outline=(0,0,0))
		d.text((18, 25), str(j), font=fnt1, fill=(0, 0, 0))
		d.rectangle([40, 25, 60, 45], fill=color,  outline=(0,0,0))
		rest.text((70, 70), str(j), font=fnt2, fill=(0, 0, 0))
		for i in range(int(j/2)):
			y_start = 60+i*10
			x_start_left  = 19
			x_start_right = 150
			rest.rectangle([x_start_left, y_start, x_start_left+20, y_start+20], fill = color, outline=(0,0,0))
			rest.rectangle([x_start_right, y_start, x_start_right+20, y_start+20], fill = color, outline=(0,0,0))
		img.save("cards/"+color_names[p]+str(j)+".png")

# for i in range(0, 7):
