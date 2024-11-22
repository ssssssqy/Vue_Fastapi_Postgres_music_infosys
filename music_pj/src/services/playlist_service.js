import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // 后端 API 地址

export const createPlaylist = async (name, userId) => {
    const response = await axios.post(`${API_BASE_URL}/playlists/`, { name, user_id: userId });
    return response.data;
};

export const deletePlaylist = async (playlistId, userId) => {
    const response = await axios.delete(`${API_BASE_URL}/playlists/${playlistId}/`, { data: { user_id: userId } });
    return response.data;
};
