"""
SQLite 통합 테스트

aiosqlite를 사용한 실제 데이터베이스 연결 및 쿼리 실행을 테스트합니다.
"""

import tempfile
from pathlib import Path

import pytest

from pybatis import PyBatis
from tests.fixtures import User


class TestSQLiteIntegration:
    """SQLite 데이터베이스 통합 테스트"""

    @pytest.fixture
    async def temp_db(self):
        """임시 SQLite 데이터베이스 픽스처"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            db_path = temp_file.name

        # DSN 생성
        dsn = f"sqlite:///{db_path}"

        try:
            # 테이블 생성을 위한 초기 연결
            db = PyBatis(dsn=dsn)
            await db.connect()

            # 테스트용 테이블 생성
            await db.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            # 테스트 데이터 삽입
            await db.execute(
                "INSERT INTO users (name, email, is_active) VALUES (:name, :email, :is_active)",
                params={"name": "테스트사용자", "email": "test@example.com", "is_active": True},
            )
            await db.execute(
                "INSERT INTO users (name, email, is_active) VALUES (:name, :email, :is_active)",
                params={"name": "비활성사용자", "email": "inactive@example.com", "is_active": False},
            )

            yield db

        finally:
            await db.close()
            # 임시 파일 정리
            Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_sqlite_connection(self):
        """SQLite 연결 테스트"""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_file:
            dsn = f"sqlite:///{temp_file.name}"

            db = PyBatis(dsn=dsn)
            await db.connect()

            assert db._connection is not None

            await db.close()

    @pytest.mark.asyncio
    async def test_fetch_val_with_sqlite(self, temp_db):
        """SQLite에서 fetch_val 테스트"""
        count = await temp_db.fetch_val("SELECT COUNT(*) FROM users")

        assert count == 2

    @pytest.mark.asyncio
    async def test_fetch_val_with_params(self, temp_db):
        """SQLite에서 파라미터를 사용한 fetch_val 테스트"""
        count = await temp_db.fetch_val(
            "SELECT COUNT(*) FROM users WHERE is_active = :active", params={"active": True}
        )

        assert count == 1

    @pytest.mark.asyncio
    async def test_fetch_one_with_sqlite(self, temp_db):
        """SQLite에서 fetch_one 테스트"""
        row = await temp_db.fetch_one(
            "SELECT id, name, email, is_active FROM users WHERE name = :name",
            params={"name": "테스트사용자"},
        )

        assert row is not None
        assert row["name"] == "테스트사용자"
        assert row["email"] == "test@example.com"
        assert row["is_active"] == 1  # SQLite에서 boolean은 integer로 저장됨

    @pytest.mark.asyncio
    async def test_fetch_all_with_sqlite(self, temp_db):
        """SQLite에서 fetch_all 테스트"""
        rows = await temp_db.fetch_all("SELECT id, name, email, is_active FROM users")

        assert len(rows) == 2
        assert rows[0]["name"] == "테스트사용자"
        assert rows[1]["name"] == "비활성사용자"

    @pytest.mark.asyncio
    async def test_execute_insert(self, temp_db):
        """SQLite에서 INSERT 실행 테스트"""
        result = await temp_db.execute(
            "INSERT INTO users (name, email, is_active) VALUES (:name, :email, :is_active)",
            params={"name": "새사용자", "email": "new@example.com", "is_active": True},
        )

        # SQLite에서는 영향받은 행 수 또는 마지막 insert row id 반환
        assert result is not None

        # 삽입된 데이터 확인
        count = await temp_db.fetch_val("SELECT COUNT(*) FROM users")
        assert count == 3

    @pytest.mark.asyncio
    async def test_execute_update(self, temp_db):
        """SQLite에서 UPDATE 실행 테스트"""
        result = await temp_db.execute(
            "UPDATE users SET is_active = :is_active WHERE name = :name",
            params={"is_active": False, "name": "테스트사용자"},
        )

        assert result is not None

        # 업데이트된 데이터 확인
        row = await temp_db.fetch_one(
            "SELECT is_active FROM users WHERE name = :name", params={"name": "테스트사용자"}
        )
        assert row["is_active"] == 0  # False는 0으로 저장됨

    @pytest.mark.asyncio
    async def test_execute_delete(self, temp_db):
        """SQLite에서 DELETE 실행 테스트"""
        result = await temp_db.execute(
            "DELETE FROM users WHERE name = :name", params={"name": "비활성사용자"}
        )

        assert result is not None

        # 삭제 확인
        count = await temp_db.fetch_val("SELECT COUNT(*) FROM users")
        assert count == 1

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """SQLite 컨텍스트 매니저 테스트"""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_file:
            dsn = f"sqlite:///{temp_file.name}"

            async with PyBatis(dsn=dsn) as db:
                # 테이블 생성
                await db.execute("""
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT
                    )
                """)

                # 데이터 삽입
                await db.execute(
                    "INSERT INTO test_table (name) VALUES (:name)", params={"name": "테스트"}
                )

                # 데이터 조회
                count = await db.fetch_val("SELECT COUNT(*) FROM test_table")
                assert count == 1

            # 컨텍스트 매니저 종료 후 연결이 닫혔는지 확인
            # (실제 테스트에서는 연결이 이미 닫혔으므로 에러가 발생해야 함)


class TestSQLitePydanticIntegration:
    """SQLite와 Pydantic 모델 통합 테스트"""

    @pytest.fixture
    async def temp_db_with_users(self):
        """사용자 데이터가 있는 임시 SQLite 데이터베이스 픽스처"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            db_path = temp_file.name

        dsn = f"sqlite:///{db_path}"

        try:
            db = PyBatis(dsn=dsn)
            await db.connect()

            # 테스트용 테이블 생성
            await db.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            # 테스트 데이터 삽입
            await db.execute(
                "INSERT INTO users (name, email, is_active) VALUES (:name, :email, :is_active)",
                params={"name": "김철수", "email": "kim@example.com", "is_active": True},
            )
            await db.execute(
                "INSERT INTO users (name, email, is_active) VALUES (:name, :email, :is_active)",
                params={"name": "이영희", "email": "lee@example.com", "is_active": True},
            )
            await db.execute(
                "INSERT INTO users (name, email, is_active) VALUES (:name, :email, :is_active)",
                params={"name": "박민수", "email": "park@example.com", "is_active": False},
            )

            yield db

        finally:
            await db.close()
            Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_fetch_one_to_pydantic_model(self, temp_db_with_users):
        """SQLite에서 조회한 데이터를 Pydantic 모델로 변환 테스트"""
        row = await temp_db_with_users.fetch_one(
            "SELECT id, name, email, is_active FROM users WHERE name = :name",
            params={"name": "김철수"},
        )

        assert row is not None

        # 딕셔너리를 Pydantic 모델로 변환
        # SQLite에서 boolean은 integer로 저장되므로 변환 필요
        user_data = dict(row)
        user_data["is_active"] = bool(user_data["is_active"])  # 1 -> True, 0 -> False
        user = User(**user_data)

        assert isinstance(user, User)
        assert user.name == "김철수"
        assert user.email == "kim@example.com"
        assert user.is_active is True
        assert user.id == 1

    @pytest.mark.asyncio
    async def test_fetch_all_to_pydantic_models(self, temp_db_with_users):
        """SQLite에서 조회한 모든 데이터를 Pydantic 모델 리스트로 변환 테스트"""
        rows = await temp_db_with_users.fetch_all(
            "SELECT id, name, email, is_active FROM users WHERE is_active = :active",
            params={"active": True},
        )

        assert len(rows) == 2

        # 딕셔너리 리스트를 Pydantic 모델 리스트로 변환
        users = []
        for row in rows:
            user_data = dict(row)
            user_data["is_active"] = bool(user_data["is_active"])
            users.append(User(**user_data))

        assert len(users) == 2
        assert all(isinstance(user, User) for user in users)
        assert users[0].name == "김철수"
        assert users[1].name == "이영희"
        assert all(user.is_active for user in users)

    @pytest.mark.asyncio
    async def test_repository_pattern_with_sqlite(self, temp_db_with_users):
        """SQLite를 사용한 Repository 패턴과 Pydantic 모델 통합 테스트"""
        from tests.fixtures import UserRepository

        repo = UserRepository(temp_db_with_users)

        # 단일 사용자 조회
        user = await repo.get_user_by_id(1)
        assert isinstance(user, User)
        assert user.name == "김철수"
        assert user.email == "kim@example.com"
        assert user.is_active is True

        # 존재하지 않는 사용자 조회
        user = await repo.get_user_by_id(999)
        assert user is None

        # 활성 사용자 목록 조회
        active_users = await repo.get_users_by_activity(True)
        assert len(active_users) == 2
        assert all(isinstance(user, User) for user in active_users)
        assert all(user.is_active for user in active_users)

        # 비활성 사용자 목록 조회
        inactive_users = await repo.get_users_by_activity(False)
        assert len(inactive_users) == 1
        assert isinstance(inactive_users[0], User)
        assert inactive_users[0].name == "박민수"
        assert inactive_users[0].is_active is False

        # 활성 사용자 수 조회
        count = await repo.count_active(True)
        assert count == 2


