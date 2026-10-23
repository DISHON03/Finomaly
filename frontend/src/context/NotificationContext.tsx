import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';

export type NotificationType = 'success' | 'error' | 'info' | 'warning';

interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
}

interface NotificationContextType {
  notify: (type: NotificationType, title: string, message?: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const notify = useCallback((type: NotificationType, title: string, message?: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setNotifications(prev => [...prev, { id, type, title, message }]);

    setTimeout(() => {
      removeNotification(id);
    }, 4500);
  }, [removeNotification]);

  return (
    <NotificationContext.Provider value={{ notify }}>
      {children}
      {/* Toast container */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full px-4 pointer-events-none">
        {notifications.map(n => {
          let bg = 'bg-slate-800 border-slate-700 text-slate-100';
          let icon = <Info className="w-5 h-5 text-cyan-400 flex-shrink-0" />;

          if (n.type === 'success') {
            bg = 'bg-emerald-950/90 border-emerald-700/50 text-emerald-100';
            icon = <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />;
          } else if (n.type === 'error') {
            bg = 'bg-rose-950/90 border-rose-700/50 text-rose-100';
            icon = <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />;
          } else if (n.type === 'warning') {
            bg = 'bg-amber-950/90 border-amber-700/50 text-amber-100';
            icon = <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0" />;
          }

          return (
            <div
              key={n.id}
              className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-2xl border backdrop-blur-md transition-all duration-300 animate-slide-in ${bg}`}
            >
              {icon}
              <div className="flex-1 text-sm">
                <div className="font-semibold">{n.title}</div>
                {n.message && <div className="text-xs opacity-90 mt-0.5">{n.message}</div>}
              </div>
              <button
                onClick={() => removeNotification(n.id)}
                className="opacity-70 hover:opacity-100 transition-opacity p-0.5"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          );
        })}
      </div>
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) throw new Error('useNotification must be used within NotificationProvider');
  return context;
};
