"""python -m mizaj_social post-due | upcoming"""
import logging
import sys

from . import poster

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "upcoming"
    if cmd == "post-due":
        for line in poster.post_due():
            print(line)
    elif cmd == "upcoming":
        if not poster.start_date():
            print("SOCIAL_START_DATE is not set, nothing is scheduled.")
        for line in poster.upcoming(int(sys.argv[2]) if len(sys.argv) > 2 else 7):
            print(line)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
