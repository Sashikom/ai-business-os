import { useState, useEffect } from 'react'

const API_URL = 'http://185.161.69.108:8005/api/v1/admin'

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [tokens, setTokens] = useState([])
  const [payments, setPayments] = useState([])
  const [plans, setPlans] = useState([])
  const [showTokenModal, setShowTokenModal] = useState(false)
  const [newToken, setNewToken] = useState(null)
  const [tokenForm, setTokenForm] = useState({ subscription: 'BASIC', days_valid: 30, username: '' })

  useEffect(() => {
    fetch(`${API_URL}/stats`).then(res => res.json()).then(setStats).catch(console.error)
    fetch(`${API_URL}/users`).then(res => res.json()).then(setUsers).catch(console.error)
    fetch(`${API_URL}/tokens`).then(res => res.json()).then(setTokens).catch(console.error)
    fetch(`${API_URL}/payments`).then(res => res.json()).then(setPayments).catch(console.error)
    fetch(`${API_URL}/plans`).then(res => res.json()).then(setPlans).catch(console.error)
  }, [])

  const generateToken = async () => {
    const res = await fetch(`${API_URL}/tokens/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tokenForm),
    })
    const data = await res.json()
    setNewToken(data)
    const updatedTokens = await fetch(`${API_URL}/tokens`).then(res => res.json())
    setTokens(updatedTokens)
  }

  const copyToken = (token) => {
    navigator.clipboard.writeText(token)
    alert('Токен скопирован!')
  }

  const menu = [
    { id: 'dashboard', label: 'Дашборд', icon: '' },
    { id: 'users', label: 'Пользователи', icon: '' },
    { id: 'tokens', label: 'Токены доступа', icon: '🔑' },
    { id: 'payments', label: 'Оплата', icon: '💳' },
    { id: 'settings', label: 'Настройки', icon: '⚙️' },
  ]

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f8fafc', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      {/* Sidebar */}
      <div style={{ width: '256px', backgroundColor: '#1e293b', color: 'white', padding: '24px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <span style={{ fontSize: '28px' }}>⚡</span>
            AI Business OS
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '14px', marginTop: '4px' }}>Панель управления</p>
        </div>

        <nav style={{ flex: 1 }}>
          {menu.map(item => (
            <button
              key={item.id}
              onClick={() => setPage(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                width: '100%',
                padding: '12px 16px',
                marginBottom: '8px',
                backgroundColor: page === item.id ? '#3b82f6' : 'transparent',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                textAlign: 'left',
                transition: 'all 0.2s'
              }}
            >
              <span style={{ fontSize: '20px' }}>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <button style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', backgroundColor: 'transparent', color: '#94a3b8', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' }}>
          <span></span>
          <span>Выйти</span>
        </button>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, padding: '32px', overflow: 'auto' }}>
        {/* Dashboard */}
        {page === 'dashboard' && stats && (
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#0f172a' }}>Дашборд</h1>
            <p style={{ color: '#64748b', marginBottom: '32px' }}>Обзор активности платформы</p>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', marginBottom: '32px' }}>
              {[
                { label: 'Всего пользователей', value: stats.total_users, icon: '', color: '#3b82f6' },
                { label: 'Активных токенов', value: stats.active_tokens, icon: '', color: '#a855f7' },
                { label: 'AI запросов', value: stats.total_requests, icon: '', color: '#10b981' },
                { label: 'Доход', value: `₽${stats.total_revenue}`, icon: '💰', color: '#f97316' },
                { label: 'Активных пользователей', value: stats.active_users, icon: '', color: '#14b8a6' },
                { label: 'Рост за месяц', value: `${stats.monthly_growth}%`, icon: '📊', color: '#ec4899' },
              ].map((card, i) => (
                <div key={i} style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <p style={{ color: '#64748b', fontSize: '14px', margin: 0 }}>{card.label}</p>
                      <h3 style={{ fontSize: '32px', fontWeight: 'bold', margin: '8px 0 0 0', color: '#0f172a' }}>{card.value}</h3>
                    </div>
                    <div style={{ backgroundColor: card.color, padding: '12px', borderRadius: '8px', fontSize: '24px' }}>
                      {card.icon}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Users */}
        {page === 'users' && (
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '32px', color: '#0f172a' }}>Пользователи</h1>
            <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Пользователь</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Тариф</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Статус</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Запросы</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '16px' }}>
                        <div style={{ fontWeight: '500', color: '#0f172a' }}>{user.username}</div>
                        <div style={{ fontSize: '14px', color: '#64748b' }}>{user.email}</div>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span style={{ padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: '500', backgroundColor: user.subscription === 'PRO' ? '#f3e8ff' : '#dbeafe', color: user.subscription === 'PRO' ? '#9333ea' : '#2563eb' }}>
                          {user.subscription}
                        </span>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span style={{ padding: '4px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: '500', backgroundColor: user.status === 'active' ? '#dcfce7' : '#fee2e2', color: user.status === 'active' ? '#16a34a' : '#dc2626' }}>
                          {user.status === 'active' ? 'Активен' : 'Заблокирован'}
                        </span>
                      </td>
                      <td style={{ padding: '16px', color: '#64748b' }}>{user.requests_used} / {user.requests_limit}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tokens */}
        {page === 'tokens' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
              <div>
                <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#0f172a' }}>Токены доступа</h1>
                <p style={{ color: '#64748b' }}>Генерация и управление токенами</p>
              </div>
              <button onClick={() => setShowTokenModal(true)} style={{ backgroundColor: '#3b82f6', color: 'white', padding: '12px 24px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '16px', fontWeight: '500' }}>
                + Сгенерировать токен
              </button>
            </div>

            <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Токен</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Клиент</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Тариф</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {tokens.map(token => (
                    <tr key={token.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '16px' }}>
                        <code style={{ backgroundColor: '#f1f5f9', padding: '4px 8px', borderRadius: '4px', fontFamily: 'monospace', fontSize: '14px' }}>{token.token}</code>
                      </td>
                      <td style={{ padding: '16px', color: '#64748b' }}>{token.username}</td>
                      <td style={{ padding: '16px' }}>
                        <span style={{ padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: '500', backgroundColor: '#dbeafe', color: '#2563eb' }}>
                          {token.subscription}
                        </span>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span style={{ padding: '4px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: '500', backgroundColor: '#dcfce7', color: '#16a34a' }}>
                          {token.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Modal */}
            {showTokenModal && (
              <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                <div style={{ backgroundColor: 'white', padding: '32px', borderRadius: '12px', width: '400px', maxWidth: '90%' }}>
                  {newToken ? (
                    <div>
                      <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>✅ Токен создан!</h2>
                      <code style={{ display: 'block', backgroundColor: '#f1f5f9', padding: '16px', borderRadius: '8px', fontFamily: 'monospace', fontSize: '16px', textAlign: 'center', marginBottom: '16px' }}>
                        {newToken.token}
                      </code>
                      <button onClick={() => copyToken(newToken.token)} style={{ width: '100%', backgroundColor: '#10b981', color: 'white', padding: '12px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '16px', marginBottom: '8px' }}>
                         Скопировать
                      </button>
                      <button onClick={() => { setShowTokenModal(false); setNewToken(null) }} style={{ width: '100%', backgroundColor: '#f1f5f9', color: '#64748b', padding: '12px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '16px' }}>
                        Закрыть
                      </button>
                    </div>
                  ) : (
                    <div>
                      <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '24px' }}>Генерация токена</h2>
                      <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', color: '#64748b', fontSize: '14px' }}>Имя клиента</label>
                        <input type="text" value={tokenForm.username} onChange={e => setTokenForm({...tokenForm, username: e.target.value})} style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '16px', boxSizing: 'border-box' }} placeholder="Иван Петров" />
                      </div>
                      <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', color: '#64748b', fontSize: '14px' }}>Тариф</label>
                        <select value={tokenForm.subscription} onChange={e => setTokenForm({...tokenForm, subscription: e.target.value})} style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '16px' }}>
                          <option value="BASIC">Базовый (990₽/мес)</option>
                          <option value="PRO">Профессиональный (2990₽/мес)</option>
                          <option value="ENTERPRISE">Корпоративный (9900₽/мес)</option>
                        </select>
                      </div>
                      <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', color: '#64748b', fontSize: '14px' }}>Срок (дней)</label>
                        <input type="number" value={tokenForm.days_valid} onChange={e => setTokenForm({...tokenForm, days_valid: Number(e.target.value)})} style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '16px', boxSizing: 'border-box' }} />
                      </div>
                      <div style={{ display: 'flex', gap: '12px' }}>
                        <button onClick={() => setShowTokenModal(false)} style={{ flex: 1, backgroundColor: '#f1f5f9', color: '#64748b', padding: '12px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '16px' }}>
                          Отмена
                        </button>
                        <button onClick={generateToken} style={{ flex: 1, backgroundColor: '#3b82f6', color: 'white', padding: '12px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '16px' }}>
                          Сгенерировать
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Payments */}
        {page === 'payments' && (
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '32px', color: '#0f172a' }}>Оплата и тарифы</h1>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', marginBottom: '32px' }}>
              {plans.map(plan => (
                <div key={plan.id} style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px', color: '#0f172a' }}>{plan.name}</h3>
                  <p style={{ fontSize: '32px', fontWeight: 'bold', margin: '16px 0', color: '#0f172a' }}>₽{plan.price}<span style={{ fontSize: '14px', color: '#64748b', fontWeight: 'normal' }}>/мес</span></p>
                  <p style={{ color: '#64748b', fontSize: '14px', marginBottom: '16px' }}>{plan.requests === -1 ? 'Безлимит' : `${plan.requests} запросов`}</p>
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {plan.features.map((f, i) => (
                      <li key={i} style={{ color: '#64748b', fontSize: '14px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ color: '#10b981' }}>✓</span> {f}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#0f172a' }}>
                Общий доход: ₽{payments.filter(p => p.status === 'paid').reduce((sum, p) => sum + p.amount, 0).toLocaleString()}
              </h2>
            </div>

            <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>ID</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Тариф</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Сумма</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Дата</th>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#64748b', fontSize: '14px' }}>Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map(payment => (
                    <tr key={payment.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '16px', color: '#64748b' }}>#{payment.id}</td>
                      <td style={{ padding: '16px' }}>
                        <span style={{ padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: '500', backgroundColor: '#dbeafe', color: '#2563eb' }}>
                          {payment.plan}
                        </span>
                      </td>
                      <td style={{ padding: '16px', fontWeight: '500', color: '#0f172a' }}>₽{payment.amount.toLocaleString()}</td>
                      <td style={{ padding: '16px', color: '#64748b' }}>{payment.date}</td>
                      <td style={{ padding: '16px' }}>
                        <span style={{ padding: '4px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: '500', backgroundColor: '#dcfce7', color: '#16a34a' }}>
                          ✓ {payment.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Settings */}
        {page === 'settings' && (
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '32px', color: '#0f172a' }}>Настройки</h1>
            
            <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px', color: '#0f172a' }}> AI Модель</h2>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#64748b', fontSize: '14px' }}>Модель Groq</label>
                <input type="text" defaultValue="qwen/qwen3.8-27b" style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '16px', boxSizing: 'border-box' }} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', color: '#64748b', fontSize: '14px' }}>Base URL</label>
                <input type="text" defaultValue="https://api.groq.com/openai/v1" style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '16px', boxSizing: 'border-box' }} />
              </div>
            </div>

            <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px', color: '#0f172a' }}>📱 Telegram Бот</h2>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', color: '#64748b', fontSize: '14px' }}>Bot Token</label>
                <input type="password" defaultValue="8903168769:AAHq..." style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '16px', boxSizing: 'border-box' }} />
              </div>
            </div>

            <button style={{ backgroundColor: '#3b82f6', color: 'white', padding: '12px 24px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '16px', fontWeight: '500' }}>
              💾 Сохранить настройки
            </button>
          </div>
        )}

        {!stats && page === 'dashboard' && <p style={{ color: '#64748b' }}>Загрузка...</p>}
      </div>
    </div>
  )
}
