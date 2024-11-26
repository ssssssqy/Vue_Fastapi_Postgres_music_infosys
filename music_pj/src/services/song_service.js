import axios from "axios";

const API_BASE_URL = "http://localhost:8000"; // 替换为你的后端地址

export async function fetchSongs(search = "") {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/songs`, {
      params: { search },
    });
    return response.data;
  } catch (error) {
    console.error("歌曲数据获取失败：", error);
    throw error;
  }
}

export async function createSong(songData) {
  const token = localStorage.getItem("access_token");
  const response = await axios.post(`${API_BASE_URL}/admin/songs`, songData,{ headers: { Authorization: `Bearer ${token}` } });
  return response.data;
}

export async function updateSong(songData) {
  const { id, ...rest } = songData;
  const token = localStorage.getItem("access_token");
  const response = await axios.put(`${API_BASE_URL}/admin/songs/${id}`, rest,{ headers: { Authorization: `Bearer ${token}` } });
  return response.data;
}

export async function deleteSong(songId) {
  const token = localStorage.getItem("access_token");
  const response = await axios.delete(`${API_BASE_URL}/admin/songs/${songId}`,{ headers: { Authorization: `Bearer ${token}` } });
  return response.data;
}

