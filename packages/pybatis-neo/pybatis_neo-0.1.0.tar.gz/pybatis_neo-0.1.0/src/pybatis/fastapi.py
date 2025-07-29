"""FastAPI 의존성 주입 통합 모듈

이 모듈은 PyBatis를 FastAPI와 통합하여 의존성 주입을 지원합니다.
주요 기능:
- PyBatis 인스턴스의 생명주기 관리
- FastAPI 의존성 주입 지원
- 트랜잭션 컨텍스트 관리
- 요청별 세션 관리
"""

import os
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, Callable, Awaitable

from pybatis import PyBatis


class PyBatisManager:
    """PyBatis 인스턴스의 생명주기를 관리하는 클래스

    이 클래스는 PyBatis 인스턴스를 생성하고 관리합니다.
    DSN 문자열 또는 기존 PyBatis 인스턴스를 받아서 초기화할 수 있습니다.

    Args:
        dsn: 데이터베이스 연결 문자열
        pybatis: 기존 PyBatis 인스턴스

    Raises:
        ValueError: dsn과 pybatis 중 하나만 제공되어야 함
    """

    def __init__(
        self,
        dsn: Optional[str] = None,
        pybatis: Optional[PyBatis] = None
    ) -> None:
        if dsn is None and pybatis is None:
            raise ValueError("dsn 또는 pybatis 중 하나는 반드시 제공되어야 합니다")

        if dsn is not None and pybatis is not None:
            raise ValueError("dsn과 pybatis는 동시에 제공될 수 없습니다")

        self.dsn = dsn
        self.pybatis = pybatis
        self._instance: Optional[PyBatis] = None

    async def get_pybatis(self) -> PyBatis:
        """PyBatis 인스턴스를 반환합니다.

        DSN이 제공된 경우 새로운 인스턴스를 생성하고,
        기존 인스턴스가 제공된 경우 그것을 반환합니다.

        Returns:
            PyBatis 인스턴스
        """
        if self.pybatis is not None:
            return self.pybatis

        if self._instance is None:
            self._instance = PyBatis(self.dsn)

        return self._instance

    async def close(self) -> None:
        """리소스를 정리합니다.

        생성된 PyBatis 인스턴스가 있다면 close 메서드를 호출합니다.
        """
        if self._instance is not None:
            await self._instance.close()
            self._instance = None


def create_pybatis_dependency(manager: PyBatisManager) -> Callable[[], Awaitable[PyBatis]]:
    """PyBatis 의존성 함수를 생성합니다.

    이 함수는 FastAPI의 Depends와 함께 사용할 수 있는 의존성 함수를 생성합니다.

    Args:
        manager: PyBatis 매니저 인스턴스

    Returns:
        FastAPI 의존성으로 사용할 수 있는 함수

    Example:
        ```python
        from fastapi import FastAPI, Depends
        from pybatis.fastapi import PyBatisManager, create_pybatis_dependency

        app = FastAPI()
        manager = PyBatisManager(dsn="sqlite:///:memory:")
        get_pybatis = create_pybatis_dependency(manager)

        @app.get("/users/{user_id}")
        async def get_user(user_id: int, pybatis: PyBatis = Depends(get_pybatis)):
            return await pybatis.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
        ```
    """
    async def dependency() -> PyBatis:
        return await manager.get_pybatis()

    return dependency


# 기본 매니저 인스턴스 (환경변수 기반)
_default_manager: Optional[PyBatisManager] = None


