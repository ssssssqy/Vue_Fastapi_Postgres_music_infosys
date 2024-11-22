
import { createApp } from 'vue'
import Login from './views/Login.vue'  // 导入 Login.vue
import router from './router/router'; // 导入 router

// 创建 Vue 应用并挂载到 #app 元素
createApp(Login).use(router).mount('#login')
