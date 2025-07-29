"""
PyBatis 메인 클래스

README.md에서 제시한 API를 구현합니다.
"""

import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, List, Optional, Union
from urllib.parse import urlparse

if TYPE_CHECKING:
    from .sql_loader import SqlLoader

logger = logging.getLogger(__name__)


class PyBatis:
    """
    pyBatis의 메인 클래스

    DSN을 통해 데이터베이스에 연결하고,
    fetch_val, fetch_one, fetch_all, execute 메서드를 제공합니다.
    """

    def __init__(
        self,
        dsn: Optional[str] = None,
        sql_dir: Optional[Union[str, Path]] = None,
    ):
        """
        PyBatis 인스턴스를 초기화합니다.

        Args:
            dsn: 데이터베이스 연결 문자열 (예: "sqlite:///path/to/db.sqlite")
            sql_dir: SQL 파일들이 있는 디렉토리 경로 (옵션)
        """
        self.dsn = dsn
        self._connection = None
        self.sql_loader: Optional["SqlLoader"] = None
        self._db_type: Optional[str] = None  # 데이터베이스 타입 저장
        self._table_schemas: Dict[str, Dict[str, str]] = {}  # 테이블 스키마 캐시

        # 쿼리 로깅 관련 속성
        self._query_logging_enabled = False
        self._query_logging_level = logging.INFO

        # 쿼리 모니터링 관련 속성
        self._query_monitoring_enabled = False
        self._query_stats = None
        self._slow_query_threshold = 1.0  # 기본 1초

        # SQL 디렉토리가 제공되면 SQL 로더 초기화
        if sql_dir:
            self.set_sql_loader_dir(sql_dir)

    def enable_query_logging(self, level: int = logging.INFO) -> None:
        """
        쿼리 로깅을 활성화합니다.

        Args:
            level: 로깅 레벨 (기본값: logging.INFO)
        """
        self._query_logging_enabled = True
        self._query_logging_level = level
        logger.info("쿼리 로깅이 활성화되었습니다.")

    def disable_query_logging(self) -> None:
        """쿼리 로깅을 비활성화합니다."""
        self._query_logging_enabled = False
        logger.info("쿼리 로깅이 비활성화되었습니다.")

    def enable_query_monitoring(self) -> None:
        """쿼리 모니터링을 활성화합니다."""
        self._query_monitoring_enabled = True
        self._query_stats = {
            "total_queries": 0,
            "method_counts": defaultdict(int),
            "execution_times": [],
            "slow_queries": [],
        }
        logger.info("쿼리 모니터링이 활성화되었습니다.")

    def disable_query_monitoring(self) -> None:
        """쿼리 모니터링을 비활성화합니다."""
        self._query_monitoring_enabled = False
        self._query_stats = None
        logger.info("쿼리 모니터링이 비활성화되었습니다.")

    def get_query_stats(self) -> Optional[Dict[str, Any]]:
        """
        쿼리 통계를 반환합니다.

        Returns:
            쿼리 통계 딕셔너리 또는 None (모니터링이 비활성화된 경우)
        """
        if not self._query_monitoring_enabled or self._query_stats is None:
            return None

        # 통계 복사본 반환 (원본 보호)
        return {
            "total_queries": self._query_stats["total_queries"],
            "method_counts": dict(self._query_stats["method_counts"]),
            "execution_times": self._query_stats["execution_times"].copy(),
            "slow_queries": self._query_stats["slow_queries"].copy(),
            "average_execution_time": (
                sum(self._query_stats["execution_times"]) / len(self._query_stats["execution_times"])
                if self._query_stats["execution_times"] else 0
            ),
        }

    def reset_query_stats(self) -> None:
        """쿼리 통계를 초기화합니다."""
        if self._query_monitoring_enabled and self._query_stats is not None:
            self._query_stats = {
                "total_queries": 0,
                "method_counts": defaultdict(int),
                "execution_times": [],
                "slow_queries": [],
            }
            logger.info("쿼리 통계가 초기화되었습니다.")

    def set_slow_query_threshold(self, threshold: float) -> None:
        """
        느린 쿼리 임계값을 설정합니다.

        Args:
            threshold: 임계값 (초 단위)
        """
        self._slow_query_threshold = threshold
        logger.info(f"느린 쿼리 임계값이 {threshold}초로 설정되었습니다.")

    def _log_query_execution(self, method: str, sql: str, params: Optional[Dict[str, Any]], execution_time: float) -> None:
        """
        쿼리 실행을 로깅합니다.

        Args:
            method: 실행된 메서드명
            sql: 실행된 SQL 문
            params: SQL 파라미터
            execution_time: 실행 시간 (초)
        """
        if self._query_logging_enabled:
            # SQL 문을 한 줄로 정리
            clean_sql = " ".join(sql.split())

            log_message = f"SQL 실행 ({method}): {clean_sql}"
            if params:
                log_message += f", params: {params}"
            log_message += f", 실행 시간: {execution_time:.4f}초"

            logger.log(self._query_logging_level, log_message)

            # 느린 쿼리 경고
            if execution_time > self._slow_query_threshold:
                logger.warning(f"느린 쿼리 감지: {execution_time:.4f}초 (임계값: {self._slow_query_threshold}초) - {clean_sql}")

    def _record_query_stats(self, method: str, sql: str, execution_time: float) -> None:
        """
        쿼리 통계를 기록합니다.

        Args:
            method: 실행된 메서드명
            sql: 실행된 SQL 문
            execution_time: 실행 시간 (초)
        """
        if self._query_monitoring_enabled and self._query_stats is not None:
            self._query_stats["total_queries"] += 1
            self._query_stats["method_counts"][method] += 1
            self._query_stats["execution_times"].append(execution_time)

            # 느린 쿼리 기록
            if execution_time > self._slow_query_threshold:
                clean_sql = " ".join(sql.split())
                self._query_stats["slow_queries"].append({
                    "sql": clean_sql,
                    "execution_time": execution_time,
                    "method": method,
                    "timestamp": time.time(),
                })

    async def _execute_with_monitoring(self, method: str, sql: str, params: Optional[Dict[str, Any]], executor_func) -> Any:
        """
        모니터링과 함께 쿼리를 실행합니다.

        Args:
            method: 실행할 메서드명
            sql: 실행할 SQL 문
            params: SQL 파라미터
            executor_func: 실제 실행할 함수

        Returns:
            쿼리 실행 결과
        """
        start_time = time.time()

        try:
            result = await executor_func()
            return result
        finally:
            execution_time = time.time() - start_time

            # 로깅 및 모니터링
            self._log_query_execution(method, sql, params, execution_time)
            self._record_query_stats(method, sql, execution_time)

    async def _get_table_schema(self, table_name: str) -> Dict[str, str]:
        """
        테이블의 스키마 정보를 가져옵니다.

        Args:
            table_name: 테이블명

        Returns:
            컬럼명 -> 데이터 타입 매핑 딕셔너리
        """
        if table_name in self._table_schemas:
            return self._table_schemas[table_name]

        if self._db_type == "sqlite" and hasattr(self._connection, 'execute'):
            # SQLite PRAGMA를 사용하여 테이블 스키마 정보 가져오기
            async with self._connection.execute(f"PRAGMA table_info({table_name})") as cursor:
                columns = await cursor.fetchall()
                schema = {}
                for col in columns:
                    col_dict = dict(col)
                    col_name = col_dict['name']
                    col_type = col_dict['type'].upper()
                    schema[col_name] = col_type

                self._table_schemas[table_name] = schema
                return schema

        return {}

    async def _extract_table_name_from_sql(self, sql: str) -> Optional[str]:
        """
        SQL 문에서 테이블명을 추출합니다.

        Args:
            sql: SQL 문

        Returns:
            테이블명 또는 None
        """
        import re

        # 간단한 SELECT 문에서 테이블명 추출
        # FROM 절에서 테이블명을 찾는 정규식
        patterns = [
            r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',  # FROM table_name
            r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)',  # UPDATE table_name
            r'INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)',  # INSERT INTO table_name
        ]

        sql_upper = sql.upper()
        for pattern in patterns:
            match = re.search(pattern, sql_upper)
            if match:
                return match.group(1).lower()

        return None

    async def _convert_row_data_with_schema(self, row_data: Dict[str, Any], table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        데이터베이스 스키마 정보를 사용하여 데이터 타입을 자동 변환합니다.

        Args:
            row_data: 데이터베이스에서 가져온 행 데이터
            table_name: 테이블명 (옵션)

        Returns:
            변환된 행 데이터
        """
        if not row_data or self._db_type != "sqlite":
            return row_data

        # 테이블 스키마 정보가 있는 경우에만 변환 수행
        if table_name:
            try:
                schema = await self._get_table_schema(table_name)
                converted_data = {}

                for key, value in row_data.items():
                    col_type = schema.get(key, '').upper()

                    # SQLite에서 BOOLEAN 타입으로 정의된 컬럼을 boolean으로 변환
                    if col_type == 'BOOLEAN' and isinstance(value, int) and value in (0, 1):
                        converted_data[key] = bool(value)
                    else:
                        converted_data[key] = value

                return converted_data
            except Exception as e:
                # 스키마 정보를 가져올 수 없는 경우 원본 데이터 반환
                logger.debug(f"스키마 정보를 가져올 수 없습니다: {e}")
                return row_data

        return row_data

    async def _convert_rows_data_with_schema(self, rows_data: List[Dict[str, Any]], table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        스키마 정보를 사용하여 여러 행의 데이터를 변환합니다.

        Args:
            rows_data: 데이터베이스에서 가져온 행 데이터 리스트
            table_name: 테이블명 (옵션)

        Returns:
            변환된 행 데이터 리스트
        """
        if not rows_data:
            return rows_data

        # 첫 번째 행으로 스키마 정보를 가져오고 모든 행에 적용
        converted_rows = []
        for row in rows_data:
            converted_row = await self._convert_row_data_with_schema(row, table_name)
            converted_rows.append(converted_row)

        return converted_rows

    def set_sql_loader_dir(self, sql_dir: Union[str, Path]) -> None:
        """
        SQL 로더 디렉토리를 설정합니다.

        Args:
            sql_dir: SQL 파일들이 있는 디렉토리 경로
        """
        from .sql_loader import SqlLoader

        self.sql_loader = SqlLoader(sql_dir)

    def set_sql_loader(self, sql_loader: "SqlLoader") -> None:
        """
        SQL 로더를 직접 설정합니다.

        Args:
            sql_loader: SqlLoader 인스턴스
        """
        self.sql_loader = sql_loader

    def load_sql(self, filename: str, name: Optional[str] = None) -> str:
        """
        SQL 파일에서 SQL 문을 로드합니다.

        Args:
            filename: SQL 파일명
            name: 로드할 SQL의 이름 (옵션)

        Returns:
            로드된 SQL 문

        Raises:
            ValueError: SQL 로더가 설정되지 않은 경우
        """
        if self.sql_loader is None:
            raise ValueError(
                "SQL 로더가 설정되지 않았습니다. set_sql_loader_dir() 또는 set_sql_loader()를 호출하세요."
            )

        return self.sql_loader.load_sql(filename, name)

    def _parse_dsn(self) -> tuple[str, str]:
        """
        DSN을 파싱하여 데이터베이스 타입과 연결 정보를 반환합니다.

        Returns:
            (db_type, connection_info) 튜플

        Raises:
            ValueError: 지원하지 않는 DSN 형식인 경우
        """
        if not self.dsn:
            raise ValueError("DSN이 설정되지 않았습니다.")

        parsed = urlparse(self.dsn)
        db_type = parsed.scheme

        if db_type == "sqlite":
            # SQLite: sqlite:///path/to/db.sqlite
            db_path = parsed.path
            if db_path.startswith("///"):
                db_path = db_path[3:]  # file:///path -> /path
            elif db_path.startswith("/"):
                db_path = db_path[1:]  # /path -> path (상대 경로)
            return db_type, db_path
        else:
            raise ValueError(f"지원하지 않는 데이터베이스 타입: {db_type}")

    async def connect(self) -> None:
        """
        데이터베이스에 연결합니다.
        DSN을 파싱하여 적절한 드라이버로 연결합니다.
        """
        if self.dsn is None:
            raise ValueError("DSN이 설정되지 않았습니다.")

        db_type, connection_info = self._parse_dsn()
        self._db_type = db_type  # 데이터베이스 타입 저장

        logger.info(f"데이터베이스 연결 중: {db_type}")

        if db_type == "sqlite":
            await self._connect_sqlite(connection_info)
        else:
            raise NotImplementedError(f"데이터베이스 타입 '{db_type}'는 아직 구현되지 않았습니다.")

    async def _connect_sqlite(self, db_path: str) -> None:
        """
        SQLite 데이터베이스에 연결합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        try:
            import aiosqlite
        except ImportError:
            raise ImportError(
                "aiosqlite가 설치되지 않았습니다. 'pip install aiosqlite' 또는 'pip install pybatis[sqlite]'를 실행하세요."
            )

        # aiosqlite 연결 생성
        self._connection = await aiosqlite.connect(db_path)
        # Row 팩토리 설정으로 딕셔너리 형태로 결과 반환
        self._connection.row_factory = aiosqlite.Row

        logger.info(f"SQLite 데이터베이스에 연결되었습니다: {db_path}")

    async def fetch_val(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        단일 스칼라 값을 반환합니다.

        Args:
            sql: 실행할 SQL 문
            params: SQL 파라미터

        Returns:
            단일 스칼라 값 (예: COUNT, MAX, MIN 등의 결과)
        """
        if self._connection is None:
            raise RuntimeError("데이터베이스에 연결되지 않았습니다.")

        async def executor():
            logger.debug(f"SQL 실행 (fetch_val): {sql}, params: {params}")

            # aiosqlite 연결인 경우 (aiosqlite.Connection 타입 체크)
            if hasattr(self._connection, 'execute') and hasattr(self._connection, 'row_factory'):
                async with self._connection.execute(sql, params or {}) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else None
            else:
                # 테스트용 MockConnection
                return await self._connection.fetchval(sql, params)

        return await self._execute_with_monitoring("fetch_val", sql, params, executor)

    async def fetch_one(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        하나의 레코드를 반환합니다.

        Args:
            sql: 실행할 SQL 문
            params: SQL 파라미터

        Returns:
            레코드 딕셔너리 또는 None
        """
        if self._connection is None:
            raise RuntimeError("데이터베이스에 연결되지 않았습니다.")

        async def executor():
            logger.debug(f"SQL 실행 (fetch_one): {sql}, params: {params}")

            # SQL에서 테이블명 추출
            table_name = await self._extract_table_name_from_sql(sql)

            # aiosqlite 연결인 경우
            if hasattr(self._connection, 'execute') and hasattr(self._connection, 'row_factory'):
                async with self._connection.execute(sql, params or {}) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        return None
                    row_data = dict(row)
                    return await self._convert_row_data_with_schema(row_data, table_name)
            else:
                # 테스트용 MockConnection
                row = await self._connection.fetchrow(sql, params)
                if row is None:
                    return None
                row_data = dict(row)
                return await self._convert_row_data_with_schema(row_data, table_name)

        return await self._execute_with_monitoring("fetch_one", sql, params, executor)

    async def fetch_all(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        모든 레코드를 반환합니다.

        Args:
            sql: 실행할 SQL 문
            params: SQL 파라미터

        Returns:
            레코드 딕셔너리들의 리스트
        """
        if self._connection is None:
            raise RuntimeError("데이터베이스에 연결되지 않았습니다.")

        async def executor():
            logger.debug(f"SQL 실행 (fetch_all): {sql}, params: {params}")

            # SQL에서 테이블명 추출
            table_name = await self._extract_table_name_from_sql(sql)

            # aiosqlite 연결인 경우
            if hasattr(self._connection, 'execute') and hasattr(self._connection, 'row_factory'):
                async with self._connection.execute(sql, params or {}) as cursor:
                    rows = await cursor.fetchall()
                    rows_data = [dict(row) for row in rows]
                    return await self._convert_rows_data_with_schema(rows_data, table_name)
            else:
                # 테스트용 MockConnection
                rows = await self._connection.fetch(sql, params)
                rows_data = [dict(row) for row in rows]
                return await self._convert_rows_data_with_schema(rows_data, table_name)

        return await self._execute_with_monitoring("fetch_all", sql, params, executor)

    async def execute(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        SQL 문을 실행합니다 (INSERT, UPDATE, DELETE).

        Args:
            sql: 실행할 SQL 문
            params: SQL 파라미터

        Returns:
            영향받은 행의 수 또는 기타 실행 결과
        """
        if self._connection is None:
            raise RuntimeError("데이터베이스에 연결되지 않았습니다.")

        async def executor():
            logger.debug(f"SQL 실행 (execute): {sql}, params: {params}")

            # aiosqlite 연결인 경우
            if hasattr(self._connection, 'execute') and hasattr(self._connection, 'row_factory'):
                async with self._connection.execute(sql, params or {}) as cursor:
                    # SQLite는 lastrowid (INSERT의 경우) 또는 rowcount (UPDATE/DELETE의 경우) 반환
                    return cursor.lastrowid or cursor.rowcount
            else:
                # 테스트용 MockConnection
                return await self._connection.execute(sql, params)

        return await self._execute_with_monitoring("execute", sql, params, executor)

    async def close(self) -> None:
        """
        데이터베이스 연결을 닫습니다.
        """
        if self._connection:
            if hasattr(self._connection, 'close') and hasattr(self._connection, 'row_factory'):
                # aiosqlite 연결
                await self._connection.close()
            else:
                # 테스트용 MockConnection
                await self._connection.close()
            self._connection = None
            logger.info("데이터베이스 연결이 닫혔습니다.")

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator["PyBatis", None]:
        """
        트랜잭션 컨텍스트 매니저를 제공합니다.

        트랜잭션 내에서 예외가 발생하면 자동으로 롤백되고,
        정상적으로 완료되면 커밋됩니다.

        Yields:
            트랜잭션이 활성화된 PyBatis 인스턴스

        Example:
            ```python
            async with pybatis.transaction() as tx:
                await tx.execute("INSERT INTO users (name) VALUES (?)", {"name": "John"})
                await tx.execute("INSERT INTO profiles (user_id) VALUES (?)", {"user_id": 1})
            ```
        """
        if self._connection is None:
            raise RuntimeError("데이터베이스에 연결되지 않았습니다.")

        # aiosqlite 연결인 경우
        if hasattr(self._connection, 'execute') and hasattr(self._connection, 'row_factory'):
            # SQLite는 기본적으로 autocommit이 비활성화되어 있음
            # 트랜잭션 시작
            if self._query_logging_enabled:
                logger.log(self._query_logging_level, "트랜잭션 시작")

            await self._connection.execute("BEGIN")
            try:
                yield self
                # 정상 완료 시 커밋
                await self._connection.commit()
                if self._query_logging_enabled:
                    logger.log(self._query_logging_level, "트랜잭션 커밋")
            except Exception:
                # 예외 발생 시 롤백
                await self._connection.rollback()
                if self._query_logging_enabled:
                    logger.log(self._query_logging_level, "트랜잭션 롤백")
                raise
        else:
            # 테스트용 MockConnection - 단순히 self 반환
            if self._query_logging_enabled:
                logger.log(self._query_logging_level, "트랜잭션 시작 (MockConnection)")
            yield self
            if self._query_logging_enabled:
                logger.log(self._query_logging_level, "트랜잭션 완료 (MockConnection)")

    async def __aenter__(self) -> "PyBatis":
        """비동기 컨텍스트 매니저 진입"""
        if self.dsn and self._connection is None:
            await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """비동기 컨텍스트 매니저 종료"""
        await self.close()
