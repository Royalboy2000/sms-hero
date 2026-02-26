import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  RefreshCcw, Phone, MessageSquare, Clock,
  CheckCircle2, AlertCircle, Shield, LayoutDashboard,
  Smartphone, Globe
} from 'lucide-react';
import { SERVICES, COUNTRIES } from '../constants';

interface Order {
  id: number;
  service_id: string;
  country_id: string;
  phone_number: string;
  order_id_provider: string;
  status: 'waiting' | 'received' | 'cancelled';
  sms_code: string | null;
  timestamp: string;
}

const Dashboard: React.FC = () => {
  const { user, token, quota, refreshQuota } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchOrders = async () => {
    if (!token) return;
    try {
      const response = await fetch('/api/orders', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setOrders(data);
      }
    } catch (error) {
      console.error('Failed to fetch orders', error);
    } finally {
      setIsLoading(false);
    }
  };

  const checkStatus = async (orderId: string) => {
    if (!token) return;
    try {
      const response = await fetch(`/api/order/${orderId}/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        fetchOrders();
        refreshQuota();
      }
    } catch (error) {
      console.error('Failed to check status', error);
    }
  };

  const handleRefreshAll = async () => {
    setIsRefreshing(true);
    const waitingOrders = orders.filter(o => o.status === 'waiting');
    await Promise.all(waitingOrders.map(o => checkStatus(o.order_id_provider)));
    setIsRefreshing(false);
  };

  useEffect(() => {
    fetchOrders();
  }, [token]);

  useEffect(() => {
    const interval = setInterval(() => {
        const waitingOrders = orders.filter(o => o.status === 'waiting');
        if (waitingOrders.length > 0) {
            handleRefreshAll();
        }
    }, 10000);
    return () => clearInterval(interval);
  }, [orders, token]);

  if (!user) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center p-4">
        <Shield className="w-16 h-16 text-zinc-800 mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Login Required</h2>
        <p className="text-zinc-500 text-center max-w-xs">Please login to access your dashboard and manage your numbers.</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-bold text-white flex items-center gap-3">
            <LayoutDashboard className="w-8 h-8 text-emerald-500" />
            User Dashboard
          </h1>
          <p className="text-zinc-500 mt-2">Welcome back, {user.username}. Here are your purchased numbers.</p>
        </div>

        <div className="grid grid-cols-2 gap-4 w-full md:w-auto">
          <div className="bg-zinc-900 border border-white/5 p-4 rounded-3xl">
            <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest mb-1">Numbers Used</p>
            <p className="text-2xl font-mono font-bold text-white">{quota?.used || 0}</p>
          </div>
          <div className="bg-zinc-900 border border-white/5 p-4 rounded-3xl">
            <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest mb-1">Quota Left</p>
            <p className="text-2xl font-mono font-bold text-emerald-500">{(quota?.allowed || 0) - (quota?.used || 0)}</p>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold text-white">Your Orders</h3>
        <button
          onClick={handleRefreshAll}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-full text-sm text-zinc-300 hover:text-white hover:border-emerald-500/50 transition-all"
        >
          <RefreshCcw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh Status
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-48 bg-zinc-900/50 animate-pulse rounded-[2rem] border border-white/5"></div>
          ))}
        </div>
      ) : orders.length === 0 ? (
        <div className="bg-zinc-900/30 border border-dashed border-zinc-800 rounded-[2rem] p-12 text-center">
            <Smartphone className="w-12 h-12 text-zinc-800 mx-auto mb-4" />
            <p className="text-zinc-500 font-medium">No numbers bought yet.</p>
            <p className="text-sm text-zinc-600 mt-1">Visit the Shop to get your first international number.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {orders.map(order => {
            const service = SERVICES.find(s => s.id === order.service_id);
            const country = COUNTRIES.find(c => c.code === order.country_id || c.dialCode === order.country_id);

            return (
              <div key={order.id} className="group relative bg-zinc-900 border border-white/5 rounded-[2rem] p-6 hover:border-emerald-500/20 transition-all overflow-hidden">
                <div className="flex justify-between items-start mb-6">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-zinc-800 rounded-xl flex items-center justify-center">
                            {service ? (
                                <Smartphone className="w-6 h-6 text-emerald-500" />
                            ) : (
                                <Globe className="w-6 h-6 text-zinc-500" />
                            )}
                        </div>
                        <div>
                            <h4 className="font-bold text-white">{service?.name || order.service_id}</h4>
                            <p className="text-xs text-zinc-500">{order.timestamp}</p>
                        </div>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        order.status === 'received' ? 'bg-emerald-500/10 text-emerald-500' :
                        order.status === 'cancelled' ? 'bg-red-500/10 text-red-500' :
                        'bg-zinc-800 text-zinc-400 animate-pulse'
                    }`}>
                        {order.status}
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-black/40 rounded-xl border border-white/5">
                        <span className="text-xs text-zinc-500 uppercase font-bold tracking-widest">Phone Number</span>
                        <span className="text-sm font-mono font-bold text-white">{order.phone_number}</span>
                    </div>

                    {order.status === 'received' && order.sms_code ? (
                        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-center">
                            <p className="text-[10px] text-emerald-500 uppercase font-bold tracking-widest mb-1">Verification Code</p>
                            <p className="text-3xl font-mono font-bold text-white tracking-widest">{order.sms_code}</p>
                        </div>
                    ) : order.status === 'waiting' ? (
                        <div className="p-4 bg-zinc-800/50 rounded-2xl flex flex-col items-center gap-2">
                            <div className="flex items-center gap-2 text-zinc-400 text-sm">
                                <RefreshCcw className="w-4 h-4 animate-spin" />
                                Waiting for SMS...
                            </div>
                            <p className="text-[10px] text-zinc-600 text-center">Codes usually arrive within 2 minutes. Stay on this page.</p>
                        </div>
                    ) : (
                        <div className="p-4 bg-red-500/5 border border-red-500/10 rounded-2xl text-center">
                             <p className="text-xs text-red-400">Order cancelled or timed out.</p>
                        </div>
                    )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div className="mt-12 p-8 glass-panel rounded-[2rem] border border-emerald-500/10 bg-emerald-500/5">
        <div className="flex flex-col md:flex-row items-center gap-6">
            <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center shrink-0">
                <Shield className="w-8 h-8 text-emerald-500" />
            </div>
            <div className="flex-1 text-center md:text-left">
                <h4 className="text-xl font-bold text-white mb-1">Need more numbers?</h4>
                <p className="text-zinc-500 text-sm">Your current limit is {quota?.allowed || 0} numbers. To increase it, contact our admin via Telegram or WhatsApp with your username: <span className="text-white font-bold">{user.username}</span></p>
            </div>
            <a
                href={`https://wa.me/${SERVICES[0].id}`}
                className="px-8 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl transition-all whitespace-nowrap"
            >
                Contact Admin
            </a>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
