import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
// import UserManagement from '@/views/UserManagement.vue';
// import SongManagement from '@/views/SongManagement.vue';
// import ArtistManagement from '@/views/ArtistManagement.vue';
// import PlaylistManagement from '@/views/PlaylistManagement.vue';
import Login from '@/views/Login.vue'; // 导入登录页面
import Register from '@/views/Register.vue'; // 导入注册页面

const routes = [
  { path: '/', name: 'Login', component: Login }, // 添加登录路由
  { path: '/home', name: 'Home', component: Home },
  { path: '/register', name: 'Register', component: Register }, // 添加注册路由
//   { path: '/users', name: 'UserManagement', component: UserManagement },
//   { path: '/songs', name: 'SongManagement', component: SongManagement },
//   { path: '/artists', name: 'ArtistManagement', component: ArtistManagement },
//   { path: '/playlists', name: 'PlaylistManagement', component: PlaylistManagement },
  
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
