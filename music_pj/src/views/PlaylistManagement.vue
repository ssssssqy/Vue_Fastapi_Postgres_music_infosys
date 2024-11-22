<template>
    <div>
      <h1>歌单管理</h1>
      <form @submit.prevent="createNewPlaylist">
        <input v-model="playlistName" placeholder="歌单名称" required />
        <button type="submit">创建歌单</button>
      </form>
      <ul>
        <li v-for="playlist in playlists" :key="playlist.id">
          {{ playlist.name }}
          <button @click="deletePlaylist(playlist.id)">删除</button>
        </li>
      </ul>
    </div>
</template>
  
<script>
  import { createPlaylist, deletePlaylist } from '@/services/playlistService';
  
  export default {
    data() {
      return {
        playlistName: '',
        playlists: [], // 假设后端有一个获取歌单的接口
      };
    },
    methods: {
      async createNewPlaylist() {
        await createPlaylist(this.playlistName, 1); // 假设用户 ID 为 1
        this.playlistName = '';
        this.loadPlaylists();
      },
      async deletePlaylist(id) {
        await deletePlaylist(id, 1); // 假设用户 ID 为 1
        this.loadPlaylists();
      },
      async loadPlaylists() {
        // 假设您有获取歌单的接口
        this.playlists = []; // 更新为实际 API 调用
      },
    },
    mounted() {
      this.loadPlaylists();
    },
  };
  </script>
  