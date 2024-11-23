import axios from "axios";

const BASE_URL = "http://localhost:8000/api"; // 替换为你的后端地址

export async function fetchSongs(search = "") {
  try {
    const response = await axios.get(`${BASE_URL}/songs`, {
      params: { search },
    });
    return response.data;
  } catch (error) {
    console.error("歌曲数据获取失败：", error);
    throw error;
  }
}
