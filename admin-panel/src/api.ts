import axios from 'axios';

   const API_BASE_URL = ' https://d4034e6dda5ef9.lhr.life';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const adminAPI = {
  generateTokens: async (count = 1, durationDays = 30) => {
    const response = await api.post('/admin/generate-tokens', {
      count,
      duration_days: durationDays,
    }, {
      params: { telegram_id: 5236809587 }
    });
    return response.data;
  },

  listTokens: async () => {
    const response = await api.get('/admin/tokens', {
      params: { telegram_id: 5236809587 }
    });
    return response.data;
  },

  listUsers: async () => {
    const response = await api.get('/admin/users', {
      params: { telegram_id: 5236809587 }
    });
    return response.data;
  },

  blockUser: async (blockTelegramId: number) => {
    const response = await api.post('/admin/block-user', {
      block_telegram_id: blockTelegramId,
    }, {
      params: { telegram_id: 5236809587 }
    });
    return response.data;
  },
};

export default api;