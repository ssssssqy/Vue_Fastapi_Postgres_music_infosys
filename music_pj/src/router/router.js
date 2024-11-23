import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import HomeAdmin from '@/views/Home_admin.vue'
import Login from '@/views/Login.vue'; // 导入登录页面
import Register from '@/views/Register.vue'; // 导入注册页面

const routes = [
  { path: '/', name: 'Login', component: Login }, // 添加登录路由
  { path: '/home', name: 'Home', component: Home },
  { path: '/homeadmin', name: 'HomeAdmin', component: HomeAdmin },
  { path: '/register', name: 'Register', component: Register }, // 添加注册路由
  
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
