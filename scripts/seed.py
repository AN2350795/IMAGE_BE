"""data/seed 의 JSON 을 데이터베이스에 적재하는 스크립트.

아직 ORM 모델이 없어서 지금은 시드 파일을 읽어 건수를 확인하는 단계까지만 수행한다.
모델이 추가되면 load_seed() 로 읽은 데이터를 세션에 넣는 코드를 여기에 이어서 작성한다.
"""

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEED_DIR = PROJECT_ROOT / "data" / "seed"


def load_seed() -> dict[str, Any]:
    """data/seed 의 JSON 을 확장자 없는 파일 이름을 키로 하여 모두 읽는다."""
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(SEED_DIR.glob("*.json"))
    }


def main() -> int:
    if not SEED_DIR.is_dir():
        print(f"시드 디렉터리를 찾을 수 없습니다: {SEED_DIR}")
        return 1

    seed = load_seed()
    if not seed:
        print(f"{SEED_DIR} 에 JSON 파일이 없습니다.")
        return 1

    for name, records in seed.items():
        print(f"  {name:30} {len(records):>6} 건")

    print("\nORM 모델이 아직 없어 데이터베이스 적재는 수행하지 않았습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
