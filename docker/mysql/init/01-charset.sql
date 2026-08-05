-- 최초 컨테이너 생성 시 1회만 실행된다(볼륨이 비어 있을 때).
-- 이후 변경은 마이그레이션 도구로 관리하고, 이 파일을 다시 적용하려면
-- docker compose down -v 로 볼륨을 지운 뒤 재생성해야 한다.
ALTER DATABASE image_be CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
