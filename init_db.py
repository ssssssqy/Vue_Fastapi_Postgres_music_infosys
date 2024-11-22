import asyncio
from database import engine
from models import Base

async def init_models():
    async with engine.begin() as conn:
        # 删除现有表格并重新创建（谨慎操作）
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表格创建完成！")

if __name__ == "__main__":
    asyncio.run(init_models())
