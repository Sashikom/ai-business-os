import { useEffect, useState } from 'react'
import { Users, MessageSquare, TrendingUp, DollarSign, Key, Activity } from 'lucide-react'
import StatCard from '../components/StatCard'

const API_URL = 'http://185.161.69.108:8005/api/v1/admin'

const weekData = [
  { name: 'Пн', requests: 120, revenue: 2990 },
  { name: 'Вт', requests: 180, revenue: 990 },
  { name: 'Ср', requests: 150, revenue: 2990 },
  { name: 'Чт', requests: 220, revenue: 990 },
  { name: 'Пт', requests: 280, revenue: 2990 },
  { name: 'Сб', requests: 190, revenue: 990 },
  { name: 'Вс', requests: 160, revenue: 0 },
]

const maxRequests = Math.max(...weekData.map(d => d.requests))
const maxRevenue = Math.max(...weekData.map(d => d.revenue))

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    fetch(`${API_URL}/stats`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Stats error:', err))
  }, [])

  if (!stats) return <div className="p-8 text-slate-500">Загрузка...</div>

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Дашборд</h1>
        <p className="text-slate-500 mt-2">Обзор активности платформы</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <StatCard title="Всего пользователей" value={stats.total_users} change="+12% за неделю" icon={Users} color="bg-blue-500" />
        <StatCard title="Активных токенов" value={stats.active_tokens} change="+8% за месяц" icon={Key} color="bg-purple-500" />
        <StatCard title="AI запросов" value={stats.total_requests.toLocaleString()} change="+23% к вчера" icon={MessageSquare} color="bg-green-500" />
        <StatCard title="Доход за всё время" value={`₽${stats.total_revenue.toLocaleString()}`} change="+15% к прошлому" icon={DollarSign} color="bg-orange-500" />
        <StatCard title="Активных пользователей" value={stats.active_users} icon={Activity} color="bg-teal-500" />
        <StatCard title="Рост за месяц" value={`${stats.monthly_growth}%`} icon={TrendingUp} color="bg-pink-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <h2 className="text-xl font-bold text-slate-900 mb-6">AI запросы за неделю</h2>
          <div className="space-y-4">
            {weekData.map((day, i) => (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">{day.name}</span>
                  <span className="font-medium text-slate-900">{day.requests}</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${(day.requests / maxRequests) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Доход за неделю</h2>
          <div className="space-y-4">
            {weekData.map((day, i) => (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">{day.name}</span>
                  <span className="font-medium text-slate-900">₽{day.revenue.toLocaleString()}</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all"
                    style={{ width: `${(day.revenue / maxRevenue) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
