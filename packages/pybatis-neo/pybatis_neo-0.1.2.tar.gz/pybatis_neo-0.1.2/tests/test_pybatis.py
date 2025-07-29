"""
PyBatis 메인 클래스의 테스트

README.md에서 제시한 새로운 API를 테스트합니다.
"""

from typing import List, Optional

import pytest

from pybatis import PyBatis
from tests.fixtures import User, MockConnection


class TestPyBatis:
    """PyBatis 클래스의 테스트"""

    @pytest.fixture
    def mock_connection(self):
        """테스트용 연결 픽스처"""
        return MockConnection()

    @pytest.fixture
    def pybatis(self, mock_connection):
        """테스트용 PyBatis 인스턴스"""
        db = PyBatis()
        db._connection = mock_connection  # 테스트용 연결 주입
        return db

    @pytest.mark.asyncio
    async def test_fetch_val(self, pybatis, mock_connection):
        """fetch_val 메서드 테스트"""
        sql = "SELECT COUNT(*) FROM users WHERE is_active = :active"
        params = {"active": True}

        result = await pybatis.fetch_val(sql, params=params)

        assert result == 5
        assert sql in mock_connection.executed_sql
        assert params in mock_connection.executed_params

    @pytest.mark.asyncio
    async def test_fetch_one(self, pybatis, mock_connection):
        """fetch_one 메서드 테스트"""
        sql = "SELECT id, name, email, is_active FROM users WHERE id = :user_id"
        params = {"user_id": 1}

        result = await pybatis.fetch_one(sql, params=params)

        assert result is not None
        assert result["id"] == 1
        assert result["name"] == "테스트사용자"
        assert sql in mock_connection.executed_sql
        assert params in mock_connection.executed_params

    @pytest.mark.asyncio
    async def test_fetch_all(self, pybatis, mock_connection):
        """fetch_all 메서드 테스트"""
        sql = (
            "SELECT id, name, email, is_active FROM users "
            "WHERE is_active = :active_status"
        )
        params = {"active_status": True}

        result = await pybatis.fetch_all(sql, params=params)

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        assert sql in mock_connection.executed_sql
        assert params in mock_connection.executed_params

    @pytest.mark.asyncio
    async def test_execute(self, pybatis, mock_connection):
        """execute 메서드 테스트"""
        sql = "INSERT INTO users (name, email) VALUES (:name, :email)"
        params = {"name": "새사용자", "email": "new@example.com"}

        result = await pybatis.execute(sql, params=params)

        assert result == 1
        assert sql in mock_connection.executed_sql
        assert params in mock_connection.executed_params


class TestUserRepository:
    """README.md 예시의 UserRepository 테스트"""

    @pytest.fixture
    def mock_connection(self):
        """테스트용 연결 픽스처"""
        return MockConnection()

    @pytest.fixture
    def pybatis(self, mock_connection):
        """테스트용 PyBatis 인스턴스"""
        db = PyBatis()
        db._connection = mock_connection
        return db

    @pytest.fixture
    def user_repository(self, pybatis):
        """테스트용 UserRepository 인스턴스"""
        from tests.fixtures import UserRepository

        return UserRepository(pybatis)

    @pytest.mark.asyncio
    async def test_count_active(self, user_repository):
        """count_active 메서드 테스트"""
        count = await user_repository.count_active(active=True)
        assert count == 5

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_repository):
        """get_user_by_id 메서드 테스트"""
        user = await user_repository.get_user_by_id(user_id=1)

        assert isinstance(user, User)
        assert user.id == 1
        assert user.name == "테스트사용자"
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_repository):
        """존재하지 않는 사용자 조회 테스트"""
        user = await user_repository.get_user_by_id(user_id=999)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_users_by_activity(self, user_repository):
        """get_users_by_activity 메서드 테스트"""
        users = await user_repository.get_users_by_activity(active_status=True)

        assert len(users) == 2
        assert all(isinstance(user, User) for user in users)
        assert all(user.is_active for user in users)


class TestPyBatisDSN:
    """PyBatis DSN 초기화 테스트"""

    def test_create_with_dsn(self):
        """DSN으로 PyBatis 인스턴스 생성 테스트"""
        dsn = "postgresql://user:pass@localhost:5432/mydb"
        db = PyBatis(dsn=dsn)

        assert db.dsn == dsn
        assert db._connection is None  # 아직 연결되지 않음

    def test_create_without_dsn(self):
        """DSN 없이 PyBatis 인스턴스 생성 테스트"""
        db = PyBatis()

        assert db.dsn is None
        assert db._connection is None
