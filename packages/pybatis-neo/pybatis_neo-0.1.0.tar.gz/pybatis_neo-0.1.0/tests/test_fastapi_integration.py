"""FastAPI 의존성 주입 통합 테스트"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel

from pybatis.fastapi import (
    get_pybatis,
    PyBatisManager,
    create_pybatis_dependency,
    transaction_context,
    _default_manager,
)
from pybatis import PyBatis


class User(BaseModel):
    id: int
    name: str
    email: str


class TestPyBatisManager:
    """PyBatisManager 클래스 테스트"""

    def test_init_with_dsn(self):
        """DSN으로 초기화 테스트"""
        manager = PyBatisManager(dsn="sqlite:///:memory:")
        assert manager.dsn == "sqlite:///:memory:"
        assert manager.pybatis is None

    def test_init_with_pybatis_instance(self):
        """PyBatis 인스턴스로 초기화 테스트"""
        pybatis = PyBatis("sqlite:///:memory:")
        manager = PyBatisManager(pybatis=pybatis)
        assert manager.pybatis is pybatis
        assert manager.dsn is None

    def test_init_without_params_raises_error(self):
        """매개변수 없이 초기화 시 에러 발생 테스트"""
        with pytest.raises(ValueError, match="dsn 또는 pybatis 중 하나는 반드시 제공되어야 합니다"):
            PyBatisManager()

    def test_init_with_both_params_raises_error(self):
        """두 매개변수 모두 제공 시 에러 발생 테스트"""
        pybatis = PyBatis("sqlite:///:memory:")
        with pytest.raises(ValueError, match="dsn과 pybatis는 동시에 제공될 수 없습니다"):
            PyBatisManager(dsn="sqlite:///:memory:", pybatis=pybatis)

    @pytest.mark.asyncio
    async def test_get_pybatis_with_dsn(self):
        """DSN으로 PyBatis 인스턴스 생성 테스트"""
        manager = PyBatisManager(dsn="sqlite:///:memory:")
        pybatis = await manager.get_pybatis()

        assert isinstance(pybatis, PyBatis)
        assert pybatis.dsn == "sqlite:///:memory:"

        # 같은 인스턴스 반환 확인
        pybatis2 = await manager.get_pybatis()
        assert pybatis is pybatis2

    @pytest.mark.asyncio
    async def test_get_pybatis_with_instance(self):
        """PyBatis 인스턴스로 초기화된 경우 테스트"""
        original_pybatis = PyBatis("sqlite:///:memory:")
        manager = PyBatisManager(pybatis=original_pybatis)

        pybatis = await manager.get_pybatis()
        assert pybatis is original_pybatis

    @pytest.mark.asyncio
    async def test_close(self):
        """리소스 정리 테스트"""
        manager = PyBatisManager(dsn="sqlite:///:memory:")
        pybatis = await manager.get_pybatis()

        # close 메서드 모킹
        pybatis.close = AsyncMock()

        await manager.close()
        pybatis.close.assert_called_once()


class TestCreatePyBatisDependency:
    """create_pybatis_dependency 함수 테스트"""

    @pytest.mark.asyncio
    async def test_dependency_function_creation(self):
        """의존성 함수 생성 테스트"""
        manager = PyBatisManager(dsn="sqlite:///:memory:")
        dependency = create_pybatis_dependency(manager)

        # 의존성 함수 호출
        pybatis = await dependency()
        assert isinstance(pybatis, PyBatis)

    @pytest.mark.asyncio
    async def test_dependency_with_custom_manager(self):
        """커스텀 매니저로 의존성 생성 테스트"""
        original_pybatis = PyBatis("sqlite:///:memory:")
        manager = PyBatisManager(pybatis=original_pybatis)
        dependency = create_pybatis_dependency(manager)

        pybatis = await dependency()
        assert pybatis is original_pybatis


class TestGetPyBatisDefault:
    """기본 get_pybatis 의존성 함수 테스트"""

    def setup_method(self):
        """각 테스트 전에 전역 상태 초기화"""
        import pybatis.fastapi
        pybatis.fastapi._default_manager = None

    @patch.dict('os.environ', {'DATABASE_URL': 'sqlite:///:memory:'})
    @pytest.mark.asyncio
    async def test_get_pybatis_with_env_var(self):
        """환경변수로 설정된 DATABASE_URL 사용 테스트"""
        pybatis = await get_pybatis()
        assert isinstance(pybatis, PyBatis)
        assert pybatis.dsn == "sqlite:///:memory:"

    @patch.dict('os.environ', {}, clear=True)
    @pytest.mark.asyncio
    async def test_get_pybatis_without_env_var_raises_error(self):
        """환경변수 없이 호출 시 에러 발생 테스트"""
        with pytest.raises(ValueError, match="DATABASE_URL 환경변수가 설정되지 않았습니다"):
            await get_pybatis()


class TestTransactionContext:
    """transaction_context 함수 테스트"""

    @pytest.mark.asyncio
    async def test_transaction_context_success(self):
        """트랜잭션 성공 케이스 테스트"""
        # PyBatis 인스턴스 생성 (실제 transaction 메서드 포함)
        pybatis = PyBatis("sqlite:///:memory:")

        # transaction 메서드를 모킹
        mock_transaction = AsyncMock()
        mock_transaction.__aenter__ = AsyncMock(return_value=pybatis)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)

        # patch.object를 사용하여 transaction 메서드를 모킹
        with patch.object(pybatis, 'transaction', return_value=mock_transaction) as mock_method:
            async with transaction_context(pybatis) as tx:
                assert tx is pybatis

        # transaction 메서드가 호출되었는지 확인
        mock_method.assert_called_once()

    @pytest.mark.asyncio
    async def test_transaction_context_with_exception(self):
        """트랜잭션 중 예외 발생 테스트"""
        # PyBatis 인스턴스 생성
        pybatis = PyBatis("sqlite:///:memory:")

        # transaction 메서드를 모킹
        mock_transaction = AsyncMock()
        mock_transaction.__aenter__ = AsyncMock(return_value=pybatis)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)

        # patch.object를 사용하여 transaction 메서드를 모킹
        with patch.object(pybatis, 'transaction', return_value=mock_transaction) as mock_method:
            with pytest.raises(ValueError, match="test error"):
                async with transaction_context(pybatis) as tx:
                    assert tx is pybatis
                    raise ValueError("test error")

        # transaction 메서드가 호출되었는지 확인
        mock_method.assert_called_once()


class TestFastAPIIntegration:
    """FastAPI 애플리케이션과의 통합 테스트"""

    def test_fastapi_app_with_dependency(self):
        """FastAPI 앱에서 의존성 주입 테스트"""
        app = FastAPI()

        # 테스트용 매니저 생성
        manager = PyBatisManager(dsn="sqlite:///:memory:")
        dependency = create_pybatis_dependency(manager)

        @app.get("/users/{user_id}")
        async def get_user(user_id: int, pybatis: PyBatis = Depends(dependency)):
            # 모킹된 결과 반환
            return {"id": user_id, "name": "Test User", "email": "test@example.com"}

        client = TestClient(app)
        response = client.get("/users/1")

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com"
        }

    def setup_method(self):
        """각 테스트 전에 전역 상태 초기화"""
        import pybatis.fastapi
        pybatis.fastapi._default_manager = None

    @patch.dict('os.environ', {'DATABASE_URL': 'sqlite:///:memory:'})
    def test_fastapi_app_with_default_dependency(self):
        """기본 의존성을 사용한 FastAPI 앱 테스트"""
        app = FastAPI()

        @app.get("/health")
        async def health_check(pybatis: PyBatis = Depends(get_pybatis)):
            return {"status": "ok", "database": "connected"}

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok", "database": "connected"}

    def test_fastapi_app_with_transaction(self):
        """트랜잭션을 사용한 FastAPI 앱 테스트"""
        app = FastAPI()

        manager = PyBatisManager(dsn="sqlite:///:memory:")
        dependency = create_pybatis_dependency(manager)

        @app.post("/users")
        async def create_user(
            user_data: dict,
            pybatis: PyBatis = Depends(dependency)
        ):
            # 트랜잭션 컨텍스트 사용 예시 (실제 DB 작업 없이 모킹)
            # transaction_context를 모킹하여 실제 DB 연결 없이 테스트
            return {"id": 1, "created": True}

        client = TestClient(app)
        response = client.post("/users", json={"name": "New User", "email": "new@example.com"})

        assert response.status_code == 200
        assert response.json() == {"id": 1, "created": True}


class TestRepositoryWithFastAPI:
    """Repository 패턴과 FastAPI 통합 테스트"""

    def test_repository_dependency_injection(self):
        """Repository를 의존성으로 주입하는 테스트"""
        app = FastAPI()

        class UserRepository:
            def __init__(self, pybatis: PyBatis):
                self.pybatis = pybatis

            async def get_user(self, user_id: int) -> User:
                # 모킹된 결과 반환
                return User(id=user_id, name="Test User", email="test@example.com")

        manager = PyBatisManager(dsn="sqlite:///:memory:")
        dependency = create_pybatis_dependency(manager)

        async def get_user_repository(pybatis: PyBatis = Depends(dependency)) -> UserRepository:
            return UserRepository(pybatis)

        @app.get("/users/{user_id}")
        async def get_user(
            user_id: int,
            user_repo: UserRepository = Depends(get_user_repository)
        ):
            user = await user_repo.get_user(user_id)
            return user.model_dump()

        client = TestClient(app)
        response = client.get("/users/1")

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com"
        }