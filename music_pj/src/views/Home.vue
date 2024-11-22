<template>
    <div class="home-container">
      <!-- 左栏：歌单 -->
      <div class="playlist-section">
        <h2>歌单</h2>
        <input 
          type="text" 
          placeholder="搜索歌单..." 
          v-model="playlistSearchQuery" 
          @input="searchPlaylists" 
        />
        <button @click="createPlaylist">创建歌单</button>
        <ul>
          <li v-for="(playlist, index) in filteredPlaylists" :key="index">
            {{ playlist.name }}
            <button @click="deletePlaylist(index)">删除</button>
          </li>
        </ul>
      </div>
  
      <!-- 中栏：歌手
      <div class="artist-section">
        <h2>歌手</h2>
        <input 
          type="text" 
          placeholder="搜索歌手..." 
          v-model="artistSearchQuery" 
          @input="searchArtists" 
        />
        <ul>
          <li v-for="(artist, index) in filteredArtists" :key="index">
            {{ artist.name }}
            <button @click="viewArtist(index)">查看</button>
          </li>
        </ul>
      </div>
   -->

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
      <div class="song-section">
        <h2>歌曲</h2>
        <input 
          type="text" 
          placeholder="搜索歌曲..." 
          v-model="songSearchQuery" 
          @input="searchSongs" 
        />
        <button @click="uploadSong">上传歌曲</button>
        <ul>
          <li v-for="(song, index) in filteredSongs" :key="index">
            {{ song.title }}
            <button @click="deleteSong(index)">删除</button>
          </li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  import { fetchArtists } from "@/services/artist_service.js"; // 引入服务

  export default {
    data() {
      return {
        playlists: [{ name: "我的歌单1" }, { name: "流行音乐" }],
        artists: [],
        songs: [{ title: "青花瓷" }, { title: "泡沫" }],
        playlistSearchQuery: "",
        artistSearchQuery: "",
        songSearchQuery: "",
      };
    },
    computed: {
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
      filteredSongs() {
        return this.songs.filter((song) =>
          song.title.includes(this.songSearchQuery)
        );
      },
    },
    methods: {
        
      createPlaylist() {
        const name = prompt("请输入新歌单名称：");
        if (name) {
          this.playlists.push({ name });
        }
      },
      deletePlaylist(index) {
        this.playlists.splice(index, 1);
      },
      searchPlaylists() {
        console.log("搜索歌单：", this.playlistSearchQuery);
      },
},
methods: {
      async searchArtists() {
        try {
            this.artists = await fetchArtists(this.artistSearchQuery); // 使用服务方法
        } catch (error) {
            console.error("搜索歌手失败:", error);
        }
      },
      
      async fetchArtists() {
        try {
            this.artists = await fetchArtists(); // 使用服务方法
        } catch (error) {
            console.error("加载歌手失败:", error);
        }
      },

      mounted() {
        this.fetchArtists(); // 页面加载时获取所有歌手
      },
      viewArtist(index) {
        alert(`查看歌手详情：${this.artists[index].name}`);
      },
      searchSongs() {
        console.log("搜索歌曲：", this.songSearchQuery);
      },
      uploadSong() {
        const title = prompt("请输入歌曲名称：");
        if (title) {
          this.songs.push({ title });
        }
      },
      deleteSong(index) {
        this.songs.splice(index, 1);
      },
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
  