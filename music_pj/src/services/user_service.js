import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // 后端 API 地址

// 登录请求函数
export const login = async (username, password) => {
  try {
    // 发送 POST 请求到 /login/ 端点，传递用户名和密码
    const response = await axios.post(`${API_BASE_URL}/login/`, { username, password });
    
    // 检查后端响应结构，返回 success 和 token
    if (response.data.access_token) {
      return {
        success: true,
        access_token: response.data.access_token,  // 返回 token
        message: '登录成功'  // 登录成功信息
      };
    } else {
      return {
        success: false,
        message: response.data.detail || '登录失败，请检查用户名和密码'
      };
    }
  } catch (error) {
    console.error('登录请求错误:', error);
    return {
      success: false,
      message: '登录请求失败，请稍后再试。'  // 网络请求失败时的提示
    };
  }
};


// 注册请求函数
export const register = async (username, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/register/`, { username, password });
      return { success: true, message: '注册请求成功！' };;
    } catch (error) {
      console.error('注册请求失败:', error);
      return { success: false, message: '注册请求失败，请稍后再试。' };
    }
  };