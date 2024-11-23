import asyncio
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from models import Base, User, Artist, Song, Playlist
from database import engine, async_session

admin_username = "admin"
admin_password = "admin"
one_username = "one normal user"
one_password = "one normal password"

async def init_models():
    # 删除现有表格并重新创建（谨慎操作）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表格创建完成！")

    # 插入示例数据
    async with async_session() as session:
        await insert_sample_data(session)


async def insert_sample_data(session: AsyncSession):
    # 创建用户
    admin_user = User(
        username=admin_username,
        hashed_password = hashlib.sha256(admin_password.encode()).hexdigest(),
        is_admin=True
    )
    normal_user = User(
        username=one_username,
        hashed_password=hashlib.sha256(one_password.encode()).hexdigest(),
        is_admin=False
    )

    # 创建歌手
    artist1 = Artist(name="Taylor Swift", genre="Pop")
    artist2 = Artist(name="Eminem", genre="Hip-Hop")

    # 创建歌曲
    song1 = Song(title="Love Story", genre="Pop", artist=artist1)
    song2 = Song(title="Lose Yourself", genre="Hip-Hop", artist=artist2)

    # 创建歌单
    playlist1 = Playlist(name="My Favorites", owner=normal_user)
    playlist2 = Playlist(name="Admin's Picks", owner=admin_user)

    # # 添加歌曲到歌单
    # playlist1.songs.extend([song1, song2])
    # playlist2.songs.append(song1)

    # 添加数据到会话
    session.add_all([admin_user, normal_user, artist1, artist2, song1, song2, playlist1, playlist2])

    # 提交事务
    await session.commit()
    print("示例数据插入完成！")


if __name__ == "__main__":
    asyncio.run(init_models())

