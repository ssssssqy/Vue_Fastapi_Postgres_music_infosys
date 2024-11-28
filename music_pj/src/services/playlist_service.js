import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export async function getPlaylists(searchQuery) {
  const params = searchQuery ? { search: searchQuery } : {};
  const response = await axios.get(`${API_BASE_URL}/api/playlists`, { params });
  return response.data; // 返回所有歌单数据
}

export async function getUserPlaylists(token) {
  const response = await axios.get(`${API_BASE_URL}/api/playlists/my`,      {
    headers: {
      Authorization: `Bearer ${token}`, // 验证头
      "Content-Type": "application/json", // 确保 Content-Type 正确
    },
  });
  return response.data; // 返回当前用户的歌单
}

export async function createPlaylist(name, token) {
  try {
    console.log("Sending data:",  name ); // 确认发送数据
    const response = await axios.post(
      `${API_BASE_URL}/api/playlists`,
       name , // 确保请求体格式是 { name: "aaaa" }
      {
        headers: {
          Authorization: `Bearer ${token}`, // 验证头
          "Content-Type": "application/json", // 确保 Content-Type 正确
        },
      }
    );
    console.log("Response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error response:", error.response?.data);
    throw error;
  }
}


export async function deletePlaylist(playlistId, token) {
  await axios.delete(`${API_BASE_URL}/api/playlists/${playlistId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}


// 新增：添加歌曲到歌单
export async function addSongToPlaylist(playlistId, songTitle, artistName, token) {
  const url = `${API_BASE_URL}/api/playlists/${playlistId}/add_song`;
  const response = await axios.post(
    url,
    {
      title: songTitle,
      artist_name: artistName,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
}

export async function removeSongFromPlaylist(playlistId, songId, token) {
  try {
    await axios.delete(
      `${API_BASE_URL}/api/playlists/${playlistId}/songs/${songId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
  } catch (error) {
    console.error("删除歌曲失败:", error);
  }
}
