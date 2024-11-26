from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:123456@localhost:5432/music"

# 创建异步数据库引擎
engine = create_async_engine(DATABASE_URL, echo=True)

# 创建会话工厂
async_session = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

# 获取会话对象的依赖
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
