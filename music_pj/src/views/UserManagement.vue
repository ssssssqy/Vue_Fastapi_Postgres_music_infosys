<template>
    <div>
      <h1>用户管理</h1>
      <form @submit.prevent="addUser">
        <input v-model="username" placeholder="用户名" required />
        <input v-model="password" type="password" placeholder="密码" required />
        <button type="submit">添加用户</button>
      </form>
      <h2>用户列表</h2>
      <ul>
        <li v-for="user in users" :key="user.id">{{ user.username }}</li>
      </ul>
    </div>
  </template>
  
  <script>
  import { createUser, getUsers } from '@/services/userService';
  
  export default {
    data() {
      return {
        username: '',
        password: '',
        users: [],
      };
    },
    methods: {
      async addUser() {
        await createUser(this.username, this.password);
        this.username = '';
        this.password = '';
        this.loadUsers();
      },
      async loadUsers() {
        this.users = await getUsers();
      },
    },
    mounted() {
      this.loadUsers();
    },
  };
  </script>
  