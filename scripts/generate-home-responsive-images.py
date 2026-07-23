from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "assets" / "images"

PRODUCT_IMAGES = [
    "product-board-yoga-seamless-activewear",
    "yoga-leggings-manufacturer-detail",
    "sports-bra-manufacturer-detail",
    "seamless-activewear-product-board",
    "plus-size-activewear-product-board",
    "athleisure-retail-drop-card",
    "hoodies-sweatshirts-manufacturer-detail",
    "joggers-tracksuits-manufacturer-detail",
]


def open_rgb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).convert("RGB")


def resize(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def save_webp(image: Image.Image, path: Path) -> None:
    image.save(path, "WEBP", quality=78, method=6)
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")


def save_avif(image: Image.Image, path: Path) -> None:
    image.save(path, "AVIF", quality=55, speed=6)
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")


for stem in PRODUCT_IMAGES:
    source = open_rgb(IMAGE_DIR / f"{stem}.jpg")
    for width in (320, 480, 640, 900):
        sized = resize(source, width)
        save_webp(sized, IMAGE_DIR / f"{stem}-{width}.webp")
        if width == 640:
            save_avif(sized, IMAGE_DIR / f"{stem}-640.avif")

hero = open_rgb(IMAGE_DIR / "hero-brand-campaign.jpg")
for width in (900, 1200):
    save_webp(resize(hero, width), IMAGE_DIR / f"hero-brand-campaign-{width}.webp")
save_webp(hero, IMAGE_DIR / "hero-brand-campaign.webp")
