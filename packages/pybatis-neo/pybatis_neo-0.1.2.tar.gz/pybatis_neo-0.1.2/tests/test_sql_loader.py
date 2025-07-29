"""
SQL 파일 로딩 기능 테스트

.sql 파일에서 SQL 문을 로드하는 기능을 테스트합니다.
"""

import tempfile
from pathlib import Path

import pytest

from pybatis.sql_loader import SqlLoader


class TestSqlLoader:
    """SQL 로더 클래스의 테스트"""

    @pytest.fixture
    def temp_sql_dir(self):
        """임시 SQL 디렉토리 픽스처"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_dir = Path(temp_dir)

            # 샘플 SQL 파일들 생성
            (sql_dir / "users.sql").write_text(
                """
-- 사용자 조회 SQL
SELECT id, name, email, is_active
FROM users
WHERE id = :user_id
""".strip()
            )

            (sql_dir / "user_operations.sql").write_text(
                """
-- name=get_user_by_email
SELECT id, name, email, is_active
FROM users
WHERE email = :email

-- name=count_active_users
SELECT COUNT(*)
FROM users
WHERE is_active = :active

-- name=insert_user
INSERT INTO users (name, email, is_active)
VALUES (:name, :email, :is_active)
""".strip()
            )

            yield sql_dir

    def test_create_sql_loader(self, temp_sql_dir):
        """SQL 로더 인스턴스 생성 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)
        assert loader.sql_dir == temp_sql_dir

    def test_load_sql_from_file(self, temp_sql_dir):
        """단일 SQL 파일 로드 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        sql = loader.load_sql("users.sql")

        assert "SELECT id, name, email, is_active" in sql
        assert "FROM users" in sql
        assert "WHERE id = :user_id" in sql

    def test_load_sql_with_name(self, temp_sql_dir):
        """이름으로 SQL 로드 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        sql = loader.load_sql("user_operations.sql", name="get_user_by_email")

        assert "SELECT id, name, email, is_active" in sql
        assert "WHERE email = :email" in sql
        assert "COUNT(*)" not in sql  # 다른 SQL은 포함되지 않음

    def test_load_sql_count_query(self, temp_sql_dir):
        """카운트 쿼리 로드 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        sql = loader.load_sql("user_operations.sql", name="count_active_users")

        assert "SELECT COUNT(*)" in sql
        assert "WHERE is_active = :active" in sql

    def test_load_sql_insert_query(self, temp_sql_dir):
        """인서트 쿼리 로드 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        sql = loader.load_sql("user_operations.sql", name="insert_user")

        assert "INSERT INTO users" in sql
        assert "VALUES (:name, :email, :is_active)" in sql

    def test_load_sql_file_not_found(self, temp_sql_dir):
        """존재하지 않는 파일 로드 시 예외 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        with pytest.raises(FileNotFoundError):
            loader.load_sql("nonexistent.sql")

    def test_load_sql_name_not_found(self, temp_sql_dir):
        """존재하지 않는 이름 로드 시 예외 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        with pytest.raises(ValueError, match="SQL with name 'nonexistent' not found"):
            loader.load_sql("user_operations.sql", name="nonexistent")

    def test_load_sql_without_name_from_multi_sql_file(self, temp_sql_dir):
        """이름 없이 다중 SQL 파일 로드 시 전체 내용 반환 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        sql = loader.load_sql("user_operations.sql")

        # 전체 파일 내용이 반환되어야 함
        assert "get_user_by_email" in sql
        assert "count_active_users" in sql
        assert "insert_user" in sql


class TestSqlLoaderIntegration:
    """SQL 로더와 PyBatis 통합 테스트"""

    @pytest.fixture
    def temp_sql_dir(self):
        """임시 SQL 디렉토리 픽스처"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_dir = Path(temp_dir)

            (sql_dir / "users.sql").write_text(
                """
SELECT id, name, email, is_active
FROM users
WHERE id = :user_id
""".strip()
            )

            yield sql_dir

    def test_pybatis_with_sql_loader(self, temp_sql_dir):
        """PyBatis와 SQL 로더 통합 테스트"""
        from pybatis import PyBatis
        from tests.test_pybatis import MockConnection

        # PyBatis에 SQL 로더 설정
        db = PyBatis()
        db.set_sql_loader(SqlLoader(sql_dir=temp_sql_dir))
        db._connection = MockConnection()  # 테스트용 연결 주입

        # SQL 파일에서 로드한 SQL 실행 테스트는 실제 구현 후 추가
        assert db.sql_loader is not None
        assert db.sql_loader.sql_dir == temp_sql_dir

    def test_pybatis_init_with_sql_dir(self, temp_sql_dir):
        """PyBatis 초기화 시 SQL 디렉토리 설정 테스트"""
        from pybatis import PyBatis

        db = PyBatis(sql_dir=temp_sql_dir)

        assert db.sql_loader is not None
        assert db.sql_loader.sql_dir == temp_sql_dir

    def test_load_sql_from_pybatis(self, temp_sql_dir):
        """PyBatis에서 SQL 로드 테스트"""
        from pybatis import PyBatis

        db = PyBatis(sql_dir=temp_sql_dir)

        sql = db.load_sql("users.sql")

        assert "SELECT id, name, email, is_active" in sql
        assert "FROM users" in sql
        assert "WHERE id = :user_id" in sql

    def test_load_sql_without_loader_raises_error(self):
        """SQL 로더 없이 SQL 로드 시 오류 테스트"""
        from pybatis import PyBatis

        db = PyBatis()

        with pytest.raises(ValueError, match="SQL 로더가 설정되지 않았습니다"):
            db.load_sql("users.sql")


class TestSqlLoaderUtilityMethods:
    """SQL 로더 유틸리티 메서드 테스트"""

    @pytest.fixture
    def temp_sql_dir(self):
        """임시 SQL 디렉토리 픽스처"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_dir = Path(temp_dir)

            (sql_dir / "users.sql").write_text("SELECT * FROM users")
            (sql_dir / "posts.sql").write_text("SELECT * FROM posts")
            (sql_dir / "comments.sql").write_text(
                """
-- name=get_comment
SELECT * FROM comments WHERE id = :id

-- name=list_comments
SELECT * FROM comments WHERE post_id = :post_id
""".strip()
            )

            yield sql_dir

    def test_list_sql_files(self, temp_sql_dir):
        """SQL 파일 목록 조회 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        files = loader.list_sql_files()

        assert "users.sql" in files
        assert "posts.sql" in files
        assert "comments.sql" in files
        assert len(files) == 3

    def test_list_named_sqls(self, temp_sql_dir):
        """이름이 지정된 SQL 목록 조회 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        names = loader.list_named_sqls("comments.sql")

        assert "get_comment" in names
        assert "list_comments" in names
        assert len(names) == 2

    def test_list_named_sqls_empty_file(self, temp_sql_dir):
        """이름이 없는 SQL 파일에서 빈 목록 반환 테스트"""
        loader = SqlLoader(sql_dir=temp_sql_dir)

        names = loader.list_named_sqls("users.sql")

        assert names == []
