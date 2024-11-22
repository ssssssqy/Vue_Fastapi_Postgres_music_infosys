from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# 用户表
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    
    playlists = relationship("Playlist", back_populates="owner")

# 歌手表
class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    genre = Column(String)

    songs = relationship("Song", back_populates="artist")

# 歌曲表
class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    genre = Column(String)
    artist_id = Column(Integer, ForeignKey("artists.id"))

    artist = relationship("Artist", back_populates="songs")
    playlists = relationship("Playlist", secondary="playlist_songs", back_populates="songs")

# 歌单表
class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="playlists")
    songs = relationship("Song", secondary="playlist_songs", back_populates="playlists")

# 歌单与歌曲的多对多关系表
playlist_songs = Table(
    "playlist_songs", Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlists.id"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.id"), primary_key=True)
)
