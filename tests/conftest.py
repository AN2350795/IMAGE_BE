import os

# app.database 는 임포트 시점에 엔진을 만든다. 실제 DB 없이도 테스트가 돌도록
# 접속을 시도하지 않는 기본값을 미리 넣어 둔다(create_engine 은 연결하지 않는다).
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
