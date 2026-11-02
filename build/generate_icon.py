"""Create the Windows .ico release resource from the project's vector mark."""

from pathlib import Path
from PIL import Image, ImageDraw


def main() -> None:
    size = 256
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = image.load()
    for y in range(size):
        t = y / (size - 1)
        color = (int(24 - 11 * t), int(40 - 17 * t), int(61 - 22 * t), 255)
        for x in range(size):
            pixels[x, y] = color
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((8, 8, 247, 247), radius=58, fill=255)
    image.putalpha(mask)
    draw = ImageDraw.Draw(image)
    # Two quadratic curves form a quiet crossing/orbit motif.
    for points, color in (
        (((49, 145), (91, 39), (129, 64), (207, 112)), (111, 218, 204, 255)),
        (((49, 111), (92, 219), (131, 192), (207, 144)), (85, 184, 208, 255)),
    ):
        p0, p1, p2, p3 = points
        path = []
        for i in range(101):
            t = i / 100
            u = 1 - t
            x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
            y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
            path.append((round(x), round(y)))
        draw.line(path, fill=color, width=10, joint="curve")
    for x, y, color in ((49, 128, (244, 247, 251, 255)), (207, 112, (116, 224, 207, 255)), (207, 144, (85, 184, 208, 255))):
        draw.ellipse((x-15, y-15, x+15, y+15), fill=color)
    output = Path(__file__).resolve().parent / "probability_of_us.ico"
    image.save(output, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
