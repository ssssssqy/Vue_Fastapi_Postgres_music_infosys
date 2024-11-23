import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // 后端 API 地址

/**
 * 获取所有歌手或按名称搜索歌手
 * @param {string} searchQuery 搜索关键词（可选）
 * @returns {Promise<Array>} 歌手列表
 */
export async function fetchArtists(searchQuery = "") {
  const url = searchQuery ? `${API_BASE_URL}/api/artists?search=${encodeURIComponent(searchQuery)}` : `${API_BASE_URL}/api/artists`;
  
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

// export async function fetchArtists(query = "") {
//   const response = await axios.get(`${API_URL}/artists`, {
//     params: { query },
//   });
//   return response.data;
// }

export async function createArtist(artist) {
  const token = localStorage.getItem("access_token");
  return axios.post(
    `${API_BASE_URL}/admin/artists`,
    artist,
    { headers: { Authorization: `Bearer ${token}` } }
  );
}

export async function updateArtist(artist) {
  const token = localStorage.getItem("access_token");
  return axios.put(
    `${API_BASE_URL}/admin/artists/${artist.id}`,
    artist,
    { headers: { Authorization: `Bearer ${token}` } }
  );
}

export async function deleteArtist(artistId) {
  const token = localStorage.getItem("access_token");
  return axios.delete(`${API_BASE_URL}/admin/artists/${artistId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}