class TestSQLiteWithSqlLoader:
    """SQLite와 SQL 로더 통합 테스트"""

    @pytest.fixture
    async def temp_db_with_sql(self):
        """SQL 파일과 함께 SQLite 데이터베이스 픽스처"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            db_path = temp_file.name

        with tempfile.TemporaryDirectory() as temp_dir:
            sql_dir = Path(temp_dir)

            # SQL 파일 생성
            (sql_dir / "users.sql").write_text("""
-- name=get_user_by_id
SELECT id, name, email, is_active
FROM users
WHERE id = :id

-- name=count_active_users
SELECT COUNT(*)
FROM users
WHERE is_active = :active

-- name=insert_user
INSERT INTO users (name, email, is_active)
VALUES (:name, :email, :is_active)
""".strip())

            # DSN 생성
            dsn = f"sqlite:///{db_path}"

            try:
                # PyBatis 인스턴스 생성 (SQL 디렉토리 포함)
                db = PyBatis(dsn=dsn, sql_dir=sql_dir)
                await db.connect()

                # 테스트용 테이블 생성
                await db.execute("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)

                yield db

            finally:
                await db.close()
                Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_fetch_with_loaded_sql(self, temp_db_with_sql):
        """SQL 파일에서 로드한 SQL로 데이터 조회 테스트"""
        # 먼저 데이터 삽입
        insert_sql = temp_db_with_sql.load_sql("users.sql", name="insert_user")
        await temp_db_with_sql.execute(insert_sql, params={"name": "테스트", "email": "test@example.com", "is_active": True})

        # 삽입된 데이터 조회
        select_sql = temp_db_with_sql.load_sql("users.sql", name="get_user_by_id")
        row = await temp_db_with_sql.fetch_one(select_sql, params={"id": 1})

        assert row is not None
        assert row["name"] == "테스트"
        assert row["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_count_with_loaded_sql(self, temp_db_with_sql):
        """SQL 파일에서 로드한 SQL로 카운트 테스트"""
        # 데이터 삽입
        insert_sql = temp_db_with_sql.load_sql("users.sql", name="insert_user")
        await temp_db_with_sql.execute(insert_sql, params={"name": "활성사용자", "email": "active@example.com", "is_active": True})
        await temp_db_with_sql.execute(insert_sql, params={"name": "비활성사용자", "email": "inactive@example.com", "is_active": False})

        # 활성 사용자 수 조회
        count_sql = temp_db_with_sql.load_sql("users.sql", name="count_active_users")
        count = await temp_db_with_sql.fetch_val(count_sql, params={"active": True})

        assert count == 1


class TestSQLiteRepository:
    """SQLite를 사용한 Repository 패턴 테스트"""

    @pytest.fixture
    async def user_repository_with_sqlite(self):
        """SQLite를 사용하는 UserRepository 픽스처"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            db_path = temp_file.name

        dsn = f"sqlite:///{db_path}"

        try:
            from tests.fixtures import UserRepository

            db = PyBatis(dsn=dsn)
            await db.connect()

            # 테이블 생성
            await db.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            repository = UserRepository(db)
            yield repository

        finally:
            await db.close()
            Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_repository_with_real_database(self, user_repository_with_sqlite):
        """실제 데이터베이스를 사용한 Repository 테스트"""
        repo = user_repository_with_sqlite

        # 먼저 사용자 데이터 삽입 (SQL을 직접 실행)
        await repo.db.execute(
            "INSERT INTO users (name, email, is_active) VALUES (:name, :email, :is_active)",
            params={"name": "실제사용자", "email": "real@example.com", "is_active": True},
        )

        # Repository 메서드로 데이터 조회
        count = await repo.count_active(active=True)
        assert count == 1


