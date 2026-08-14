"""Generate afking.ico for the exe icon. Run automatically by build.bat."""

from icon import make_image

SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

if __name__ == "__main__":
    make_image(active=True, size=256).save("afking.ico", format="ICO", sizes=SIZES)
    print("Wrote afking.ico")
