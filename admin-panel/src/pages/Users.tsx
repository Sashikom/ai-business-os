import { useEffect, useState } from 'react'
import { Ban, CheckCircle, Trash2, Clock } from 'lucide-react'

const API_URL = 'http://185.161.69.108:8005/api/v1/admin'

export default function Users() {
  const [users, setUsers] = useState<any[]>([])

  useEffect(() => {
    fetch(`${API_URL}/users`)
      .then(res => res.json())
      .then(data => setUsers(data))
  }, [])

  const toggleStatus = async (userId: number, newStatus: string) => {
    await fetch(`${API_URL}/users/${userId}/toggle`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    })
    setUsers(users.map(u => u.id === userId ? { ...u, status: newStatus } : u))
  }

  const deleteUser = async (userId: number) => {
    if (!confirm('Удалить пользователя?')) return
    await fetch(`${API_URL}/users/${userId}`, { method: 'DELETE' })
    setUsers(users.filter(u => u.id !== userId))
  }

  const getStatusBadge = (status: string) => {
    const styles: any = {
      active: 'bg-green-100 text-green-700',
      blocked: 'bg-red-100 text-red-700',
    }
    const labels: any = { active: 'Активен', blocked: 'Заблокирован' }
    return <span className={`px-3 py-1 rounded-full text-xs font-medium ${styles[status]}`}>{labels[status]}</span>
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Пользователи</h1>
        <p className="text-slate-500 mt-2">Управление клиентами платформы</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Пользователь</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Тариф</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Статус</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Запросы</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Истекает</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="p-4">
                  <div className="font-medium text-slate-900">{user.username}</div>
                  <div className="text-sm text-slate-500">{user.email}</div>
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${user.subscription === 'PRO' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                    {user.subscription}
                  </span>
                </td>
                <td className="p-4">{getStatusBadge(user.status)}</td>
                <td className="p-4 text-sm text-slate-600">{user.requests_used} / {user.requests_limit}</td>
                <td className="p-4 text-sm text-slate-600 flex items-center gap-1"><Clock size={14} />{user.expires_at}</td>
                <td className="p-4">
                  <div className="flex gap-2">
                    {user.status === 'active' ? (
                      <button onClick={() => toggleStatus(user.id, 'blocked')} className="p-2 text-red-600 hover:bg-red-50 rounded-lg"><Ban size={18} /></button>
                    ) : (
                      <button onClick={() => toggleStatus(user.id, 'active')} className="p-2 text-green-600 hover:bg-green-50 rounded-lg"><CheckCircle size={18} /></button>
                    )}
                    <button onClick={() => deleteUser(user.id)} className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg"><Trash2 size={18} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