async def get_pybatis() -> PyBatis:
    """기본 PyBatis 의존성 함수

    DATABASE_URL 환경변수를 사용하여 PyBatis 인스턴스를 생성합니다.
    이 함수는 FastAPI의 Depends와 함께 사용할 수 있습니다.

    Returns:
        PyBatis 인스턴스

    Raises:
        ValueError: DATABASE_URL 환경변수가 설정되지 않은 경우

    Example:
        ```python
        from fastapi import FastAPI, Depends
        from pybatis.fastapi import get_pybatis

        app = FastAPI()

        @app.get("/users/{user_id}")
        async def get_user(user_id: int, pybatis: PyBatis = Depends(get_pybatis)):
            return await pybatis.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
        ```
    """
    global _default_manager

    if _default_manager is None:
        database_url = os.getenv("DATABASE_URL")
        if database_url is None:
            raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다")

        _default_manager = PyBatisManager(dsn=database_url)

    return await _default_manager.get_pybatis()


@asynccontextmanager
async def transaction_context(pybatis: PyBatis) -> AsyncGenerator[PyBatis, None]:
    """트랜잭션 컨텍스트 매니저

    이 함수는 PyBatis의 트랜잭션 기능을 async with 문과 함께 사용할 수 있게 해줍니다.
    트랜잭션 내에서 예외가 발생하면 자동으로 롤백되고,
    정상적으로 완료되면 커밋됩니다.

    Args:
        pybatis: PyBatis 인스턴스

    Yields:
        트랜잭션이 활성화된 PyBatis 인스턴스

    Example:
        ```python
        from fastapi import FastAPI, Depends
        from pybatis.fastapi import get_pybatis, transaction_context

        app = FastAPI()

        @app.post("/users")
        async def create_user(
            user_data: dict,
            pybatis: PyBatis = Depends(get_pybatis)
        ):
            async with transaction_context(pybatis) as tx:
                user_id = await tx.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)",
                    user_data["name"], user_data["email"]
                )
                await tx.execute(
                    "INSERT INTO user_profiles (user_id, created_at) VALUES (?, ?)",
                    user_id, datetime.now()
                )
                return {"id": user_id, "created": True}
        ```
    """
    async with pybatis.transaction() as tx:
        yield tx


# 애플리케이션 생명주기 관리를 위한 헬퍼 함수들

async def startup_pybatis(manager: Optional[PyBatisManager] = None) -> None:
    """애플리케이션 시작 시 PyBatis 초기화

    FastAPI의 lifespan 이벤트와 함께 사용할 수 있습니다.

    Args:
        manager: 사용할 PyBatis 매니저 (None인 경우 기본 매니저 사용)
    """
    if manager is None:
        # 기본 매니저 초기화를 위해 get_pybatis 호출
        await get_pybatis()
    else:
        await manager.get_pybatis()


async def shutdown_pybatis(manager: Optional[PyBatisManager] = None) -> None:
    """애플리케이션 종료 시 PyBatis 리소스 정리

    FastAPI의 lifespan 이벤트와 함께 사용할 수 있습니다.

    Args:
        manager: 정리할 PyBatis 매니저 (None인 경우 기본 매니저 사용)
    """
    global _default_manager

    if manager is None:
        if _default_manager is not None:
            await _default_manager.close()
            _default_manager = None
    else:
        await manager.close()


@asynccontextmanager
async def lifespan_pybatis(
    app,
    manager: Optional[PyBatisManager] = None
) -> AsyncGenerator[None, None]:
    """FastAPI 애플리케이션의 lifespan 컨텍스트 매니저

    애플리케이션 시작 시 PyBatis를 초기화하고,
    종료 시 리소스를 정리합니다.

    Args:
        app: FastAPI 애플리케이션 인스턴스
        manager: 사용할 PyBatis 매니저 (None인 경우 기본 매니저 사용)

    Example:
        ```python
        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        from pybatis.fastapi import lifespan_pybatis, PyBatisManager

        manager = PyBatisManager(dsn="sqlite:///:memory:")

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            async with lifespan_pybatis(app, manager):
                yield

        app = FastAPI(lifespan=lifespan)
        ```
    """
    # 시작 시 초기화
    await startup_pybatis(manager)

    try:
        yield
    finally:
        # 종료 시 정리
        await shutdown_pybatis(manager)