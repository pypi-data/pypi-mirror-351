# 🐍 pyBatis Neo

**MyBatis-style SQL Mapper for FastAPI - Modern and Pythonic Implementation**

[![PyPI version](https://badge.fury.io/py/pybatis-neo.svg)](https://badge.fury.io/py/pybatis-neo)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[한국어 README](README_ko.md) | [Documentation](https://pybatis-neo.readthedocs.io) | [PyPI](https://pypi.org/project/pybatis-neo/)

pyBatis Neo is an open-source SQL mapper library for FastAPI backend developers. Inspired by Java's MyBatis, it allows you to write SQL explicitly without XML, separating business logic from data access logic with a modern, Pythonic approach.

## ✨ Key Features

- 🚀 **Perfect FastAPI Integration**: Seamlessly integrates with FastAPI's dependency injection system
- 🔄 **Async Support**: High-performance asynchronous SQL execution with async/await
- 🎯 **Pydantic Model Mapping**: Automatic mapping of SQL query results to Pydantic models
- 🐍 **Pythonic Configuration**: Uses decorators and function annotations instead of XML
- 🔒 **SQL Injection Prevention**: Safe parameter binding
- 🧪 **Test-Friendly**: Easy testing with mocking and dependency injection
- 📊 **Query Monitoring**: Execution time measurement and performance monitoring
- 📁 **SQL File Loader**: Load SQL statements from external .sql files

## 📋 Requirements

- **Python 3.11+**
- FastAPI 0.104.0+
- Pydantic 2.0.0+

## 📦 Installation

```bash
pip install pybatis-neo
```

### Database Driver Installation

```bash
# PostgreSQL
pip install pybatis-neo[postgres]

# MySQL
pip install pybatis-neo[mysql]

# SQLite
pip install pybatis-neo[sqlite]

# All drivers
pip install pybatis-neo[all]
```

## 🚀 Quick Start

### 1. Define Models

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
```

### 2. Create Repository Class

```python
from typing import Optional, List
from pybatis import PyBatis
from .models import User

class UserRepository:
    def __init__(self, db: PyBatis):
        self.db = db

    async def create_user(self, name: str, email: str, is_active: bool = True) -> int:
        """Create a new user"""
        sql = """
        INSERT INTO users (name, email, is_active)
        VALUES (:name, :email, :is_active)
        """
        return await self.db.execute(sql, params={
            "name": name,
            "email": email,
            "is_active": is_active
        })

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        sql = "SELECT id, name, email, is_active FROM users WHERE id = :user_id"
        row = await self.db.fetch_one(sql, params={"user_id": user_id})
        return User(**row) if row else None

    async def get_users_by_activity(self, active_status: bool) -> List[User]:
        """Get users by activity status"""
        sql = "SELECT id, name, email, is_active FROM users WHERE is_active = :active_status"
        rows = await self.db.fetch_all(sql, params={"active_status": active_status})
        return [User(**row) for row in rows]

    async def count_active(self, active: bool) -> int:
        """Count active users"""
        sql = "SELECT COUNT(*) FROM users WHERE is_active = :active"
        return await self.db.fetch_val(sql, params={"active": active})
```

### 3. FastAPI Integration (Basic)

```python
from fastapi import FastAPI, HTTPException
from pybatis import PyBatis

app = FastAPI()

# Simple usage
@app.on_event("startup")
async def startup():
    global db
    db = PyBatis(dsn="sqlite:///example.db")
    await db.connect()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 4. FastAPI Integration (Advanced - Dependency Injection)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from pybatis import PyBatis
from pybatis.fastapi import PyBatisManager, create_pybatis_dependency

# PyBatis manager setup
manager = PyBatisManager(dsn="sqlite:///example.db")
get_pybatis = create_pybatis_dependency(manager)

# Repository dependency function
async def get_user_repository(pybatis: PyBatis = Depends(get_pybatis)) -> UserRepository:
    return UserRepository(pybatis)

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    async with manager.get_pybatis() as pybatis:
        await pybatis.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
    yield
    # Shutdown: Clean up resources
    await manager.close()

app = FastAPI(lifespan=lifespan)

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository)
):
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/active-count")
async def active_users_count(
    user_repo: UserRepository = Depends(get_user_repository)
):
    count = await user_repo.count_active(active=True)
    return {"active_user_count": count}
```

## 🔧 Advanced Features

### Query Logging and Monitoring

```python
import logging

# Enable query logging
db.enable_query_logging(level=logging.INFO)

# Enable query monitoring
db.enable_query_monitoring()

# Set slow query threshold (1 second)
db.set_slow_query_threshold(1.0)

# Get statistics
stats = db.get_query_stats()
print(f"Total queries: {stats['total_queries']}")
print(f"Average execution time: {stats['average_execution_time']:.4f}s")
```

### Transaction Management

```python
# Using transaction context manager
async with db.transaction() as tx:
    await tx.execute("INSERT INTO users (name) VALUES (:name)", {"name": "User1"})
    await tx.execute("INSERT INTO profiles (user_id) VALUES (:user_id)", {"user_id": 1})
    # Auto-commit (auto-rollback on exception)
```

### SQL File Loader

```python
# Set SQL directory
db.set_sql_loader_dir("sql/")

# Load from SQL file
sql = db.load_sql("users.sql", "get_active_users")
users = await db.fetch_all(sql, {"active": True})
```

## 🏗️ Architecture

pyBatis Neo consists of the following core components:

- **PyBatis**: Core SQL execution engine class
- **Repository Pattern**: Encapsulates domain-specific data access logic
- **DSN Connection**: Database connection string-based initialization
- **Async Support**: High-performance SQL execution with async/await
- **FastAPI Integration**: Dependency injection and lifecycle management

## 🧪 Development Setup

To develop the project locally:

```bash
# Clone repository
git clone https://github.com/jinto/pybatis.git
cd pybatis

# Create virtual environment (using uv)
uv venv
source .venv/bin/activate

# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Code formatting
black src tests
isort src tests

# Type checking
mypy src

# Run sample code
python samples/demo_sqlite_pydantic.py
python samples/fastapi_example.py
```

## 📊 Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=pybatis --cov-report=html

# Run specific test file
uv run pytest tests/test_pybatis.py
```

## 📚 Sample Code

Check out various usage examples in the `samples/` directory:

- `demo_sqlite_pydantic.py`: SQLite and Pydantic model integration demo
- `fastapi_example.py`: Complete FastAPI integration example

## 🤝 Contributing

pyBatis Neo is an open-source project. Contributions are welcome!

1. Check existing issues or create a new issue
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](https://pybatis-neo.readthedocs.io)
- [GitHub Repository](https://github.com/jinto/pybatis)
- [Issue Tracker](https://github.com/jinto/pybatis/issues)
- [PyPI](https://pypi.org/project/pybatis-neo/)
- [Changelog](CHANGELOG.md)

---

**Write clean and maintainable SQL code in FastAPI with pyBatis Neo! 🚀**
