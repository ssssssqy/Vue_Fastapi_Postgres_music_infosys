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

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True
        from_attributes = True

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
    songs: List

    class Config:
        orm_mode = True

class ArtistRequest(BaseModel):
    name: str
    genre: Optional[str] = None

    class Config:
        orm_mode = True

class SongRequest(BaseModel):
    title: str
    genre: Optional[str] = None
    artist: Optional[str] = None  # 关联的歌手 ID

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
    return {"access_token": access_token, "token_type": "bearer","admin":user.is_admin}

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
    query = select(Playlist).options(selectinload(Playlist.owner),selectinload(Playlist.songs)).limit(limit)
    if search:
        query = query.where(Playlist.name.contains(search))
    result = await session.execute(query)
    playlists = result.scalars().all()
    return [
        PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            owner=playlist.owner.username if playlist.owner else None,
            songs=[
                {
                    "id": song.id,
                    "title": song.title,
                    "genre":song.genre,
                    #"artist": song.artist.name,  # 假设 Song 模型有 `artist` 外键
                }
                for song in playlist.songs
            ] if playlist.songs else []
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
        select(Playlist).options(selectinload(Playlist.songs)).where(Playlist.owner_id == current_user.id)
    )
    playlists = result.scalars().all()
    return [
        PlaylistResponse(
            id=playlist.id, 
            name=playlist.name, 
            owner=current_user.username,
            songs=[
                {
                    "id": song.id,
                    "title": song.title,
                    "genre":song.genre,
                    #"artist": song.artist.name,  # 假设 Song 模型有 `artist` 外键
                }
                for song in playlist.songs
            ] if playlist.songs else []
            )
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
    return PlaylistResponse(id=new_playlist.id, name=new_playlist.name, owner=current_user.username,songs=[])


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
    if playlist.owner_id != current_user.id | current_user.is_admin == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    await session.delete(playlist)
    await session.commit()
    return {"success": True, "message": "Playlist deleted"}



@app.get("/admin/users", response_model=List[UserResponse])
async def get_users(
    query: str = "",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 验证是否为管理员
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限访问此资源"
        )
    # 查询用户名包含 query 的用户
    stmt = select(User).where(User.username.contains(query))
    result = await session.execute(stmt)
    users = result.scalars().all()
    return [UserResponse.from_orm(user) for user in users]


@app.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 验证是否为管理员
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限访问此资源"
        )
    # 查询并删除用户
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user.is_admin:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您不能删除Admin管理员账号！"
        )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    await session.delete(user)
    await session.commit()

@app.post("/admin/artists", response_model=dict)
async def add_artist(
    artist_request: ArtistRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 验证是否为管理员
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限添加歌手"
        )
    # 创建新歌手
    new_artist = Artist(name=artist_request.name, genre=artist_request.genre)
    session.add(new_artist)
    await session.commit()
    await session.refresh(new_artist)
    return {"id": new_artist.id, "name": new_artist.name, "genre": new_artist.genre}


# 更新歌手信息
@app.put("/admin/artists/{artist_id}", response_model=dict)
async def update_artist(
    artist_id: int,
    artist_request: ArtistRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 验证是否为管理员
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限更新歌手信息"
        )
    # 查找歌手
    result = await session.execute(select(Artist).where(Artist.id == artist_id))
    artist = result.scalar_one_or_none()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="歌手不存在")
    # 更新歌手信息
    artist.name = artist_request.name
    artist.genre = artist_request.genre
    await session.commit()
    await session.refresh(artist)
    return {"id": artist.id, "name": artist.name, "genre": artist.genre}


# 删除歌手
@app.delete("/admin/artists/{artist_id}")
async def delete_artist(
    artist_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 验证是否为管理员
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除歌手"
        )
    # 查找并删除歌手
    result = await session.execute(select(Artist).where(Artist.id == artist_id))
    artist = result.scalar_one_or_none()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="歌手不存在")
    await session.delete(artist)
    await session.commit()
    return {"success": True, "message": "歌手已删除"}


