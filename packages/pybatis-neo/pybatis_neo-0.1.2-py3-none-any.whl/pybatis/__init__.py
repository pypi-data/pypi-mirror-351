"""
pyBatis - FastAPI를 위한 MyBatis 스타일의 SQL 매퍼

이 라이브러리는 FastAPI 백엔드 개발자를 위한 SQL 매퍼로,
Java의 MyBatis에서 영감을 받아 Pythonic한 방식으로 구현되었습니다.
"""

from .pybatis import PyBatis
from .sql_loader import SqlLoader

# FastAPI 통합 모듈은 선택적으로 import
try:
    from .fastapi import (
        PyBatisManager,
        create_pybatis_dependency,
        get_pybatis,
        transaction_context,
        startup_pybatis,
        shutdown_pybatis,
        lifespan_pybatis,
    )
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False

__version__ = "0.1.0"
__author__ = "pyBatis Contributors"

__all__ = [
    "PyBatis",
    "SqlLoader",
]

# FastAPI가 사용 가능한 경우에만 추가
if _FASTAPI_AVAILABLE:
    __all__.extend([
        "PyBatisManager",
        "create_pybatis_dependency",
        "get_pybatis",
        "transaction_context",
        "startup_pybatis",
        "shutdown_pybatis",
        "lifespan_pybatis",
    ])
