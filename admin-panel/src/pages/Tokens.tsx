import { useEffect, useState } from 'react'
import { Plus, Trash2, XCircle, Copy, Check } from 'lucide-react'

const API_URL = 'http://localhost:8001/api/v1/admin'

export default function Tokens() {
  const [tokens, setTokens] = useState<any[]>([])
  const [showModal, setShowModal] = useState(false)
  const [copiedId, setCopiedId] = useState<number | null>(null)
  const [form, setForm] = useState({ subscription: 'BASIC', days_valid: 30, username: '' })
  const [generatedToken, setGeneratedToken] = useState<any>(null)

  useEffect(() => { fetchTokens() }, [])

  const fetchTokens = () => {
    fetch(`${API_URL}/tokens`).then(res => res.json()).then(setTokens)
  }

  const generateToken = async () => {
    const res = await fetch(`${API_URL}/tokens/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    const data = await res.json()
    setGeneratedToken(data)
    fetchTokens()
  }

  const revokeToken = async (id: number) => {
    await fetch(`${API_URL}/tokens/${id}/revoke`, { method: 'POST' })
    fetchTokens()
  }

  const deleteToken = async (id: number) => {
    if (!confirm('Удалить токен?')) return
    await fetch(`${API_URL}/tokens/${id}`, { method: 'DELETE' })
    fetchTokens()
  }

  const copyToken = (token: string, id: number) => {
    navigator.clipboard.writeText(token)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const getStatusBadge = (status: string) => {
    const styles: any = { active: 'bg-green-100 text-green-700', revoked: 'bg-red-100 text-red-700', expired: 'bg-slate-100 text-slate-700' }
    const labels: any = { active: 'Активен', revoked: 'Отозван', expired: 'Истёк' }
    return <span className={`px-3 py-1 rounded-full text-xs font-medium ${styles[status]}`}>{labels[status]}</span>
  }

  return (
    <div className="p-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Токены доступа</h1>
          <p className="text-slate-500 mt-2">Генерация и управление токенами для клиентов</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus size={20} /> Сгенерировать токен
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Токен</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Клиент</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Тариф</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Статус</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Истекает</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Действия</th>
            </tr>
          </thead>
          <tbody>
            {tokens.map(token => (
              <tr key={token.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <code className="bg-slate-100 px-2 py-1 rounded text-sm font-mono">{token.token}</code>
                    <button onClick={() => copyToken(token.token, token.id)} className="p-1 text-slate-500 hover:text-blue-600">
                      {copiedId === token.id ? <Check size={16} className="text-green-600" /> : <Copy size={16} />}
                    </button>
                  </div>
                </td>
                <td className="p-4 text-sm text-slate-600">{token.username}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${token.subscription === 'PRO' ? 'bg-purple-100 text-purple-700' : token.subscription === 'ENTERPRISE' ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'}`}>
                    {token.subscription}
                  </span>
                </td>
                <td className="p-4">{getStatusBadge(token.status)}</td>
                <td className="p-4 text-sm text-slate-600">{token.expires_at}</td>
                <td className="p-4">
                  <div className="flex gap-2">
                    {token.status === 'active' && (
                      <button onClick={() => revokeToken(token.id)} className="p-2 text-orange-600 hover:bg-orange-50 rounded-lg"><XCircle size={18} /></button>
                    )}
                    <button onClick={() => deleteToken(token.id)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg"><Trash2 size={18} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Генерация токена доступа</h2>
            
            {generatedToken ? (
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm text-green-700 mb-2">✅ Токен успешно создан!</p>
                  <code className="block bg-white px-3 py-2 rounded font-mono text-lg text-center">{generatedToken.token}</code>
                  <button onClick={() => copyToken(generatedToken.token, -1)} className="mt-2 w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 flex items-center justify-center gap-2">
                    <Copy size={16} /> Скопировать
                  </button>
                </div>
                <div className="text-sm text-slate-600 space-y-1">
                  <p>Тариф: <b>{generatedToken.subscription}</b></p>
                  <p>Срок: <b>{generatedToken.days_valid} дней</b></p>
                  <p>Истекает: <b>{generatedToken.expires_at}</b></p>
                </div>
                <button onClick={() => { setShowModal(false); setGeneratedToken(null) }} className="w-full bg-slate-100 text-slate-700 py-2 rounded-lg hover:bg-slate-200">Закрыть</button>
              </div>
            ) : (
              <>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Имя клиента (необязательно)</label>
                    <input type="text" value={form.username} onChange={e => setForm({...form, username: e.target.value})} className="w-full px-3 py-2 border border-slate-300 rounded-lg" placeholder="Например: Иван Петров" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Тариф</label>
                    <select value={form.subscription} onChange={e => setForm({...form, subscription: e.target.value})} className="w-full px-3 py-2 border border-slate-300 rounded-lg">
                      <option value="BASIC">Базовый (990₽/мес, 100 запросов)</option>
                      <option value="PRO">Профессиональный (2990₽/мес, 1000 запросов)</option>
                      <option value="ENTERPRISE">Корпоративный (9900₽/мес, безлимит)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Срок действия (дней)</label>
                    <input type="number" value={form.days_valid} onChange={e => setForm({...form, days_valid: Number(e.target.value)})} className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
                  </div>
                </div>
                <div className="flex gap-2 mt-6">
                  <button onClick={() => setShowModal(false)} className="flex-1 bg-slate-100 text-slate-700 py-2 rounded-lg hover:bg-slate-200">Отмена</button>
                  <button onClick={generateToken} className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Сгенерировать</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