class TestSQLiteSchemaBasedBooleanConversion:
    """SQLite 스키마 기반 boolean 자동 변환 테스트"""

    @pytest.fixture
    async def temp_db_with_boolean_schema(self):
        """BOOLEAN 타입 컬럼이 있는 임시 SQLite 데이터베이스 픽스처"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            db_path = temp_file.name

        dsn = f"sqlite:///{db_path}"

        try:
            db = PyBatis(dsn=dsn)
            await db.connect()

            # BOOLEAN 타입으로 명시적으로 정의된 테이블 생성
            await db.execute("""
                CREATE TABLE test_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_verified BOOLEAN DEFAULT FALSE,
                    has_premium BOOLEAN DEFAULT FALSE
                )
            """)

            # 테스트 데이터 삽입
            await db.execute(
                "INSERT INTO test_users (name, email, is_active, is_verified, has_premium) VALUES (:name, :email, :is_active, :is_verified, :has_premium)",
                params={"name": "테스트사용자1", "email": "test1@example.com", "is_active": True, "is_verified": False, "has_premium": True},
            )
            await db.execute(
                "INSERT INTO test_users (name, email, is_active, is_verified, has_premium) VALUES (:name, :email, :is_active, :is_verified, :has_premium)",
                params={"name": "테스트사용자2", "email": "test2@example.com", "is_active": False, "is_verified": True, "has_premium": False},
            )

            yield db

        finally:
            await db.close()
            Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_schema_based_boolean_conversion_fetch_one(self, temp_db_with_boolean_schema):
        """스키마 기반 boolean 변환 - fetch_one 테스트"""
        row = await temp_db_with_boolean_schema.fetch_one(
            "SELECT id, name, email, is_active, is_verified, has_premium FROM test_users WHERE name = :name",
            params={"name": "테스트사용자1"},
        )

        assert row is not None
        assert row["name"] == "테스트사용자1"
        assert row["email"] == "test1@example.com"

        # 스키마 기반 boolean 자동 변환 확인
        assert row["is_active"] is True  # True -> True
        assert row["is_verified"] is False  # False -> False
        assert row["has_premium"] is True  # True -> True

        # 타입 확인
        assert isinstance(row["is_active"], bool)
        assert isinstance(row["is_verified"], bool)
        assert isinstance(row["has_premium"], bool)

    @pytest.mark.asyncio
    async def test_schema_based_boolean_conversion_fetch_all(self, temp_db_with_boolean_schema):
        """스키마 기반 boolean 변환 - fetch_all 테스트"""
        rows = await temp_db_with_boolean_schema.fetch_all(
            "SELECT id, name, email, is_active, is_verified, has_premium FROM test_users ORDER BY id"
        )

        assert len(rows) == 2

        # 첫 번째 사용자
        user1 = rows[0]
        assert user1["name"] == "테스트사용자1"
        assert user1["is_active"] is True
        assert user1["is_verified"] is False
        assert user1["has_premium"] is True
        assert all(isinstance(user1[col], bool) for col in ["is_active", "is_verified", "has_premium"])

        # 두 번째 사용자
        user2 = rows[1]
        assert user2["name"] == "테스트사용자2"
        assert user2["is_active"] is False
        assert user2["is_verified"] is True
        assert user2["has_premium"] is False
        assert all(isinstance(user2[col], bool) for col in ["is_active", "is_verified", "has_premium"])

    @pytest.mark.asyncio
    async def test_schema_info_caching(self, temp_db_with_boolean_schema):
        """스키마 정보 캐싱 테스트"""
        db = temp_db_with_boolean_schema

        # 첫 번째 쿼리 - 스키마 정보 로드
        await db.fetch_one("SELECT * FROM test_users WHERE id = 1")

        # 스키마 캐시 확인
        assert "test_users" in db._table_schemas
        schema = db._table_schemas["test_users"]
        assert schema["is_active"] == "BOOLEAN"
        assert schema["is_verified"] == "BOOLEAN"
        assert schema["has_premium"] == "BOOLEAN"
        assert schema["name"] == "TEXT"
        assert schema["email"] == "TEXT"

    @pytest.mark.asyncio
    async def test_non_boolean_columns_unchanged(self, temp_db_with_boolean_schema):
        """boolean이 아닌 컬럼은 변환되지 않는지 테스트"""
        row = await temp_db_with_boolean_schema.fetch_one(
            "SELECT id, name, email FROM test_users WHERE id = 1"
        )

        assert row is not None
        assert isinstance(row["id"], int)
        assert isinstance(row["name"], str)
        assert isinstance(row["email"], str)

    @pytest.mark.asyncio
    async def test_table_name_extraction(self, temp_db_with_boolean_schema):
        """SQL에서 테이블명 추출 테스트"""
        db = temp_db_with_boolean_schema

        # 다양한 SQL 패턴에서 테이블명 추출 테스트
        test_cases = [
            ("SELECT * FROM test_users", "test_users"),
            ("SELECT id, name FROM test_users WHERE id = 1", "test_users"),
            ("UPDATE test_users SET name = 'test'", "test_users"),
            ("INSERT INTO test_users (name) VALUES ('test')", "test_users"),
        ]

        for sql, expected_table in test_cases:
            table_name = await db._extract_table_name_from_sql(sql)
            assert table_name == expected_table