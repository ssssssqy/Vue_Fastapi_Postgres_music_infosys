<template>
    
    <div class="login-container">
      <div class="login">
        <h1>登录</h1>
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
            <button type="submit">登录</button>
          </div>
          <div v-if="errorMessage" class="error-message">
            <p>{{ errorMessage }}</p>
          </div>
        </form>
        <div class="register-link">
          <p>还没有账户？ 
            <!-- 修改为按钮样式 -->
            <!-- <router-view v-slot="Register"></router-view> -->
            <router-link to="/register" class="register-button">注册</router-link>
          </p>
          <router-view :key="key"></router-view>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { login } from '@/services/user_service';
  
  export default {
    data() {
      return {
        username: '',
        password: '',
        errorMessage: ''
      };
    },
    methods: {
      async submitForm() {
        try {
          const { success, access_token, message, admin } = await login(this.username, this.password);
          console.log( success, access_token, message, admin );
          if (success) {
            console.log('登录成功:', message);
            localStorage.setItem('access_token', access_token);
            if(admin){
              this.$router.push('/homeadmin');
            }
            else{
              this.$router.push('/home');
            }
          } else {
            this.errorMessage = message;
            console.log('登录失败:', message);
          }
        } catch (error) {
          this.errorMessage = '登录请求失败，请稍后再试。';
          console.log('登录请求错误:', error);
        }
      },

    },

  };

  </script>
  
  <style scoped>
  /* 整个页面的背景和居中容器 */
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-image: url('./img/login_bg.png'); 
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    padding: 0 20px;
  }
  
  /* 登录表单容器 */
  .login {
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
  
  /* 错误信息的样式 */
  .error-message {
    color: red;
    font-size: 14px;
    margin-top: 10px;
  }
  
  /* 注册按钮的样式 */
  .register-link {
    text-align: center;
    margin-top: 20px;
  }
  
  .register-button {
    font-size: 16px;
    color: #eccf9d;
    text-decoration: none;
    padding: 8px 16px;
    background-color: #f1f1f1;
    border-radius: 4px;
    border: 1px solid #eccf9d;
    transition: background-color 0.3s, color 0.3s;
  }
  
  .register-button:hover {
    background-color: #f4e2c4;
    color: white;
  }
  
  .register-button:focus {
    outline: none;
  }
  
  @media (max-width: 480px) {
    .login {
      padding: 15px;
    }
  
    h1 {
      font-size: 20px;
    }
  
    input, button {
      font-size: 16px;
    }
  }
  </style>
  