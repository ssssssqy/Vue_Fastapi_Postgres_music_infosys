<template>
  <div class="home-container">
    <!-- 歌单栏 -->
    <div class="playlist-section">
      <h2>guanli歌单</h2>
      <input
        type="text"
        placeholder="搜索歌单..."
        v-model="playlistSearchQuery"
        @input="searchPlaylists"
      />
      <ul>
        <li v-for="playlist in filteredPlaylists" :key="playlist.id">
          <strong>{{ playlist.name }}</strong> by {{ playlist.owner }}
          <button @click="deletePlaylist(playlist.id)">删除</button>
        </li>
      </ul>

      <h3>我的歌单</h3>
      <button @click="createPlaylist">创建歌单</button>
      <ul>
        <li v-for="playlist in userPlaylists" :key="playlist.id">
          {{ playlist.name }}
          <button @click="deletePlaylist(playlist.id)">删除</button>
        </li>
      </ul>
    </div>

    <!-- 歌手栏 -->
    <div class="artist-section">
      <h2>歌手</h2>
      <input
        type="text"
        placeholder="搜索歌手..."
        v-model="artistSearchQuery"
        @input="searchArtists"
      />
      <button @click="showCreateArtistForm = true">新增歌手</button>
      <ul>
        <li v-for="artist in displayedArtists" :key="artist.id">
          <div>
            <strong>{{ artist.name }}</strong>
            <p v-if="artist.genre">流派: {{ artist.genre }}</p>
            <button @click="editArtist(artist)">修改</button>
            <button @click="deleteArtist(artist.id)">删除</button>
          </div>
        </li>
      </ul>
      


    <!-- 新增歌手表单 -->
    <div v-if="showCreateArtistForm" class="artist-form">
      <h3>新增歌手</h3>
      <label>名称:</label>
      <input type="text" v-model="newArtist.name" />
      <label>流派:</label>
      <input type="text" v-model="newArtist.genre" />
      <button @click="createArtist">保存</button>
      <button @click="showCreateArtistForm = false">取消</button>
    </div>

    <!-- 修改歌手表单 -->
    <div v-if="editArtistForm.show" class="artist-form">
      <h3>修改歌手信息</h3>
      <label>名称:</label>
      <input type="text" v-model="editArtistForm.data.name" />
      <label>流派:</label>
      <input type="text" v-model="editArtistForm.data.genre" />
      <button @click="updateArtist">保存</button>
      <button @click="editArtistForm.show = false">取消</button>
    </div>
  </div>


    <!-- 歌曲栏 -->
    <div class="song-section">
      <h2>歌曲</h2>
      <input 
        type="text" 
        placeholder="搜索歌曲..." 
        v-model="songSearchQuery" 
        @input="fetchSongs" 
      />
      <button v-if="isAdmin" @click="showCreateSongForm = true">新增歌曲</button>
      <ul>
        <li v-for="(song, index) in songs" :key="index">
          <div>

            <strong>{{ song.title }}</strong> 
            <p v-if="song.genre">流派: {{ song.genre }}</p>
            <p v-if="song.artist"> by {{ song.artist }}</p>
            <div v-if="isAdmin">
              <button @click="editSong(song)">修改</button>
              <button @click="deleteSong(song.id)">删除</button>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- 新增歌曲表单 -->
    <div v-if="showCreateSongForm" class="form-container">
      <h3>新增歌曲</h3>
      <label>标题:</label>
      <input type="text" v-model="newSong.title" />
      <label>流派:</label>
      <input type="text" v-model="newSong.genre" />
      <label>歌手:</label>
      <input type="text" v-model="newSong.artist" />
      <button @click="createSong">保存</button>
      <button @click="showCreateSongForm = false">取消</button>
    </div>

    <!-- 修改歌曲表单 -->
    <div v-if="editSongForm.show" class="form-container">
      <h3>修改歌曲信息</h3>
      <label>标题:</label>
      <input type="text" v-model="editSongForm.data.title" />
      <label>流派:</label>
      <input type="text" v-model="editSongForm.data.genre" />
      <label>歌手:</label>
      <input type="text" v-model="editSongForm.data.artist" />
      <button @click="updateSong">保存</button>
      <button @click="editSongForm.show = false">取消</button>
    </div>

    <!-- 用户管理栏 -->
    <div v-if="isAdmin" class="user-management-section">
      <h2>用户管理</h2>
      <input
        type="text"
        placeholder="搜索用户..."
        v-model="userSearchQuery"
        @input="searchUsers"
      />
      <ul>
        <li v-for="user in displayedUsers" :key="user.id">
          <strong>{{ user.username }}</strong>
          <button v-show="user.id !== 1" @click="deleteUser(user.id)">删除</button>
        </li>
      </ul>
    </div>
    </div>
</template>

<script>
import { fetchArtists, createArtist, deleteArtist, updateArtist } from "@/services/artist_service.js";
import { fetchSongs, createSong, updateSong, deleteSong } from "@/services/song_service";
import { getPlaylists, getUserPlaylists, createPlaylist, deletePlaylist } from "@/services/playlist_service";
import { fetchUsers, deleteUser } from "@/services/user_service"; // 引入用户管理服务

