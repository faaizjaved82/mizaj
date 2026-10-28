"""Check the T21 illustration contract. Run after installing the server dependencies."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TYPES = "intj intp entj entp infj infp enfj enfp istj isfj estj esfj istp isfp estp esfp".split()
MIZAJ = "damvi safravi balghami saudavi".split()


def main() -> None:
    assets = [(f"types/{code}.webp", 800) for code in TYPES]
    assets += [(f"mizaj/{key}.webp", 800) for key in MIZAJ]
    assets += [("hero.webp", 840)]
    total = 0
    for relative, size in assets:
        path = ROOT / "site/static/img" / relative
        assert path.is_file(), f"Missing illustration: {relative}"
        with Image.open(path) as image:
            assert image.format == "WEBP", f"Not WebP: {relative}"
            assert image.size == (size, size), f"Wrong dimensions: {relative}: {image.size}"
            image.verify()
        length = path.stat().st_size
        assert 0 < length < 120_000, f"Illustration must be under 120 KB: {relative}: {length}"
        total += length
    print(f"Verified {len(assets)} WebP illustrations; {total:,} bytes total; each under 120 KB")


if __name__ == "__main__":
    main()
