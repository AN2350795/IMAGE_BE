"""도커 없이 호스트에서 바로 개발 서버를 띄우는 보조 스크립트.

권장 실행 방법은 devcontainer 이며, 자세한 내용은 README 를 참고한다.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INSTALL_GUIDE = """\
❌ uv 를 찾을 수 없습니다. 아래 중 하나로 설치한 뒤 다시 실행해 주세요.

  Windows : powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  macOS/Linux : curl -LsSf https://astral.sh/uv/install.sh | sh
  공통 : pip install uv
"""


def main() -> int:
    uv = shutil.which("uv")
    if uv is None:
        print(INSTALL_GUIDE)
        return 1

    # 어느 경로에서 실행해도 저장소 루트를 기준으로 동작하게 맞춘다.
    os.chdir(PROJECT_ROOT)

    print("📦 uv.lock 에 고정된 버전으로 가상환경을 맞춥니다...")
    subprocess.check_call([uv, "sync", "--frozen"])

    print("🚀 백엔드 서버를 구동합니다...")
    try:
        subprocess.run([uv, "run", "--frozen", "fastapi", "dev", "app/main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 서버 실행이 중단되었습니다.")
    except subprocess.CalledProcessError as exc:
        print(f"\n❌ 실행 중 오류가 발생했습니다: {exc}")
        return exc.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
