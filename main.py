import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Query, Body, Request
from fastapi.middleware.cors import CORSMiddleware  # 导入 CORS 中间件
from datetime import datetime, timedelta
from models import User,Playlist,Song,Artist
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from database import get_session
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import hashlib
from typing import List, Optional

# 配置常量
SECRET_KEY = "adegetrgbb"  
ALGORITHM = "HS256"  # JWT 签名算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 过期时间为 30 分钟

# OAuth2PasswordBearer 用于获取请求中的 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# FastAPI 应用实例
app = FastAPI()

# 将 CORS 中间件添加到 FastAPI 应用中
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 创建 JWT Token 的函数
def create_jwt(user_id: int) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Generated Token: {token}")
    return token

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    try:
        print(f"Received token: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")  # Debugging
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token1"
            )
        result = await session.execute(select(User).where(User.id == int(user_id)))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        print(user.username)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        print(f"Token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token2"
        )


# Pydantic 模型，用于请求体验证
class UserRequest(BaseModel):
    username: str
    password: str

class SongResponse(BaseModel):
    id: int
    title: str
    genre: Optional[str]
    artist: Optional[str]  # 歌手名称，可能为空

    class Config:
        orm_mode = True

class PlaylistResponse(BaseModel):
    id: int
    name: str
    owner: Optional[str]  # 歌单的所有者用户名，可能为空

    class Config:
        orm_mode = True

# 辅助函数：检查用户密码
async def verify_password(db_session: AsyncSession, username: str, password: str) -> bool:
    result = await db_session.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if user is None:
        return False
    # 使用存储的 hashed_password 验证密码（实际应该使用更安全的哈希验证）
    return user.hashed_password == hashlib.sha256(password.encode()).hexdigest()

# 辅助函数：检查是否为管理员
async def is_admin(user_id: int, session: AsyncSession):
    result = await session.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")

# 用户登录端点：验证用户并生成 JWT
@app.post("/login/")
async def user_login(request: UserRequest, session: AsyncSession = Depends(get_session)):
    # 验证用户名和密码
    if not await verify_password(session, request.username, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    # 如果验证通过，生成 JWT
    user_result = await session.execute(select(User).filter(User.username == request.username))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 生成 JWT token
    access_token = create_jwt(user.id)
    return {"access_token": access_token, "token_type": "bearer"}

# 创建用户
@app.post("/register/")
async def create_user(request: UserRequest, session: AsyncSession = Depends(get_session)):
    # 密码加密（使用 hashlib 只是示范，实际使用更安全的方式，如 bcrypt）
    hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
    new_user = User(username=request.username, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return {"success": True, "message": "注册成功！"}

@app.get("/api/artists", response_model=List[dict])
async def get_artists(search: str = Query(None), session: AsyncSession = Depends(get_session)):
    if search:
        # 按名字模糊查询歌手
        result = await session.execute(select(Artist).where(Artist.name.contains(search)))
    else:
        # 查询所有歌手
        result = await session.execute(select(Artist))
    
    artists = result.scalars().all()
    return [{"id": artist.id, "name": artist.name, "genre": artist.genre} for artist in artists]

@app.get("/api/songs", response_model=List[SongResponse])
async def get_songs(
    search: str = Query(None), 
    limit: int = Query(10), 
    session: AsyncSession = Depends(get_session)
):

    query = select(Song).options(selectinload(Song.artist)).limit(limit)
    if search:
        query = query.where(Song.title.contains(search))

    result = await session.execute(query)
    songs = result.scalars().all()

    
    # 构造响应数据
    return [
        SongResponse(
            id=song.id,
            title=song.title,
            genre=song.genre,
            artist=song.artist.name if song.artist else None
        )
        for song in songs
    ]


# 获取所有用户创建的歌单或通过名称搜索歌单
@app.get("/api/playlists", response_model=List[PlaylistResponse])
async def get_playlists(
    search: str = Query(None),
    limit: int = Query(10),
    session: AsyncSession = Depends(get_session),
):
    query = select(Playlist).options(selectinload(Playlist.owner)).limit(limit)
    if search:
        query = query.where(Playlist.name.contains(search))
    result = await session.execute(query)
    playlists = result.scalars().all()
    return [
        PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            owner=playlist.owner.username if playlist.owner else None,
        )
        for playlist in playlists
    ]


# 获取当前用户的歌单
@app.get("/api/playlists/my", response_model=List[PlaylistResponse])
async def get_user_playlists(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Playlist).where(Playlist.owner_id == current_user.id)
    )
    playlists = result.scalars().all()
    return [
        PlaylistResponse(id=playlist.id, name=playlist.name, owner=current_user.username)
        for playlist in playlists
    ]


