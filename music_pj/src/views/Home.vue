<template>
    <div class="home-container">
        <div class="playlist-section">
        <h2>歌单</h2>
        <!-- 搜索所有用户创建的歌单 -->
        <input
            type="text"
            placeholder="搜索歌单..."
            v-model="playlistSearchQuery"
            @input="searchPlaylists"
        />
        <ul>
            <li v-for="playlist in filteredPlaylists" :key="playlist.id">
            <div>
              <strong>{{ playlist.name }}</strong> 
              <p>by {{ playlist.owner }}</p>
              <ul>
              <li v-for="song in playlist.songs" :key="song.id">
                <p>{{ song.title }}</p>
              </li>
              <li v-if="playlist.songs.length === 0">没有歌曲</li>
              </ul>
            </div>  
            </li>
        </ul>

        <!-- 展示当前用户的歌单 -->
        <h3>我的歌单</h3>
        <button @click="createPlaylist">创建歌单</button>
        <ul>
            <li v-for="playlist in userPlaylists" :key="playlist.id">
            <div>
              {{ playlist.name }}
            <p>            
            <button @click="deletePlaylist(playlist.id)">删除</button>
            <!-- 新增：添加歌曲按钮 -->
            <button @click="showAddSongForm(playlist.id)">添加歌曲</button></p>  
            <!-- 歌单内歌曲列表 -->
            
              <ul>
              <li v-for="song in playlist.songs" :key="song.id">
                <p>{{ song.title }}</p>
                <button @click="removeSongFromPlaylist(playlist.id, song.id)">
                删除歌曲
                </button>
              </li>
              <li v-if="playlist.songs.length === 0">没有歌曲</li>
            </ul>
            </div>
            </li>
        </ul>
        <!-- 添加歌曲表单 -->
      <div v-if="showForm">
        <h4>向歌单 {{ currentPlaylistName }} 添加歌曲</h4>
        <form @submit.prevent="submitAddSong">
          <label for="song-title">歌曲名:</label>
          <input
            id="song-title"
            type="text"
            v-model="newSong.title"
            placeholder="输入歌曲名称"
            required
          />
          <label for="artist-name">创作者:</label>
          <input
            id="artist-name"
            type="text"
            v-model="newSong.artist"
            placeholder="输入创作者名称"
            required
          />
          <button type="submit" @click="submitAddSong">提交</button>
          <button type="button" @click="cancelAddSong">取消</button>
        </form>
      </div>
      </div>


    <div class="artist-section">
    <h2>歌手</h2>
    <!-- 搜索框 -->
    <input 
        type="text" 
        placeholder="搜索歌手..." 
        v-model="artistSearchQuery" 
        @input="searchArtists" 
    />
    <!-- 搜索结果 -->
    <ul>
        <li v-for="artist in displayedArtists" :key="artist.id">
        <div>
            <strong>{{ artist.name }}</strong>
            <p v-if="artist.genre">流派: {{ artist.genre }}</p>
        </div>
        </li>
    </ul>
    </div>


      <!-- 右栏：歌曲 -->
      <!-- 歌曲栏 -->
    <div class="song-section">
      <h2>歌曲</h2>
      <input 
        type="text" 
        placeholder="搜索歌曲..." 
        v-model="songSearchQuery" 
        @input="fetchSongs" 
      />
      <ul>
        <li v-for="(song, index) in songs" :key="index">
          <strong>{{ song.title }}</strong> - {{ song.genre }}
          <span v-if="song.artist"> by {{ song.artist }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

  
  <script>
  import { fetchArtists } from "@/services/artist_service.js"; // 引入服务
  import { fetchSongs } from "@/services/song_service";
  import {
  getPlaylists,
  getUserPlaylists,
  createPlaylist,
  deletePlaylist,
  addSongToPlaylist, // 新增服务方法
  removeSongFromPlaylist,
} from "@/services/playlist_service";

  export default {
    data() {
      return {
        playlists: [],
        artists: [],
        songs: [],
        playlistSearchQuery: "",
        artistSearchQuery: "",
        songSearchQuery: "",
        playlistSearchQuery: "",
        userPlaylists: [],
        token: "", // 当前用户的 JWT token
        showForm: false, // 控制表单显示
        currentPlaylistId: null, // 当前操作的歌单 ID
        currentPlaylistName: "", // 当前操作的歌单名称
        newSong: {
          title: "",
          artist: "",
        },
      };
    },
    computed: {
      // 根据搜索框内容过滤展示的歌单
      filteredPlaylists() {
        return this.playlists.filter((playlist) =>
          playlist.name.includes(this.playlistSearchQuery)
        );
      },
      // 根据搜索框内容过滤展示的歌手
      displayedArtists() {
        if (!this.artistSearchQuery) {
          return this.artists; // 未搜索时显示所有歌手
        }
        return this.artists.filter((artist) =>
          artist.name.includes(this.artistSearchQuery)
        );
      },
      // 根据搜索框内容过滤展示的歌曲
      filteredSongs() {
        return this.songs.filter((song) =>
          song.title.includes(this.songSearchQuery)
        );
      },
    },
    methods: {

      // 搜索歌手
      async searchArtists() {
        try {
          this.artists = await fetchArtists(this.artistSearchQuery); // 使用服务方法
        } catch (error) {
          console.error("搜索歌手失败:", error);
        }
      },
      // 获取所有歌手
      async fetchArtists() {
        try {
          this.artists = await fetchArtists(); // 使用服务方法
        } catch (error) {
          console.error("加载歌手失败:", error);
        }
      },
      // 获取歌曲
      async fetchSongs() {
        try {
          const response = await fetchSongs(this.songSearchQuery);
          this.songs = response;
        } catch (error) {
          console.error("获取歌曲失败：", error);
        }
      },

      async searchPlaylists() {
        this.playlists = await getPlaylists(this.playlistSearchQuery);
      },

      async loadUserPlaylists() {
        const token = localStorage.getItem("access_token"); // 从 localStorage 获取 token
        this.userPlaylists = await getUserPlaylists(token);
      },

      async createPlaylist() {
        const name = prompt("请输入新歌单名称：");
        if (name) {
            const token = localStorage.getItem("access_token"); // 从 localStorage 获取 token
            console.log("Token:", token); // 打印 token 以便调试
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

      showAddSongForm(playlistId) {
      const playlist = this.userPlaylists.find((p) => p.id === playlistId);
      this.currentPlaylistId = playlistId;
      this.currentPlaylistName = playlist.name;
      this.showForm = true;
    },
      async submitAddSong() {
        try {
          const token = localStorage.getItem("access_token");
          await addSongToPlaylist(
            this.currentPlaylistId,
            this.newSong.title,
            this.newSong.artist,
            token
          );
          alert(`歌曲 "${this.newSong.title}" 添加成功！`);
          this.cancelAddSong();
        } catch (error) {
          console.error("添加歌曲失败：", error);
          alert("添加歌曲失败，请重试！");
        }
      },
      cancelAddSong() {
        this.showForm = false;
        this.newSong = { title: "", artist: "" };
      },

      async removeSongFromPlaylist(playlistId, songId) {
      try {
        const token = localStorage.getItem("access_token");
        await removeSongFromPlaylist(playlistId,songId,token);
        // this.playlist.songs = this.playlist.songs.filter((song) => song["id"] !== songId); // 更新前端数据
        await this.loadUserPlaylists();
        await this.searchPlaylists();
      } catch (error) {
        console.error("Failed to remove song:", error);
      }
    },

    },
    mounted() {
      // 页面加载时获取数据
      this.fetchArtists(); // 页面加载时获取所有歌手
      this.fetchSongs(); // 页面加载时获取前10首歌曲
      this.searchPlaylists();
      this.loadUserPlaylists();
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
  position: relative; /* 确保伪元素可以覆盖整个容器 */
  gap: 20px;
  overflow: hidden; /* 防止内容溢出 */
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
  opacity: 0.5; /* 调整透明度，值在0到1之间 */
  z-index: -1; /* 确保背景图片在其他内容的下面 */
}

  
  /* 栏目样式 */
  .playlist-section,
  .artist-section,
  .song-section {
    flex: 1;
    max-width: 30%;
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
    margin-right: 10px;
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
    .song-section {
      max-width: 100%;
      margin-bottom: 20px;
    }
  }
  </style>
  