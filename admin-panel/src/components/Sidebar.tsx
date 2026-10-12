import { LayoutDashboard, Users, Key, CreditCard, Settings, LogOut, Zap } from 'lucide-react'

interface SidebarProps {
  activePage: string
  onNavigate: (page: string) => void
}

export default function Sidebar({ activePage, onNavigate }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Дашборд', icon: LayoutDashboard },
    { id: 'users', label: 'Пользователи', icon: Users },
    { id: 'tokens', label: 'Токены доступа', icon: Key },
    { id: 'payments', label: 'Оплата', icon: CreditCard },
    { id: 'settings', label: 'Настройки', icon: Settings },
  ]

  return (
    <div className="w-64 bg-gradient-to-b from-slate-900 to-slate-800 text-white min-h-screen p-6 flex flex-col">
      <div className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Zap className="text-yellow-400" size={28} />
          AI Business OS
        </h1>
        <p className="text-slate-400 text-sm mt-1">Панель управления</p>
      </div>

      <nav className="space-y-2 flex-1">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = activePage === item.id
          
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                  : 'text-slate-300 hover:bg-slate-700'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>

      <button className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-700 transition-all">
        <LogOut size={20} />
        <span>Выйти</span>
      </button>
    </div>
  )
}
