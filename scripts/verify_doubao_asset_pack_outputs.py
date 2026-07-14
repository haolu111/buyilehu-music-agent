from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.doubao_asset_pack_verifier import verify_doubao_asset_pack_outputs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Doubao-generated primary music asset-pack PNG outputs.")
    parser.add_argument("--tasks", type=Path, help="Path to doubao-generation-tasks.json.")
    parser.add_argument("--json", action="store_true", help="Print full JSON report.")
    args = parser.parse_args()

    report = verify_doubao_asset_pack_outputs(args.tasks)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            f"{report['status']}: ready={report['ready_count']} "
            f"missing={report['missing_count']} invalid={report['invalid_count']}"
        )
        for pack in report["packs"]:
            print(f"- {pack['asset_pack_id']}: {pack['status']} ({pack['ready_count']}/{pack['total_count']})")
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
