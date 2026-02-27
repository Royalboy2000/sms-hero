import React, { useState, useEffect, useMemo } from 'react';
import {
  X, Search, Globe, ShieldCheck, CheckCircle2,
  ExternalLink, MapPin, MessageCircle, ArrowRight,
  Info
} from 'lucide-react';
import { SERVICES, COUNTRIES, renderIcon, WHATSAPP_CONTACT } from '../constants';
import { Service, Country } from '../types';
import { useCurrency } from '../context/CurrencyContext';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface CatalogModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialServiceId?: string;
  initialCountryId?: string;
}

const CatalogModal: React.FC<CatalogModalProps> = ({
  isOpen,
  onClose,
  initialServiceId,
  initialCountryId
}) => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<Country | null>(null);
  const [serviceQuery, setServiceQuery] = useState('');
  const [countryQuery, setCountryQuery] = useState('');

  const { currency, formatPrice, detectedCountry } = useCurrency();
  const { user, token, quota, refreshQuota } = useAuth();
  const [isGenerating, setIsGenerating] = useState(false);
  const [genError, setGenError] = useState('');

  // Reset state when opening
  useEffect(() => {
    if (isOpen) {
      if (initialServiceId) {
        const s = SERVICES.find(s => s.id === initialServiceId);
        if (s) {
            setSelectedService(s);
            setStep(2);
        }
      }
      if (initialCountryId) {
        const c = COUNTRIES.find(c => c.code.toLowerCase() === initialCountryId.toLowerCase());
        if (c) setSelectedCountry(c);
      } else if (detectedCountry) {
        const c = COUNTRIES.find(c => c.code === detectedCountry);
        if (c) setSelectedCountry(c);
      } else if (!selectedCountry) {
        setSelectedCountry(COUNTRIES[0]); // Default to Kenya
      }
    } else {
        // Reset state when closed to ensure a clean start next time
        setStep(1);
        setSelectedService(null);
        setServiceQuery('');
        setCountryQuery('');
    }
  }, [isOpen, initialServiceId, initialCountryId, detectedCountry]);

  const filteredServices = useMemo(() =>
    SERVICES.filter(s => s.name.toLowerCase().includes(serviceQuery.toLowerCase())),
    [serviceQuery]
  );

  const filteredCountries = useMemo(() =>
    COUNTRIES.filter(c => c.name.toLowerCase().includes(countryQuery.toLowerCase())),
    [countryQuery]
  );

  const handleOrder = () => {
    if (!selectedService || !selectedCountry) return;
    const priceText = currency === 'KES' ? `KSh ${selectedService.price}` : `$${selectedService.priceUsd}`;
    const text = `Hello, I would like to buy a verification number.%0A%0AService: ${selectedService.name}%0ACountry: ${selectedCountry.name}%0APrice: ${priceText}`;
    const url = `https://wa.me/${WHATSAPP_CONTACT}?text=${text}`;
    window.open(url, '_blank');
  };

  const handleGenerate = async () => {
    if (!selectedService || !selectedCountry || !token) return;

    setIsGenerating(true);
    setGenError('');

    try {
      const response = await fetch('/api/generate-number', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          service_id: selectedService.id,
          country_id: selectedCountry.code
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Redirect to dashboard
        onClose();
        navigate('/dashboard');
      } else {
        setGenError(data.message || 'Failed to generate number');
      }
    } catch (err) {
      setGenError('Failed to connect to server');
    } finally {
      setIsGenerating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-300">
      <div className="relative w-full max-w-4xl bg-zinc-950 border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col md:flex-row max-h-[90vh]">

        {/* Left Side: Info & Steps (Visible on Desktop) */}
        <div className="hidden md:flex w-72 bg-zinc-900/50 p-8 flex-col justify-between border-r border-white/5">
          <div>
            <div className="flex items-center gap-2 text-emerald-500 mb-6">
                <ShieldCheck className="w-6 h-6" />
                <span className="font-bold tracking-tight">SMSKenya</span>
            </div>

            <h2 className="text-xl font-bold text-white mb-4">How it works</h2>
            <div className="space-y-6">
                {[
                    { icon: <Search className="w-4 h-4" />, text: "Pick an App", active: step === 1 },
                    { icon: <Globe className="w-4 h-4" />, text: "Pick a Country", active: step === 2 },
                    { icon: <MessageCircle className="w-4 h-4" />, text: "Get Your Code", active: step === 3 }
                ].map((s, i) => (
                    <div key={i} className={`flex items-center gap-3 text-sm ${s.active ? 'text-emerald-400 font-bold' : 'text-zinc-500'}`}>
                        <div className={`w-8 h-8 rounded-full border flex items-center justify-center ${s.active ? 'border-emerald-500 bg-emerald-500/10' : 'border-zinc-800'}`}>
                            {s.icon}
                        </div>
                        {s.text}
                    </div>
                ))}
            </div>
          </div>

          <div className="p-4 bg-emerald-500/5 rounded-2xl border border-emerald-500/10">
            <p className="text-[10px] text-emerald-500 font-bold uppercase tracking-widest mb-1">Guaranteed</p>
            <p className="text-xs text-zinc-400 leading-relaxed">Real SIM cards only. Automatic refunds for failed activations.</p>
          </div>
        </div>

        {/* Right Side: Main Content */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="p-6 border-b border-white/5 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white">
                {step === 1 ? 'Pick an App' : `Get Code for ${selectedService?.name}`}
              </h3>
              <p className="text-xs text-zinc-500">
                {step === 1 ? 'Which app do you want to open?' : 'Which country do you want?'}
              </p>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors text-zinc-500 hover:text-white">
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent">
            {step === 1 ? (
              <div className="space-y-6">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                  <input
                    autoFocus
                    type="text"
                    placeholder="Type app name (WhatsApp, etc)..."
                    value={serviceQuery}
                    onChange={(e) => setServiceQuery(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-2xl pl-12 pr-4 py-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all shadow-inner"
                  />
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {filteredServices.map(service => (
                    <button
                      key={service.id}
                      onClick={() => {
                        setSelectedService(service);
                        setStep(2);
                      }}
                      className="group relative flex flex-col items-center gap-3 p-6 rounded-3xl bg-zinc-900/30 border border-zinc-800/50 hover:border-emerald-500/40 hover:bg-zinc-900 transition-all duration-300 overflow-hidden"
                    >
                      <div className="absolute inset-0 bg-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                      <div className="p-3 bg-zinc-800 rounded-2xl group-hover:scale-110 transition-transform relative z-10">
                        {renderIcon(service.icon, "w-8 h-8 text-zinc-300 group-hover:text-emerald-400")}
                      </div>
                      <div className="text-center">
                        <span className="block font-bold text-white text-sm">{service.name}</span>
                        <span className="block text-[10px] text-zinc-500 mt-1 uppercase">{service.category}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
                <div className="flex flex-col sm:flex-row items-center gap-4 bg-zinc-900/50 p-4 rounded-3xl border border-zinc-800">
                    <div className="p-3 bg-zinc-800 rounded-xl">
                        {renderIcon(selectedService?.icon || '', "w-6 h-6 text-emerald-400")}
                    </div>
                    <div className="flex-1 text-center sm:text-left">
                        <h4 className="font-bold text-white">{selectedService?.name} Verification</h4>
                        <p className="text-xs text-zinc-500">Starting from <span className="text-emerald-400 font-mono font-bold">{selectedService ? formatPrice(selectedService) : ''}</span></p>
                    </div>
                    <button onClick={() => setStep(1)} className="text-xs text-emerald-500 hover:underline px-4 py-2">Change App</button>
                </div>

                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Choose Country</h4>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3 h-3 text-zinc-500" />
                            <input
                                type="text"
                                placeholder="Search country..."
                                value={countryQuery}
                                onChange={(e) => setCountryQuery(e.target.value)}
                                className="bg-zinc-900 border border-zinc-800 rounded-full pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500/50"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        {filteredCountries.map(country => (
                            <button
                                key={country.code}
                                onClick={() => setSelectedCountry(country)}
                                className={`relative flex items-center gap-3 p-3 rounded-xl border transition-all overflow-hidden ${
                                    selectedCountry?.code === country.code
                                    ? 'bg-emerald-500/20 border-emerald-500 text-white shadow-[0_0_15px_rgba(16,185,129,0.2)]'
                                    : 'bg-black border-zinc-800 text-zinc-400 hover:border-zinc-700'
                                }`}
                            >
                                {selectedCountry?.code === country.code && (
                                    <div className="absolute inset-0 bg-emerald-500/5 animate-pulse" />
                                )}
                                <span className="text-xl">{country.flag}</span>
                                <span className="text-xs font-medium truncate">{country.name}</span>
                            </button>
                        ))}
                    </div>
                </div>
              </div>
            )}
          </div>

          <div className="p-6 border-t border-white/5 bg-zinc-900/20">
             {step === 2 && selectedService && selectedCountry ? (
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center">
                            <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                        </div>
                        <div>
                            <p className="text-xs text-zinc-500 uppercase font-bold tracking-widest">Price to Pay</p>
                            <p className="text-2xl font-mono font-bold text-white">{formatPrice(selectedService)}</p>
                        </div>
                    </div>

                    <div className="flex-1 w-full sm:w-auto">
                        {genError && (
                             <div className="mb-2 bg-red-500/5 p-3 rounded-xl border border-red-500/10">
                                <p className="text-[10px] text-red-500 font-bold">{genError}</p>
                                {genError.toLowerCase().includes('quota') && (
                                    <a
                                        href={`https://wa.me/${WHATSAPP_CONTACT}?text=Hello, my username is ${user?.username}. I need to increase my number generation quota.`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-[10px] text-emerald-500 hover:underline mt-1 inline-block font-bold"
                                    >
                                        Contact Admin on WhatsApp to get credit →
                                    </a>
                                )}
                                {genError.toLowerCase().includes('whitelist') && (
                                    <a
                                        href={`https://wa.me/${WHATSAPP_CONTACT}?text=Hello, I would like to whitelist ${selectedService?.name} in ${selectedCountry?.name} for my account (${user?.username}).`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-[10px] text-emerald-500 hover:underline mt-1 inline-block font-bold"
                                    >
                                        Ask Admin to Whitelist this Service →
                                    </a>
                                )}
                             </div>
                        )}
                        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-4">
                            {user ? (
                                <button
                                    disabled={isGenerating || (quota && (quota.allowed - quota.used) <= 0)}
                                    onClick={handleGenerate}
                                    className="flex-1 sm:flex-none flex items-center justify-center gap-3 px-10 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] group hover:scale-105 disabled:opacity-50 disabled:scale-100"
                                >
                                    {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : (quota && (quota.allowed - quota.used) <= 0) ? 'No Quota Left' : 'Generate Number Now'}
                                    {!isGenerating && <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />}
                                </button>
                            ) : (
                                <button
                                    onClick={handleOrder}
                                    className="flex-1 sm:flex-none flex items-center justify-center gap-3 px-10 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] group hover:scale-105"
                                >
                                    Send Order to WhatsApp
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </button>
                            )}
                            <div className="flex flex-col items-center sm:items-end gap-1">
                                <p className="text-[10px] text-zinc-500 font-medium">Pay safely via M-PESA</p>
                                {user && <p className="text-[10px] text-emerald-500 font-bold">Quota: {(quota?.allowed || 0) - (quota?.used || 0)} left</p>}
                            </div>
                        </div>
                    </div>
                </div>
             ) : (
                <div className="flex items-center gap-3 text-zinc-500 bg-white/5 p-4 rounded-2xl">
                    <Info className="w-5 h-5 text-emerald-500" />
                    <p className="text-xs">Select an application and country to continue with your order.</p>
                </div>
             )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CatalogModal;
