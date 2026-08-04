import os
import venv
import subprocess

# 설정 변수
VENV_DIR = ".venv"
REQ_FILE = "requirements.txt"

def get_venv_python():
    """현재 OS에 맞는 가상환경 내부의 Python 실행 파일 경로를 반환합니다."""
    if os.name == 'nt':  # 윈도우 환경
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:                # 리눅스 / 맥 환경
        return os.path.join(VENV_DIR, "bin", "python")

def setup_virtualenv():
    """가상환경 폴더가 없으면 자동으로 생성합니다."""
    if not os.path.exists(VENV_DIR):
        print(f"🌱 [{VENV_DIR}] 가상환경이 없습니다. 새로 생성합니다 (시간이 조금 걸릴 수 있습니다)...")
        # 현재 실행 중인 파이썬 엔진을 기반으로 새 가상환경(pip 포함) 생성
        venv.create(VENV_DIR, with_pip=True)
        print("✅ 가상환경 생성 완료!\n")
    else:
        print(f"✅ [{VENV_DIR}] 가상환경이 이미 준비되어 있습니다.\n")

def install_requirements(python_exe):
    """'가상환경 내부의 Python'을 사용하여 패키지를 안전하게 설치합니다."""
    if os.path.exists(REQ_FILE):
        print(f"📦 [{REQ_FILE}] 패키지를 격리된 가상환경에 설치 및 업데이트합니다...")
        subprocess.check_call([python_exe, "-m", "pip", "install", "-r", REQ_FILE])
        print("✅ 패키지 세팅 완료!\n")
    else:
        print(f"⚠️ [{REQ_FILE}] 파일을 찾을 수 없습니다. 패키지 설치를 건너뜁니다.\n")

def run_application(python_exe):
    """'가상환경 내부의 Python'으로 백엔드 서버를 실행합니다."""
    print("🚀 백엔드 서버를 구동합니다...")
    
    # (fastapi dev main.py)
    command = [python_exe, "-m", "fastapi", "dev", "main.py"]

    try:
        # 프로세스가 종료될 때까지 대기
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 서버 실행이 중단되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    print("=== 🚀 자동 세팅 및 실행 스크립트 시작 ===\n")
    
    # 1. 가상환경 세팅
    setup_virtualenv()
    
    # 2. OS에 맞는 가상환경 파이썬 경로 획득
    venv_python = get_venv_python()
    
    # 3. 패키지 설치
    install_requirements(venv_python)
    
    # 4. 앱 실행
    run_application(venv_python)