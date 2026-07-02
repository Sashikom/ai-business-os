import { useState, useEffect } from 'react';
import { adminAPI } from './api';

function App() {
  const [activeTab, setActiveTab] = useState('tokens');
  const [tokens, setTokens] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'tokens') {
        const data = await adminAPI.listTokens();
        setTokens(data.tokens || []);
      } else if (activeTab === 'users') {
        const data = await adminAPI.listUsers();
        setUsers(data.users || []);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('Ошибка загрузки');
    }
    setLoading(false);
  };

  const handleGenerateTokens = async () => {
    try {
      setLoading(true);
      await adminAPI.generateTokens(5, 30);
      setMessage('✅ Создано 5 токенов на 30 дней!');
      await loadData();
    } catch (error) {
      setMessage('❌ Ошибка создания токенов');
    }
    setLoading(false);
  };

  const handleBlockUser = async (telegramId: number) => {
    if (!confirm('Заблокировать пользователя?')) return;
    try {
      await adminAPI.blockUser(telegramId);
      setMessage('✅ Пользователь заблокирован');
      await loadData();
    } catch (error) {
      setMessage('❌ Ошибка блокировки');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="bg-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">🤖 AI Business OS - Админка</h1>
          <p className="text-gray-400 mt-2">Управление ботом и пользователями</p>
        </div>
      </div>

      {message && (
        <div className="max-w-7xl mx-auto px-4 mt-4">
          <div className="bg-blue-600 text-white px-4 py-3 rounded-lg">
            {message}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 mt-6">
        <div className="flex space-x-4 border-b border-gray-700">
          <button
            onClick={() => setActiveTab('tokens')}
            className={`px-6 py-3 font-semibold ${
              activeTab === 'tokens'
                ? 'text-blue-500 border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            🎫 Токены
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-6 py-3 font-semibold ${
              activeTab === 'users'
                ? 'text-blue-500 border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            👥 Пользователи
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {loading ? (
          <div className="text-center py-12"><div className="text-xl">Загрузка...</div></div>
        ) : activeTab === 'tokens' ? (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Токены доступа</h2>
              <button
                onClick={handleGenerateTokens}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold"
              >
                + Создать 5 токенов (30 дней)
              </button>
            </div>
            {tokens.length === 0 ? (
              <div className="bg-gray-800 rounded-lg p-8 text-center">
                <p className="text-gray-400">Нет токенов. Создайте первый!</p>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Токен</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Дней</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Статус</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Использован</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {tokens.map((token: any, idx: number) => (
                      <tr key={idx} className="hover:bg-gray-700">
                        <td className="px-6 py-4 font-mono text-sm">{token.token}</td>
                        <td className="px-6 py-4">{token.duration_days}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded text-xs ${token.is_used ? 'bg-red-600' : 'bg-green-600'}`}>
                            {token.is_used ? 'Использован' : 'Активен'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-400">{token.used_by_telegram_id || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ) : (
          <div>
            <h2 className="text-2xl font-bold mb-6">Пользователи</h2>
            {users.length === 0 ? (
              <div className="bg-gray-800 rounded-lg p-8 text-center">
                <p className="text-gray-400">Нет пользователей</p>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Telegram ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Имя</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Статус</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Действия</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {users.map((user: any, idx: number) => (
                      <tr key={idx} className="hover:bg-gray-700">
                        <td className="px-6 py-4 font-mono text-sm">{user.telegram_id}</td>
                        <td className="px-6 py-4">{user.full_name || user.username || '—'}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded text-xs ${user.has_access ? 'bg-green-600' : 'bg-red-600'}`}>
                            {user.has_access ? 'Активен' : 'Заблокирован'}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {user.has_access && user.telegram_id && (
                            <button
                              onClick={() => handleBlockUser(user.telegram_id)}
                              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm"
                            >
                              Заблокировать
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;