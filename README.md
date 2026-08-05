# IMAGE_BE

FastAPI + MySQL 백엔드. 어느 머신에서든 동일한 개발 환경으로 실행할 수 있도록
devcontainer 와 Docker Compose 를 기준으로 구성되어 있다.

## 프로젝트 구조

```
app/                     애플리케이션 패키지
  main.py                FastAPI 앱 생성과 라우터 등록
  config.py              환경 변수 설정 (pydantic-settings)
  database.py            엔진 / 세션 / ORM 기반 클래스
  routers/
    health.py            /health/db
data/
  seed/                  데이터베이스에 적재할 원본 JSON
docker/
  Dockerfile.dev         개발용 앱 이미지 (uv 포함)
  mysql/init/            MySQL 최초 기동 시 1회 실행되는 SQL
scripts/
  dev.py                 도커 없이 호스트에서 서버 실행
  seed.py                data/seed 적재 스크립트
tests/                   pytest 테스트
requests/api.http        API 요청 샘플
.devcontainer/           devcontainer 정의 (docker-compose.yml 을 재사용)
docker-compose.yml       mysql + app 서비스 정의
pyproject.toml           의존성과 도구 설정
uv.lock                  고정된 의존성 버전
```

애플리케이션 코드는 모두 `app/` 안에 있고, 루트에는 설정 파일만 둔다.
새 엔드포인트는 `app/routers/` 에 모듈을 추가하고 `app/main.py` 에서 등록한다.

## 실행 방법 1 — Devcontainer (권장)

필요한 것은 **Docker 와 VS Code / Cursor** 뿐이다. 호스트에 Python 을 설치하지 않아도 된다.

1. 저장소를 clone 한다.
2. 에디터에서 폴더를 연 뒤 **Reopen in Container** 를 실행한다.
3. 컨테이너 안 터미널에서 서버를 띄운다.

```bash
uv run fastapi dev app/main.py --host 0.0.0.0
```

MySQL 은 devcontainer 가 뜰 때 함께 기동되고, 준비될 때까지 기다린 뒤 앱 컨테이너가 시작된다.
서버는 호스트의 http://127.0.0.1:8000 으로 접속한다.

## 실행 방법 2 — Docker Compose 만 사용

에디터는 호스트에서 쓰고 실행만 컨테이너로 하고 싶을 때.

```bash
docker compose up --build
```

앱과 DB 가 함께 뜬다. 코드 변경은 바인드 마운트를 통해 즉시 반영된다(`fastapi dev` 의 자동 리로드).

## 실행 방법 3 — 호스트에서 직접

가장 가볍지만 호스트에 [uv](https://docs.astral.sh/uv/) 가 필요하다.

```bash
docker compose up -d mysql   # DB 만 컨테이너로
python scripts/dev.py        # uv sync 후 fastapi dev 실행
```

## 환경 변수

`.env.example` 을 `.env` 로 복사해서 사용한다. `.env` 는 커밋되지 않는다.

```bash
cp .env.example .env
```

`.env` 가 없어도 compose 는 개발용 기본값으로 동작한다. 값을 바꾸려면 `.env` 를 만들어야 한다.

| 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `MYSQL_PORT` | `3306` | 호스트로 노출할 MySQL 포트 |
| `MYSQL_DATABASE` | `image_be` | 데이터베이스 이름 |
| `MYSQL_USER` / `MYSQL_PASSWORD` | `image_be` / `devpass` | 애플리케이션 계정 |
| `MYSQL_ROOT_PASSWORD` | `devroot` | root 비밀번호 |
| `APP_PORT` | `8000` | 호스트로 노출할 앱 포트 |
| `SQL_ECHO` | `false` | 실행되는 SQL 을 콘솔에 출력 |

`DATABASE_URL` 은 호스트에서 실행할 때만 `.env` 값을 쓴다. 컨테이너 안에서는 DB 주소가
`127.0.0.1` 이 아니라 서비스 이름 `mysql` 이어야 하므로 compose 가 환경 변수로 주입한다.
pydantic-settings 는 실제 환경 변수를 `.env` 파일보다 우선하므로 양쪽이 충돌 없이 동작한다.

## 의존성 관리

[uv](https://docs.astral.sh/uv/) 를 쓰며, 버전은 `uv.lock` 에 고정되어 있다.
`uv.lock` 은 반드시 커밋해야 모든 머신에서 같은 버전이 설치된다.

```bash
uv add <package>              # 런타임 의존성 추가
uv add --dev <package>        # 개발 도구 추가
uv sync --frozen              # 락파일 그대로 설치
uv lock --upgrade             # 의존성 버전 올리기
```

devcontainer 안에서 가상환경은 워크스페이스가 아니라 `/opt/venv` 에 만들어진다.
바인드 마운트된 폴더에 두면 호스트의 `.venv` 와 충돌하고 윈도우에서 I/O 가 크게 느려지기 때문이다.

## 테스트와 린트

```bash
uv run pytest                 # 테스트
uv run ruff check .           # 린트
uv run ruff format .          # 포맷
```

`/health/db` 테스트는 세션 의존성을 대역으로 바꿔치기하므로 MySQL 이 떠 있지 않아도 통과한다.

## 시드 데이터

`data/seed/` 의 JSON 은 최종적으로 MySQL 에 적재할 원본 자료다.

| 파일 | 내용 |
| --- | --- |
| `character_data.json` | 캐릭터별 직업과 이미지 경로 |
| `background_file_list.json` | 배경 이미지 파일 목록 |
| `filter-char.json` | 팀 / 캐릭터 필터 옵션 |
| `filter-theme.json` | 테마 필터 옵션 |
| `output.json` | 이미지 메타데이터 전체 목록 |

```bash
uv run python scripts/seed.py
```

현재는 ORM 모델이 없어 파일을 읽어 건수를 확인하는 것까지만 동작한다.
모델이 추가되면 `scripts/seed.py` 에 적재 로직을 이어서 작성한다.

## 동작 확인

```
GET http://127.0.0.1:8000            # {"Hello": "Secret Backend Project"}
GET http://127.0.0.1:8000/health/db  # {"database": "ok"}
```

`requests/api.http` 파일로도 바로 호출해 볼 수 있다.

## 알려진 제약

데이터베이스 스키마는 `docker/mysql/init/01-charset.sql` 로만 관리된다. 이 스크립트는
볼륨이 비어 있는 최초 1회에만 실행되므로 머신 간 스키마 동기화 수단이 되지 못한다.
모델이 생기기 시작하면 Alembic 같은 마이그레이션 도구로 옮기는 것이 좋다.
