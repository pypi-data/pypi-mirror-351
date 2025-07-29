"""
SQL 파일 로더

.sql 파일에서 SQL 문을 로드하는 기능을 제공합니다.
"""

import re
from pathlib import Path
from typing import Optional, Union


class SqlLoader:
    """
    SQL 파일 로더 클래스

    .sql 파일에서 SQL 문을 로드하고,
    이름 기반으로 특정 SQL을 추출하는 기능을 제공합니다.
    """

    def __init__(self, sql_dir: Union[str, Path]):
        """
        SQL 로더를 초기화합니다.

        Args:
            sql_dir: SQL 파일들이 있는 디렉토리 경로
        """
        self.sql_dir = Path(sql_dir)
        if not self.sql_dir.exists():
            raise ValueError(f"SQL 디렉토리가 존재하지 않습니다: {self.sql_dir}")
        if not self.sql_dir.is_dir():
            raise ValueError(f"SQL 경로가 디렉토리가 아닙니다: {self.sql_dir}")

    def load_sql(self, filename: str, name: Optional[str] = None) -> str:
        """
        SQL 파일에서 SQL 문을 로드합니다.

        Args:
            filename: SQL 파일명 (예: "users.sql")
            name: 로드할 SQL의 이름 (옵션)

        Returns:
            로드된 SQL 문

        Raises:
            FileNotFoundError: SQL 파일이 존재하지 않는 경우
            ValueError: 지정된 이름의 SQL을 찾을 수 없는 경우
        """
        sql_file = self.sql_dir / filename

        if not sql_file.exists():
            raise FileNotFoundError(f"SQL 파일이 존재하지 않습니다: {sql_file}")

        content = sql_file.read_text(encoding="utf-8")

        if name is None:
            # 이름이 지정되지 않으면 전체 파일 내용 반환
            return self._clean_sql(content)

        # 이름으로 특정 SQL 추출
        return self._extract_named_sql(content, name)

    def _extract_named_sql(self, content: str, name: str) -> str:
        """
        파일 내용에서 특정 이름의 SQL을 추출합니다.

        SQL 파일 형식:
        -- name=sql_name
        SELECT * FROM table;

        Args:
            content: SQL 파일 전체 내용
            name: 추출할 SQL의 이름

        Returns:
            추출된 SQL 문

        Raises:
            ValueError: 지정된 이름의 SQL을 찾을 수 없는 경우
        """
        # 정규식으로 이름 기반 SQL 블록 찾기
        pattern = rf"--\s*name\s*=\s*{re.escape(name)}\s*\n(.*?)(?=--\s*name\s*=|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        if not match:
            raise ValueError(f"SQL with name '{name}' not found in file")

        sql = match.group(1).strip()
        return self._clean_sql(sql)

    def _clean_sql(self, sql: str) -> str:
        """
        SQL 문을 정리합니다 (불필요한 공백, 주석 제거).

        Args:
            sql: 원본 SQL 문

        Returns:
            정리된 SQL 문
        """
        # 빈 줄과 앞뒤 공백 제거
        lines = []
        for line in sql.split("\n"):
            line = line.strip()
            # 빈 줄과 단순 주석 줄 건너뛰기 (-- name= 형태는 제외)
            if line and not (line.startswith("--") and "name=" not in line):
                lines.append(line)

        return " ".join(lines) if lines else sql.strip()

    def list_sql_files(self) -> list[str]:
        """
        SQL 디렉토리의 모든 .sql 파일 목록을 반환합니다.

        Returns:
            SQL 파일명 목록
        """
        return [f.name for f in self.sql_dir.glob("*.sql")]

    def list_named_sqls(self, filename: str) -> list[str]:
        """
        특정 SQL 파일에서 이름이 지정된 SQL들의 목록을 반환합니다.

        Args:
            filename: SQL 파일명

        Returns:
            이름이 지정된 SQL들의 이름 목록
        """
        sql_file = self.sql_dir / filename

        if not sql_file.exists():
            raise FileNotFoundError(f"SQL 파일이 존재하지 않습니다: {sql_file}")

        content = sql_file.read_text(encoding="utf-8")

        # 정규식으로 모든 이름 찾기
        pattern = r"--\s*name\s*=\s*(\w+)"
        matches = re.findall(pattern, content, re.IGNORECASE)

        return matches
