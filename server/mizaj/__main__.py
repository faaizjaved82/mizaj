"""Command line: python -m mizaj <command>. Used by systemd timers and by the owner."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import db, notify, payments, stats
from .config import settings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mizaj")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("digest", help="send yesterday's numbers to the owner on Telegram")
    ex = sub.add_parser("export-stats", help="write the aggregate weekly stats JSON")
    ex.add_argument("path")
    cd = sub.add_parser("codes", help="create voucher codes (B2B seats, gifts, discounts)")
    cd.add_argument("product", help="full | career | couple | palm | bundle | * (discounts only)")
    cd.add_argument("--count", type=int, default=1)
    cd.add_argument("--kind", choices=["unlock", "discount"], default="unlock")
    cd.add_argument("--discount", type=int, default=0)
    cd.add_argument("--uses", type=int, default=1)
    cd.add_argument("--org", default="")
    cd.add_argument("--prefix", default="MZ")
    ap_ = sub.add_parser("approve", help="mark an order paid")
    ap_.add_argument("order_id")
    sub.add_parser("pending", help="list payments waiting for approval")
    args = ap.parse_args(argv)

    db.connect()
    if args.cmd == "digest":
        text = stats.digest_text()
        print(text)
        notify.telegram(text, [[("Open admin", f"{settings.site_url}/admin")]])
    elif args.cmd == "export-stats":
        p = Path(args.path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(stats.weekly_export(), indent=2))
        print(f"wrote {p}")
    elif args.cmd == "codes":
        for c in payments.create_codes(args.product, args.count, args.kind, args.discount, args.uses, args.org,
                                       prefix=args.prefix.upper()):
            print(c)
    elif args.cmd == "approve":
        o = payments.mark_paid(args.order_id)
        print("approved" if o else "not found")
    elif args.cmd == "pending":
        for r in db.q("SELECT id, product, amount, method, tid, sender FROM orders WHERE status = 'proof'"):
            print(dict(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