# 添加新歌曲
@app.post("/admin/songs", response_model=SongResponse)
async def add_song(
    song_request: SongRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 验证是否为管理员
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限添加歌曲"
        )

    # 检查关联的歌手是否存在
    artist = None
    if song_request.artist:
        result = await session.execute(select(Artist).where(Artist.name == song_request.artist))
        artist = result.scalar_one_or_none()
        if not artist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="歌手不存在")

    # 添加歌曲到数据库
    new_song = Song(title=song_request.title, genre=song_request.genre, artist_id=artist.id)
    session.add(new_song)
    await session.commit()
    await session.refresh(new_song)

    return SongResponse(id=new_song.id, title=new_song.title, genre=new_song.genre, artist=artist.name if artist else None)


# 更新歌曲信息
@app.put("/admin/songs/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: int,
    song_request: SongRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 验证是否为管理员
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限更新歌曲"
        )

    # 查找歌曲
    result = await session.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="歌曲不存在")
    
    # 检查关联的歌手是否存在
    artist = None
    if song_request.artist:
        result = await session.execute(select(Artist).where(Artist.name == song_request.artist))
        artist = result.scalar_one_or_none()
        if not artist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="歌手不存在")

    # 更新歌曲信息
    song.title = song_request.title
    song.genre = song_request.genre
    song.artist_id = artist.id

    await session.commit()
    await session.refresh(song)

    return SongResponse(
        id=song.id, title=song.title, genre=song.genre, artist=song.artist.name if song.artist else None
    )


# 删除歌曲
@app.delete("/admin/songs/{song_id}")
async def delete_song(
    song_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 验证是否为管理员
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限删除歌曲"
        )

    # 查找歌曲
    result = await session.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="歌曲不存在")

    # 删除歌曲
    await session.delete(song)
    await session.commit()
    return {"success": True, "message": "歌曲已删除"}


# 获取歌曲详情
@app.get("/api/songs/{song_id}", response_model=SongResponse)
async def get_song_details(
    song_id: int,
    session: AsyncSession = Depends(get_session),
):
    # 查找歌曲
    result = await session.execute(select(Song).where(Song.id == song_id).options(selectinload(Song.artist)))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="歌曲不存在")

    return SongResponse(
        id=song.id, title=song.title, genre=song.genre, artist=song.artist.name if song.artist else None
    )


# 添加歌曲到歌单
@app.post("/api/playlists/{playlist_id}/add_song")
async def add_song_to_playlist(
    playlist_id: int,
    song_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 查找歌单
    result = await session.execute(select(Playlist).options(selectinload(Playlist.songs)).where(Playlist.id == playlist_id))
    playlist = result.scalars().first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单未找到")

    # 确保是当前用户的歌单
    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")

    # 查找歌手
    artist_name = song_data.get("artist_name")
    result = await session.execute(select(Artist).where(Artist.name == artist_name))
    artist = result.scalars().first()
    if not artist:
        raise HTTPException(status_code=404, detail="歌手未找到")
    
    #查找歌曲
    result = await session.execute(select(Song).where(Song.artist_id == artist.id))
    song = result.unique().scalars().first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲未找到")

    # 添加歌曲
    playlist.songs.append(song)
    # await session.add(new_song)
    await session.commit()
    return {"message": "歌曲添加成功"}

# 从歌单中移除歌曲
@app.delete("/api/playlists/{playlist_id}/songs/{song_id}")
async def remove_song_from_playlist(
    playlist_id: int,
    song_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 查找歌单
    result = await session.execute(select(Playlist).options(selectinload(Playlist.songs)).where(Playlist.id == playlist_id))
    playlist = result.scalars().first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单未找到")

    # 确保是当前用户的歌单
    if playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")

    # 查找歌曲并移除
    result = await session.execute(select(Song).where(Song.id == song_id))
    song = result.scalars().first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲未找到")

    if song not in playlist.songs:
        raise HTTPException(status_code=400, detail="歌曲不在歌单中")

    playlist.songs.remove(song)
    await session.commit()
    return {"message": "歌曲已移除"}