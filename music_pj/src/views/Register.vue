<template>
    <div class="register-container">
      <div class="register">
        <h1>注册</h1>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label for="username">用户名:</label>
            <input type="text" id="username" v-model="username" required />
          </div>
          <div class="form-group">
            <label for="password">密码:</label>
            <input type="password" id="password" v-model="password" required />
          </div>
          <div class="form-group">
            <button type="submit">注册</button>
          </div>
          <div v-if="errorMessage" class="error-message">
            <p>{{ errorMessage }}</p>
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  // 导入注册的函数
  import { register } from '@/services/user_service';
  
  export default {
    data() {
      return {
        username: '',
        password: '',
        errorMessage: '' // 错误信息
      };
    },
    methods: {
      async submitForm() {
        try {
          const { success, message } = await register(this.username, this.password);
  
          if (success) {
            console.log('注册成功:', message);
            // 注册成功后跳转到登录页面
            this.$router.push({ name: 'Login' });
          } else {
            this.errorMessage = message;
          }
        } catch (error) {
          this.errorMessage = '注册请求失败，请稍后再试。';
          console.log('注册请求错误:', error);
        }
      }
    }
  };
  </script>
  
  <style scoped>
  /* 同登录界面样式 */
  .register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 50vh;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    padding: 0 20px;
  }
  
  .register {
    max-width: 400px;
    width: 100%;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.8);
  }
  
  h1 {
    text-align: center;
    font-size: 24px;
    margin-bottom: 20px;
  }
  
  form {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
  }
  
  label {
    margin-bottom: 5px;
    font-weight: bold;
  }
  
  input {
    padding: 10px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 4px;
    width: 100%;
    box-sizing: border-box;
  }
  
  input:focus {
    border-color: #eccf9d;
    outline: none;
  }
  
  button {
    padding: 10px;
    background-color: #eccf9d;
    color: black;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
    box-sizing: border-box;
  }
  
  button:hover {
    background-color: #f4e2c4;
  }
  
  button:focus {
    outline: none;
  }
  
  .error-message {
    color: red;
    font-size: 14px;
    margin-top: 10px;
  }
  </style>
  