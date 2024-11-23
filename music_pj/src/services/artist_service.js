import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/artists'; // 后端 API 地址

/**
 * 获取所有歌手或按名称搜索歌手
 * @param {string} searchQuery 搜索关键词（可选）
 * @returns {Promise<Array>} 歌手列表
 */
export async function fetchArtists(searchQuery = "") {
  const url = searchQuery ? `${API_BASE_URL}?search=${encodeURIComponent(searchQuery)}` : API_BASE_URL;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`请求失败: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("获取歌手数据失败:", error);
    throw error;
  }
}
