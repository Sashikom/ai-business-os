import { useEffect, useState } from 'react'
import { CreditCard, CheckCircle, Clock, XCircle } from 'lucide-react'

const API_URL = 'http://185.161.69.108:8005/api/v1/admin'

export default function Payments() {
  const [payments, setPayments] = useState<any[]>([])
  const [plans, setPlans] = useState<any[]>([])

  useEffect(() => {
    fetch(`${API_URL}/payments`).then(res => res.json()).then(setPayments)
    fetch(`${API_URL}/plans`).then(res => res.json()).then(setPlans)
  }, [])

  const getStatusIcon = (status: string) => {
    if (status === 'paid') return <CheckCircle size={18} className="text-green-600" />
    if (status === 'pending') return <Clock size={18} className="text-orange-600" />
    return <XCircle size={18} className="text-red-600" />
  }

  const totalRevenue = payments.filter(p => p.status === 'paid').reduce((sum, p) => sum + p.amount, 0)

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Оплата и тарифы</h1>
        <p className="text-slate-500 mt-2">Управление платежами и тарифными планами</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {plans.map(plan => (
          <div key={plan.id} className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900">{plan.name}</h3>
            <p className="text-3xl font-bold text-slate-900 mt-2">₽{plan.price}<span className="text-sm text-slate-500 font-normal">/мес</span></p>
            <p className="text-sm text-slate-500 mt-1">{plan.requests === -1 ? 'Безлимит запросов' : `${plan.requests} запросов`}</p>
            <ul className="mt-4 space-y-2">
              {plan.features.map((f: string, i: number) => (
                <li key={i} className="text-sm text-slate-600 flex items-center gap-2">
                  <CheckCircle size={14} className="text-green-600" /> {f}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Общий доход: ₽{totalRevenue.toLocaleString()}</h2>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left p-4 text-sm font-medium text-slate-600">ID</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Пользователь</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Тариф</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Сумма</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Дата</th>
              <th className="text-left p-4 text-sm font-medium text-slate-600">Статус</th>
            </tr>
          </thead>
          <tbody>
            {payments.map(payment => (
              <tr key={payment.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="p-4 text-sm text-slate-600">#{payment.id}</td>
                <td className="p-4 text-sm text-slate-600">Пользователь #{payment.user_id}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${payment.plan === 'PRO' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                    {payment.plan}
                  </span>
                </td>
                <td className="p-4 font-medium text-slate-900">₽{payment.amount.toLocaleString()}</td>
                <td className="p-4 text-sm text-slate-600">{payment.date}</td>
                <td className="p-4 flex items-center gap-2">
                  {getStatusIcon(payment.status)}
                  <span className="text-sm">{payment.status === 'paid' ? 'Оплачено' : payment.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
