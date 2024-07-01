from PIL import Image
import os
from colorama import init
import cv2
import time
from blessed import Terminal
import sys

term = Terminal()

init()

strcharset = "@#$%&*()0!=-.,"

size = os.get_terminal_size()

imgs = []

isColored = False


def pix_to_code(i, img):
    x = i % size.columns-1
    y = i // size.columns-1

    code = img.getpixel((x, y))
    return f"\033[38;2;{code[0]};{code[1]};{code[2]}m"


def printImg(image):
    img = image.resize((size.columns, size.lines), Image.Resampling.LANCZOS)

    gimg = img.convert('L')

    img = img.quantize(colors=32)
    img = img.convert('RGB')

    pixels = list(gimg.getdata())

    string = ""
    lastcolor = None

    # splitting these up because its kinda braindead to be checking for color
    # every pixel idk what i was thinking
    if isColored:
        for i in range(len(pixels)):

            if i % size.columns-1 == 0:
                string += "\n"
            ind = int(pixels[i] / 255 * (len(strcharset) - 1))
            # now we have the pixel brightness mapped to a char, lets colour it!
            # this is why we have img and gimg
            # string += pix_to_code(i, img) + strcharset[ind] + "\033[0;39m"
            # string += strcharset[ind]
            color = f"{pix_to_code(i, img)}"
            if color != lastcolor:
                string += "\033[0;39m" + color + strcharset[ind]
                lastcolor = color
            else:
                string += strcharset[ind]
    else:
        for i in range(len(pixels)):

            if i % size.columns-1 == 0:
                string += "\n"
            ind = int(pixels[i] / 255 * (len(strcharset) - 1))

            string += strcharset[ind]

    with term.hidden_cursor():
        sys.stdout.write(term.home)
        sys.stdout.write(string)
        sys.stdout.flush()


def openVideo(file):
    vid = cv2.VideoCapture(file)

    while vid.isOpened():
        ret, img = vid.read()

        if ret:

            conv = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            pilImg = Image.fromarray(conv)

            imgs.append(pilImg)

        else:
            break

    vid.release()


print(sys.argv)
if len(sys.argv) > 1:

    if sys.argv[1].split(".")[2] in ["mp4", "avi", "mov", "gif"]:
        openVideo(sys.argv[1])
    else:
        imgs.append(Image.open(sys.argv[1]))

    if len(sys.argv) >= 2:
        for i in sys.argv[2:]:
            match i:
                case "-c":
                    isColored = True
                case "-f":
                    strcharset = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,^`'."

    for img in imgs:
        printImg(img)
        # each print takes about 0.0166 s, so if we wanna run at 30fps...
        time.sleep(0.01666667)
    print("\033[0;39m")
else:
    print("No file provided. Please provide a file as an argument.")