export default {
  data() {
    return {
      playlists: [],
      artists: [],
      songs: [],
      users: [], // 用户列表
      playlistSearchQuery: "",
      artistSearchQuery: "",
      songSearchQuery: "",
      userSearchQuery: "", // 用户搜索查询
      userPlaylists: [],
      token: localStorage.getItem("access_token"),
      isAdmin: false, // 是否为管理员
      showCreateArtistForm: false,
      newArtist: { name: "", genre: "" },
      editArtistForm: {
        show: false,
        data: { id: null, name: "", genre: "" },
      },
      newSong: { title: "", genre: "", artist: "" },
      showCreateSongForm: false,
      editSongForm: {
        show: false,
        data: { id: null, title: "", genre: "", artist: "" },
      },
    };
  },
  computed: {
    filteredPlaylists() {
      return this.playlists.filter((playlist) =>
        playlist.name.includes(this.playlistSearchQuery)
      );
    },
    displayedArtists() {
      if (!this.artistSearchQuery) {
        return this.artists;
      }
      return this.artists.filter((artist) =>
        artist.name.includes(this.artistSearchQuery)
      );
    },
    filteredSongs() {
      return this.songs.filter((song) =>
        song.title.includes(this.songSearchQuery)
      );
    },
    displayedUsers() {
      if (!this.userSearchQuery) {
        return [];
      }
      return this.users.filter((user) =>
        user.username.includes(this.userSearchQuery)
      );
    },
  },
  methods: {
    async searchArtists() {
      try {
        this.artists = await fetchArtists(this.artistSearchQuery);
      } catch (error) {
        console.error("搜索歌手失败:", error);
      }
    },
    async fetchArtists() {
      try {
        this.artists = await fetchArtists();
      } catch (error) {
        console.error("加载歌手失败:", error);
      }
    },
    async createArtist() {
      try {
        await createArtist(this.newArtist);
        this.showCreateArtistForm = false;
        this.searchArtists();
      } catch (error) {
        console.error("新增歌手失败:", error);
      }
    },
    async editArtist(artist) {
      this.editArtistForm.show = true;
      this.editArtistForm.data = { ...artist };
    },
    async updateArtist() {
      try {
        await updateArtist(this.editArtistForm.data);
        this.editArtistForm.show = false;
        this.searchArtists();
      } catch (error) {
        console.error("修改歌手信息失败:", error);
      }
    },
    async deleteArtist(artistId) {
      try {
        await deleteArtist(artistId);
        this.searchArtists();
      } catch (error) {
        console.error("删除歌手失败:", error);
      }
    },
    async fetchSongs() {
      try {
        this.songs = await fetchSongs(this.songSearchQuery);
      } catch (error) {
        console.error("获取歌曲失败：", error);
      }
    },
    async createSong() {
      try {
        await createSong(this.newSong);
        this.showCreateSongForm = false;
        this.fetchSongs();
      } catch (error) {
        console.error("新增歌曲失败：", error);
      }
    },
    async editSong(song) {
      this.editSongForm.show = true;
      this.editSongForm.data = { ...song };
    },
    async updateSong() {
      try {
        await updateSong(this.editSongForm.data);
        this.editSongForm.show = false;
        this.fetchSongs();
      } catch (error) {
        console.error("修改歌曲失败：", error);
      }
    },
    async deleteSong(songId) {
      try {
        await deleteSong(songId);
        this.fetchSongs();
      } catch (error) {
        console.error("删除歌曲失败：", error);
      }
    },
    async searchPlaylists() {
      this.playlists = await getPlaylists(this.playlistSearchQuery);
    },
    async loadUserPlaylists() {
      const token = localStorage.getItem("access_token");
      this.userPlaylists = await getUserPlaylists(token);
    },
    async createPlaylist() {
      const name = prompt("请输入新歌单名称：");
      if (name) {
        const token = localStorage.getItem("access_token");
        if (token) {
          await createPlaylist(name, token);
          await this.loadUserPlaylists();
          await this.searchPlaylists();
        } else {
          console.error("No token found!");
        }
      }
    },
    async deletePlaylist(playlistId) {
      const token = localStorage.getItem("access_token");
      await deletePlaylist(playlistId, token);
      await this.loadUserPlaylists();
      await this.searchPlaylists();
    },
    async searchUsers() {
      try {
        this.users = await fetchUsers(this.userSearchQuery, this.token);
      } catch (error) {
        console.error("搜索用户失败:", error);
      }
    },
    async deleteUser(userId) {
      try {
        if (this.isAdmin) {
          await deleteUser(userId, this.token);
          await this.searchUsers(); // 刷新用户列表
        } else {
          console.error("权限不足");
        }
      } catch (error) {
        console.error("删除用户失败:", error);
      }
    },
    async checkAdminStatus() {
      // 校验是否为管理员
      try {
        const response = await fetchUsers("", this.token); // 测试访问权限
        if (response) {
          this.isAdmin = true;
        }
      } catch (error) {
        this.isAdmin = false;
        console.error("用户权限校验失败:", error);
      }
    },
  },
  mounted() {
    this.fetchArtists();
    this.searchArtists();
    this.fetchSongs();
    this.searchPlaylists();
    this.loadUserPlaylists();
    this.checkAdminStatus(); // 检查是否为管理员
  },
};
</script>

<style scoped>
/* 页面背景及居中布局 */
.home-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  min-height: 100vh;
  position: relative;
  gap: 20px;
  overflow: hidden;
}

.home-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('./img/login_bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0.5;
  z-index: -1;
}

/* 栏目样式 */
.playlist-section,
.artist-section,
.song-section,
.user-management-section {
  flex: 1;
  max-width: 22%;
  padding: 20px;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.8);
}

h2 {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
  color: #d95d18;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eccf9d;
}

input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #eccf9d;
}

button {
  padding: 6px 12px;
  font-size: 14px;
  background-color: #eccf9d;
  color: black;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px; /* 为每个按钮添加右边距 */
}

button:hover {
  background-color: #f4e2c4;
}

@media (max-width: 768px) {
  .home-container {
    flex-direction: column;
    align-items: stretch;
  }
  .playlist-section,
  .artist-section,
  .song-section,
  .user-management-section {
    max-width: 100%;
    margin-bottom: 20px;
  }
}
</style>
