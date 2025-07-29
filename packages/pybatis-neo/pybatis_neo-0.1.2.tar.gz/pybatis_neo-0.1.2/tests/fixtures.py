"""
테스트용 픽스처들

README.md 예시에 맞는 UserRepository 등을 포함합니다.
"""

from typing import List, Optional

from pydantic import BaseModel


class MockConnection:
    """테스트용 데이터베이스 연결 모킹"""

    def __init__(self):
        self.executed_sql = []
        self.executed_params = []
        self.mock_data = {}

    async def execute(self, sql: str, params: Optional[dict] = None) -> int:
        """SQL 실행을 모킹합니다."""
        self.executed_sql.append(sql)
        self.executed_params.append(params)
        return 1

    async def fetchval(self, sql: str, params: Optional[dict] = None) -> int:
        """스칼라 값 조회를 모킹합니다."""
        self.executed_sql.append(sql)
        self.executed_params.append(params)

        # COUNT 쿼리 모킹
        if "COUNT" in sql:
            if params and params.get("active"):
                return 5  # 활성 사용자 5명
            return 2  # 비활성 사용자 2명
        return 0

    async def fetchrow(self, sql: str, params: Optional[dict] = None) -> Optional[dict]:
        """하나의 레코드 조회를 모킹합니다."""
        self.executed_sql.append(sql)
        self.executed_params.append(params)

        if params and params.get("user_id") == 1:
            return {
                "id": 1,
                "name": "테스트사용자",
                "email": "test@example.com",
                "is_active": True,
            }
        return None

    async def fetch(self, sql: str, params: Optional[dict] = None) -> List[dict]:
        """모든 레코드 조회를 모킹합니다."""
        self.executed_sql.append(sql)
        self.executed_params.append(params)

        if params and params.get("active_status"):
            return [
                {
                    "id": 1,
                    "name": "활성사용자1",
                    "email": "active1@example.com",
                    "is_active": True,
                },
                {
                    "id": 2,
                    "name": "활성사용자2",
                    "email": "active2@example.com",
                    "is_active": True,
                },
            ]
        else:
            return [
                {
                    "id": 3,
                    "name": "비활성사용자1",
                    "email": "inactive1@example.com",
                    "is_active": False,
                },
            ]

    async def close(self) -> None:
        """연결 닫기를 모킹합니다."""
        pass


class User(BaseModel):
    """사용자 모델"""

    id: int
    name: str
    email: str
    is_active: bool


class UserRepository:
    """README.md 예시의 UserRepository"""

    def __init__(self, db):
        self.db = db

    async def count_active(self, active: bool) -> int:
        """
        활성 사용자 수를 반환합니다.
        """
        sql = "SELECT COUNT(*) FROM users WHERE is_active = :active"
        # fetch_val: 단일 스칼라 값을 바로 리턴
        return await self.db.fetch_val(sql, params={"active": active})

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        주어진 ID의 사용자 한 명을 User 모델로 반환합니다.
        """
        sql = "SELECT id, name, email, is_active FROM users WHERE id = :user_id"
        row = await self.db.fetch_one(sql, params={"user_id": user_id})

        if row is None:
            return None

        return User(**row)

    async def get_users_by_activity(self, active_status: bool) -> List[User]:
        """
        활성 상태에 따라 사용자 목록을 User 모델 리스트로 반환합니다.
        """
        sql = (
            "SELECT id, name, email, is_active FROM users "
            "WHERE is_active = :active_status"
        )
        rows = await self.db.fetch_all(sql, params={"active_status": active_status})

        return [User(**row) for row in rows]
