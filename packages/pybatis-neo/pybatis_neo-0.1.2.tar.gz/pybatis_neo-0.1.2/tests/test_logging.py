"""
쿼리 로깅 및 모니터링 기능 테스트

이 모듈은 PyBatis의 쿼리 로깅, 실행 시간 측정, 성능 모니터링 기능을 테스트합니다.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any
from unittest.mock import Mock, patch

import pytest

from pybatis import PyBatis
from tests.fixtures import MockConnection


class TestQueryLogging:
    """쿼리 로깅 기능 테스트"""

    @pytest.fixture
    def mock_connection(self):
        """테스트용 연결 픽스처"""
        return MockConnection()

    @pytest.fixture
    def pybatis_with_logging(self, mock_connection):
        """로깅이 활성화된 PyBatis 인스턴스"""
        db = PyBatis()
        db._connection = mock_connection
        db.enable_query_logging(level=logging.DEBUG)
        return db

    @pytest.mark.asyncio
    async def test_query_logging_enabled(self, pybatis_with_logging, mock_connection):
        """쿼리 로깅이 활성화되었을 때 로그가 기록되는지 테스트"""
        with patch('pybatis.pybatis.logger') as mock_logger:
            sql = "SELECT * FROM users WHERE id = :user_id"
            params = {"user_id": 1}

            await pybatis_with_logging.fetch_one(sql, params)

            # 로그가 기록되었는지 확인 (log 메서드 호출 확인)
            mock_logger.log.assert_called()
            call_args = mock_logger.log.call_args_list

            # SQL 실행 로그 확인
            assert any("SQL 실행" in str(call) for call in call_args)

    @pytest.mark.asyncio
    async def test_query_logging_disabled(self, mock_connection):
        """쿼리 로깅이 비활성화되었을 때 로그가 기록되지 않는지 테스트"""
        db = PyBatis()
        db._connection = mock_connection
        # 로깅 비활성화 (기본값)

        with patch('pybatis.pybatis.logger') as mock_logger:
            sql = "SELECT * FROM users WHERE id = :user_id"
            params = {"user_id": 1}

            await db.fetch_one(sql, params)

            # 쿼리 실행 로그가 기록되지 않았는지 확인
            log_calls = [call for call in mock_logger.log.call_args_list
                        if "SQL 실행" in str(call)]
            assert len(log_calls) == 0

    @pytest.mark.asyncio
    async def test_query_logging_with_execution_time(self, pybatis_with_logging, mock_connection):
        """쿼리 실행 시간이 로그에 포함되는지 테스트"""
        # MockConnection에 지연 시간 추가
        async def slow_fetchrow(sql, params):
            await asyncio.sleep(0.1)  # 100ms 지연
            return {"id": 1, "name": "테스트사용자"}

        mock_connection.fetchrow = slow_fetchrow

        with patch('pybatis.pybatis.logger') as mock_logger:
            sql = "SELECT * FROM users WHERE id = :user_id"
            params = {"user_id": 1}

            await pybatis_with_logging.fetch_one(sql, params)

            # 실행 시간이 포함된 로그 확인
            call_args = mock_logger.log.call_args_list
            execution_time_logs = [call for call in call_args
                                 if "실행 시간" in str(call)]
            assert len(execution_time_logs) > 0

    @pytest.mark.asyncio
    async def test_query_logging_with_parameters(self, pybatis_with_logging, mock_connection):
        """쿼리 파라미터가 로그에 포함되는지 테스트"""
        with patch('pybatis.pybatis.logger') as mock_logger:
            sql = "SELECT * FROM users WHERE id = :user_id AND name = :name"
            params = {"user_id": 1, "name": "테스트사용자"}

            await pybatis_with_logging.fetch_one(sql, params)

            # 파라미터가 포함된 로그 확인
            call_args = mock_logger.log.call_args_list
            param_logs = [call for call in call_args
                         if "params" in str(call)]
            assert len(param_logs) > 0

    @pytest.mark.asyncio
    async def test_query_logging_different_methods(self, pybatis_with_logging, mock_connection):
        """다양한 쿼리 메서드에서 로깅이 작동하는지 테스트"""
        with patch('pybatis.pybatis.logger') as mock_logger:
            # fetch_val 테스트
            await pybatis_with_logging.fetch_val("SELECT COUNT(*) FROM users")

            # fetch_all 테스트
            await pybatis_with_logging.fetch_all("SELECT * FROM users")

            # execute 테스트
            await pybatis_with_logging.execute("INSERT INTO users (name) VALUES (:name)",
                                             {"name": "새사용자"})

            # 각 메서드에 대한 로그가 기록되었는지 확인
            call_args = mock_logger.log.call_args_list
            assert len(call_args) >= 3  # 최소 3개의 로그 호출


class TestQueryMonitoring:
    """쿼리 모니터링 기능 테스트"""

    @pytest.fixture
    def mock_connection(self):
        """테스트용 연결 픽스처"""
        return MockConnection()

    @pytest.fixture
    def pybatis_with_monitoring(self, mock_connection):
        """모니터링이 활성화된 PyBatis 인스턴스"""
        db = PyBatis()
        db._connection = mock_connection
        db.enable_query_monitoring()
        return db

    @pytest.mark.asyncio
    async def test_query_monitoring_enabled(self, pybatis_with_monitoring, mock_connection):
        """쿼리 모니터링이 활성화되었을 때 통계가 수집되는지 테스트"""
        sql = "SELECT * FROM users WHERE id = :user_id"
        params = {"user_id": 1}

        await pybatis_with_monitoring.fetch_one(sql, params)

        # 쿼리 통계 확인
        stats = pybatis_with_monitoring.get_query_stats()
        assert stats is not None
        assert stats["total_queries"] == 1
        assert "fetch_one" in stats["method_counts"]

    @pytest.mark.asyncio
    async def test_query_monitoring_multiple_queries(self, pybatis_with_monitoring, mock_connection):
        """여러 쿼리 실행 시 통계가 누적되는지 테스트"""
        # 여러 쿼리 실행
        await pybatis_with_monitoring.fetch_val("SELECT COUNT(*) FROM users")
        await pybatis_with_monitoring.fetch_one("SELECT * FROM users WHERE id = 1")
        await pybatis_with_monitoring.fetch_all("SELECT * FROM users")
        await pybatis_with_monitoring.execute("INSERT INTO users (name) VALUES ('test')")

        stats = pybatis_with_monitoring.get_query_stats()
        assert stats["total_queries"] == 4
        assert stats["method_counts"]["fetch_val"] == 1
        assert stats["method_counts"]["fetch_one"] == 1
        assert stats["method_counts"]["fetch_all"] == 1
        assert stats["method_counts"]["execute"] == 1

    @pytest.mark.asyncio
    async def test_query_monitoring_execution_times(self, pybatis_with_monitoring, mock_connection):
        """쿼리 실행 시간이 기록되는지 테스트"""
        # MockConnection에 지연 시간 추가
        async def slow_fetchval(sql, params):
            await asyncio.sleep(0.05)  # 50ms 지연
            return 1

        mock_connection.fetchval = slow_fetchval

        await pybatis_with_monitoring.fetch_val("SELECT COUNT(*) FROM users")

        stats = pybatis_with_monitoring.get_query_stats()
        assert "execution_times" in stats
        assert len(stats["execution_times"]) == 1
        assert stats["execution_times"][0] >= 0.05  # 최소 50ms

    @pytest.mark.asyncio
    async def test_query_monitoring_slow_query_detection(self, pybatis_with_monitoring, mock_connection):
        """느린 쿼리 감지 기능 테스트"""
        # 로깅도 활성화 (느린 쿼리 경고를 위해)
        pybatis_with_monitoring.enable_query_logging()

        # 느린 쿼리 임계값 설정 (100ms)
        pybatis_with_monitoring.set_slow_query_threshold(0.1)

        # MockConnection에 긴 지연 시간 추가
        async def very_slow_fetchval(sql, params):
            await asyncio.sleep(0.15)  # 150ms 지연
            return 1

        mock_connection.fetchval = very_slow_fetchval

        with patch('pybatis.pybatis.logger') as mock_logger:
            await pybatis_with_monitoring.fetch_val("SELECT COUNT(*) FROM users")

            # 느린 쿼리 경고 로그 확인
            warning_calls = [call for call in mock_logger.warning.call_args_list
                           if "느린 쿼리" in str(call)]
            assert len(warning_calls) > 0

    @pytest.mark.asyncio
    async def test_query_monitoring_reset_stats(self, pybatis_with_monitoring, mock_connection):
        """쿼리 통계 초기화 기능 테스트"""
        # 몇 개의 쿼리 실행
        await pybatis_with_monitoring.fetch_val("SELECT COUNT(*) FROM users")
        await pybatis_with_monitoring.fetch_one("SELECT * FROM users WHERE id = 1")

        # 통계 확인
        stats = pybatis_with_monitoring.get_query_stats()
        assert stats["total_queries"] == 2

        # 통계 초기화
        pybatis_with_monitoring.reset_query_stats()

        # 초기화 후 통계 확인
        stats = pybatis_with_monitoring.get_query_stats()
        assert stats["total_queries"] == 0
        assert len(stats["execution_times"]) == 0

    def test_query_monitoring_disabled_by_default(self, mock_connection):
        """기본적으로 쿼리 모니터링이 비활성화되어 있는지 테스트"""
        db = PyBatis()
        db._connection = mock_connection

        # 모니터링이 비활성화된 상태에서는 통계가 None이어야 함
        stats = db.get_query_stats()
        assert stats is None


class TestQueryLoggingIntegration:
    """쿼리 로깅과 모니터링 통합 테스트"""

    @pytest.fixture
    def mock_connection(self):
        """테스트용 연결 픽스처"""
        return MockConnection()

    @pytest.fixture
    def pybatis_full_featured(self, mock_connection):
        """로깅과 모니터링이 모두 활성화된 PyBatis 인스턴스"""
        db = PyBatis()
        db._connection = mock_connection
        db.enable_query_logging(level=logging.INFO)
        db.enable_query_monitoring()
        return db

    @pytest.mark.asyncio
    async def test_logging_and_monitoring_together(self, pybatis_full_featured, mock_connection):
        """로깅과 모니터링이 함께 작동하는지 테스트"""
        with patch('pybatis.pybatis.logger') as mock_logger:
            sql = "SELECT * FROM users WHERE id = :user_id"
            params = {"user_id": 1}

            await pybatis_full_featured.fetch_one(sql, params)

            # 로깅 확인
            assert mock_logger.log.called

            # 모니터링 확인
            stats = pybatis_full_featured.get_query_stats()
            assert stats["total_queries"] == 1

    @pytest.mark.asyncio
    async def test_transaction_logging(self, pybatis_full_featured, mock_connection):
        """트랜잭션 내에서의 로깅 테스트"""
        with patch('pybatis.pybatis.logger') as mock_logger:
            async with pybatis_full_featured.transaction() as tx:
                await tx.execute("INSERT INTO users (name) VALUES (:name)", {"name": "사용자1"})
                await tx.execute("INSERT INTO users (name) VALUES (:name)", {"name": "사용자2"})

            # 트랜잭션 관련 로그 확인
            call_args = mock_logger.log.call_args_list
            transaction_logs = [call for call in call_args
                              if "트랜잭션" in str(call) or "transaction" in str(call).lower()]
            # 트랜잭션 시작과 커밋 로그가 있어야 함
            assert len(transaction_logs) >= 2