# 创建歌单
@app.post("/api/playlists", response_model=PlaylistResponse)
async def create_playlist(
    request: Request,
    name: str = Body(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    raw_body = await request.body()
    print(f"Raw body: {raw_body}")  # 打印原始请求体
    print(f"Received name: {name}")  # 打印 name 查看
    new_playlist = Playlist(name=name, owner_id=current_user.id)
    session.add(new_playlist)
    await session.commit()
    await session.refresh(new_playlist)
    return PlaylistResponse(id=new_playlist.id, name=new_playlist.name, owner=current_user.username)


# 删除歌单
@app.delete("/api/playlists/{playlist_id}")
async def delete_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Playlist).where(Playlist.id == playlist_id)
    )
    playlist = result.scalars().first()

    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found"
        )
    if playlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    await session.delete(playlist)
    await session.commit()
    return {"success": True, "message": "Playlist deleted"}

# 管理员：删除歌单
@app.delete("/playlists/{playlist_id}/admin/")
async def delete_playlist_admin(playlist_id: int, user_id: int, session: AsyncSession = Depends(get_session)):
    await is_admin(user_id, session)
    result = await session.execute(select(Playlist).filter(Playlist.id == playlist_id))
    playlist = result.scalars().first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    await session.delete(playlist)
    await session.commit()
    return {"msg": "Playlist deleted by admin"}

# 管理员：修改歌单
@app.put("/playlists/{playlist_id}/admin/")
async def update_playlist_admin(playlist_id: int, name: str, user_id: int, session: AsyncSession = Depends(get_session)):
    await is_admin(user_id, session)
    result = await session.execute(select(Playlist).filter(Playlist.id == playlist_id))
    playlist = result.scalars().first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    playlist.name = name
    await session.commit()
    return playlist

# 管理员：增删改歌手信息
@app.post("/artists/admin/")
async def create_artist(name: str, genre: str, user_id: int, session: AsyncSession = Depends(get_session)):
    await is_admin(user_id, session)
    new_artist = Artist(name=name, genre=genre)
    session.add(new_artist)
    await session.commit()
    await session.refresh(new_artist)
    return new_artist

@app.delete("/artists/{artist_id}/admin/")
async def delete_artist(artist_id: int, user_id: int, session: AsyncSession = Depends(get_session)):
    await is_admin(user_id, session)
    result = await session.execute(select(Artist).filter(Artist.id == artist_id))
    artist = result.scalars().first()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
    await session.delete(artist)
    await session.commit()
    return {"msg": "Artist deleted by admin"}

@app.put("/artists/{artist_id}/admin/")
async def update_artist(artist_id: int, name: str, genre: str, user_id: int, session: AsyncSession = Depends(get_session)):
    await is_admin(user_id, session)
    result = await session.execute(select(Artist).filter(Artist.id == artist_id))
    artist = result.scalars().first()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
    artist.name = name
    artist.genre = genre
    await session.commit()
    return artist

# # 获取所有用户（管理员功能）
# @app.get("/users/", response_model=List[User])
# async def get_users(session: AsyncSession = Depends(get_session)):
#     result = await session.execute(select(User))
#     users = result.scalars().all()
#     return users