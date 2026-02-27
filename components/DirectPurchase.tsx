import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Loader2, CheckCircle2, XCircle, ShieldCheck, Clock, Copy, ArrowRight, Smartphone } from 'lucide-react';
import { renderIcon, COUNTRIES, SERVICES } from '../constants';

const DirectPurchase = () => {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const serviceId = searchParams.get('service');
    const countryId = searchParams.get('country');

    const [status, setStatus] = useState<'idle' | 'generating' | 'waiting' | 'received' | 'error'>('idle');
    const [orderData, setOrderData] = useState<any>(null);
    const [error, setError] = useState('');
    const [smsCode, setSmsCode] = useState<string | null>(null);

    const service = SERVICES.find(s => s.id === serviceId);
    const country = COUNTRIES.find(c => c.code === countryId);

    const startPurchase = async () => {
        if (!token || !serviceId || !countryId) {
            setError('Missing purchase details (token, service, or country).');
            setStatus('error');
            return;
        }

        setStatus('generating');
        try {
            const res = await fetch('/api/direct/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, service_id: serviceId, country_id: countryId })
            });
            const data = await res.json();
            if (res.ok) {
                setOrderData(data);
                setStatus('waiting');
            } else {
                setError(data.message || 'Failed to start purchase');
                setStatus('error');
            }
        } catch (err) {
            setError('Connection error');
            setStatus('error');
        }
    };

    useEffect(() => {
        let interval: any;
        if (status === 'waiting' && orderData?.order_id) {
            interval = setInterval(async () => {
                try {
                    const res = await fetch(`/api/direct/status?token=${token}&order_id=${orderData.order_id}`);
                    const data = await res.json();
                    if (data.status === 'received') {
                        setSmsCode(data.sms_code);
                        setStatus('received');
                        clearInterval(interval);
                    } else if (data.status === 'cancelled') {
                        setError('Order was cancelled');
                        setStatus('error');
                        clearInterval(interval);
                    }
                } catch (err) {
                    console.error("Status check failed", err);
                }
            }, 5000);
        }
        return () => clearInterval(interval);
    }, [status, orderData, token]);

    if (!token) {
        return (
            <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
                <div className="bg-zinc-900 border border-white/10 p-8 rounded-[2rem] text-center max-w-md">
                    <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <h1 className="text-2xl font-bold text-white mb-2">Invalid Access</h1>
                    <p className="text-zinc-400">This link is invalid or has already been used.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
            <div className="w-full max-w-xl bg-zinc-900 border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden">
                <div className="p-8 border-b border-white/5 flex items-center justify-between bg-zinc-900/50">
                    <div className="flex items-center gap-2 text-emerald-500">
                        <ShieldCheck className="w-6 h-6" />
                        <span className="font-bold text-lg tracking-tight">SMSKenya Direct</span>
                    </div>
                    {status === 'waiting' && (
                        <div className="flex items-center gap-2 text-emerald-500 text-xs font-bold px-3 py-1 bg-emerald-500/10 rounded-full animate-pulse">
                            <Clock className="w-3 h-3" />
                            LIVE TRACKING
                        </div>
                    )}
                </div>

                <div className="p-8">
                    {status === 'idle' && (
                        <div className="text-center space-y-6">
                            <div className="flex justify-center items-center gap-4">
                                <div className="p-4 bg-zinc-800 rounded-2xl">
                                    {renderIcon(service?.icon || '', "w-10 h-10 text-emerald-400")}
                                </div>
                                <ArrowRight className="text-zinc-700" />
                                <div className="text-4xl">{country?.flag}</div>
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-2">Ready to Buy</h2>
                                <p className="text-zinc-400">You are about to generate a {country?.name} number for {service?.name}.</p>
                            </div>
                            <button
                                onClick={startPurchase}
                                className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl transition-all shadow-lg shadow-emerald-600/20"
                            >
                                Get Number Now
                            </button>
                        </div>
                    )}

                    {status === 'generating' && (
                        <div className="text-center py-12 space-y-4">
                            <Loader2 className="w-12 h-12 text-emerald-500 animate-spin mx-auto" />
                            <p className="text-white font-medium">Securing your private line...</p>
                        </div>
                    )}

                    {status === 'waiting' && (
                        <div className="space-y-6">
                            <div className="bg-zinc-950 border border-white/5 p-6 rounded-3xl text-center">
                                <p className="text-xs text-zinc-500 uppercase font-bold tracking-widest mb-2">Your Phone Number</p>
                                <div className="flex items-center justify-center gap-3">
                                    <span className="text-3xl font-mono font-bold text-white tracking-tighter">
                                        {orderData.phone_number}
                                    </span>
                                    <button
                                        onClick={() => {
                                            navigator.clipboard.writeText(orderData.phone_number);
                                        }}
                                        className="p-2 hover:bg-white/5 rounded-lg text-zinc-500 transition-colors"
                                    >
                                        <Copy className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <div className="flex flex-col items-center gap-4 py-8">
                                <div className="relative">
                                    <div className="absolute inset-0 bg-emerald-500/20 blur-xl rounded-full" />
                                    <div className="relative w-16 h-16 bg-zinc-900 border-2 border-emerald-500 rounded-full flex items-center justify-center">
                                        <div className="w-8 h-8 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
                                    </div>
                                </div>
                                <div className="text-center">
                                    <h3 className="text-white font-bold">Waiting for SMS</h3>
                                    <p className="text-sm text-zinc-500">Please enter the number in {service?.name} app now.</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {status === 'received' && (
                        <div className="space-y-6 text-center animate-in zoom-in-95 duration-300">
                            <div className="w-20 h-20 bg-emerald-500/10 border-2 border-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
                                <CheckCircle2 className="w-10 h-10 text-emerald-500" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">Code Received!</h2>
                                <p className="text-zinc-400">Use the code below to complete your verification.</p>
                            </div>
                            <div className="bg-emerald-500 p-8 rounded-3xl shadow-[0_0_50px_rgba(16,185,129,0.4)]">
                                <span className="text-5xl font-mono font-black text-white tracking-[0.2em]">
                                    {smsCode}
                                </span>
                            </div>
                        </div>
                    )}

                    {status === 'error' && (
                        <div className="text-center space-y-6 py-8">
                            <div className="w-16 h-16 bg-red-500/10 border-2 border-red-500/50 rounded-full flex items-center justify-center mx-auto">
                                <XCircle className="w-8 h-8 text-red-500" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-white">Something went wrong</h2>
                                <p className="text-zinc-500 text-sm mt-1">{error}</p>
                            </div>
                            <button
                                onClick={() => setStatus('idle')}
                                className="px-8 py-3 bg-zinc-800 hover:bg-zinc-700 text-white font-bold rounded-xl transition-all"
                            >
                                Try Again
                            </button>
                        </div>
                    )}
                </div>

                <div className="p-6 bg-zinc-950/50 border-t border-white/5 flex items-center justify-center gap-6">
                    <div className="flex items-center gap-2 text-[10px] text-zinc-500 font-bold uppercase tracking-widest">
                        <ShieldCheck className="w-3 h-3" />
                        Private Line
                    </div>
                    <div className="flex items-center gap-2 text-[10px] text-zinc-500 font-bold uppercase tracking-widest">
                        <Smartphone className="w-3 h-3" />
                        Real SIM
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DirectPurchase;
