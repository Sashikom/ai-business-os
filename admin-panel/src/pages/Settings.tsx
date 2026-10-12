import { Save, Key, Globe, Bell } from 'lucide-react'

export default function Settings() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Настройки</h1>
      
      <div className="space-y-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2"><Key size={20} /> AI Модель</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Модель Groq</label>
              <input type="text" defaultValue="qwen/qwen3.8-27b" className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Base URL</label>
              <input type="text" defaultValue="https://api.groq.com/openai/v1" className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2"><Globe size={20} /> Telegram Бот</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Bot Token</label>
            <input type="password" defaultValue="8903168769:AAHq..." className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2"><Bell size={20} /> Уведомления</h2>
          <label className="flex items-center gap-3">
            <input type="checkbox" defaultChecked className="w-4 h-4" />
            <span className="text-slate-700">Email при новой регистрации</span>
          </label>
          <label className="flex items-center gap-3 mt-2">
            <input type="checkbox" defaultChecked className="w-4 h-4" />
            <span className="text-slate-700">Telegram при ошибке AI</span>
          </label>
        </div>

        <button className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
          <Save size={20} /> Сохранить настройки
        </button>
      </div>
    </div>
  )
}
