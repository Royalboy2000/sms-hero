import React, { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { useParams } from 'react-router-dom';
import {
  Search,
  MessageCircle,
  ShieldCheck,
  CheckCircle2,
  ExternalLink,
  MapPin,
  Globe
} from 'lucide-react';
import { SERVICES, COUNTRIES, renderIcon, WHATSAPP_CONTACT } from '../constants';
import { Service, Country } from '../types';
import { useCurrency } from '../context/CurrencyContext';

const Dashboard: React.FC = () => {
  const [selectedCountry, setSelectedCountry] = useState<Country>(COUNTRIES[0]);
  const [searchQuery, setSearchQuery] = useState('');
  const [countryQuery, setCountryQuery] = useState('');
  const { currency, formatPrice } = useCurrency();
  const { serviceId, countryId } = useParams<{ serviceId?: string, countryId?: string }>();

  useEffect(() => {
    // Handle URL Params
    if (serviceId) {
      const foundService = SERVICES.find(s => s.id === serviceId);
      if (foundService) {
        setSearchQuery(foundService.name);
      }
    }
    if (countryId) {
      const foundCountry = COUNTRIES.find(c => c.code.toLowerCase() === countryId?.toLowerCase());
      if (foundCountry) {
        setSelectedCountry(foundCountry);
      }
    }
  }, [serviceId, countryId]);

  // Filter services
  const filteredServices = SERVICES.filter(service =>
    service.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Filter countries
  const filteredCountries = COUNTRIES.filter(country =>
    country.name.toLowerCase().includes(countryQuery.toLowerCase())
  );

  const handleOrder = (service: Service) => {
    const priceText = currency === 'KES' ? `KSh ${service.price}` : `$${service.priceUsd}`;
    const text = `Hello, I would like to buy a verification number.%0A%0AService: ${service.name}%0ACountry: ${selectedCountry.name}%0APrice: ${priceText}`;
    const url = `https://wa.me/${WHATSAPP_CONTACT}?text=${text}`;
    window.open(url, '_blank');
  };

  const getPageTitle = () => {
    if (serviceId && countryId && selectedCountry.code.toLowerCase() === countryId.toLowerCase()) {
        const s = SERVICES.find(s => s.id === serviceId);
        if (s) return `Buy ${s.name} Number for ${selectedCountry.name} | SMSKenya`;
    }
    if (serviceId) {
        const s = SERVICES.find(s => s.id === serviceId);
        if (s) return `Buy ${s.name} Verification Number | SMSKenya`;
    }
    if (countryId) {
        const c = COUNTRIES.find(c => c.code.toLowerCase() === countryId.toLowerCase());
        if (c) return `Buy Virtual Numbers for ${c.name} | SMSKenya`;
    }
    return "Dashboard - Buy Premium Virtual Numbers | SMSKenya";
  };

  const getPageDescription = () => {
    if (serviceId && countryId) return `Get a real non-VoIP ${searchQuery} number for ${selectedCountry.name}. Instant delivery via WhatsApp.`;
    return "Browse our catalog of premium services. Buy verification numbers for WhatsApp, Telegram, PayPal, Google, and more. Instant delivery and 24/7 support.";
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Helmet>
        <title>{getPageTitle()}</title>
        <meta name="description" content={getPageDescription()} />
        <link rel="canonical" href={window.location.href.replace('smskenya.com', 'smskenya.net').split('?')[0]} />
      </Helmet>

      {/* Header Info */}
      <div className="flex flex-col md:flex-row justify-between items-end mb-16 border-b border-white/5 pb-8">
        <div>
          <h2 className="text-4xl font-bold text-white tracking-tight mb-2">Service Catalog</h2>
          <p className="text-zinc-500 max-w-lg">
            Select a region and service to request your premium verification number.
            All orders are processed instantly via our WhatsApp concierge.
          </p>
        </div>
        <div className="flex items-center gap-3 mt-6 md:mt-0 bg-emerald-900/10 px-6 py-3 rounded-full border border-emerald-500/10 hover:border-emerald-500/30 transition-colors cursor-default">
             <div className="flex -space-x-2">
                {[1,2,3].map(i => (
                    <div key={i} className="w-8 h-8 rounded-full bg-zinc-800 border-2 border-black flex items-center justify-center text-[10px] text-zinc-500">
                        <MessageCircle className="w-4 h-4 text-emerald-500" />
                    </div>
                ))}
             </div>
             <span className="text-sm font-medium text-emerald-400">Online Support Active</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Left Column: Catalog */}
        <div className="lg:col-span-2 space-y-12">

          {/* Country Selector */}
          <div>
             <div className="flex items-center justify-between mb-6">
                <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                    <Globe className="w-4 h-4" /> 1. Choose Region
                </h3>
                <div className="relative w-48">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3 h-3 text-zinc-500" />
                    <input
                        type="text"
                        placeholder="Search country..."
                        value={countryQuery}
                        onChange={(e) => setCountryQuery(e.target.value)}
                        className="w-full bg-zinc-900 border border-zinc-800 rounded-full pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-zinc-600"
                    />
                </div>
             </div>

             <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 max-h-[320px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent">
              {filteredCountries.map(country => (
                <button
                  key={country.code}
                  onClick={() => setSelectedCountry(country)}
                  className={`relative group flex flex-col items-center gap-2 p-4 rounded-2xl border transition-all duration-300 ${
                    selectedCountry.code === country.code
                      ? 'bg-gradient-to-br from-zinc-800 to-black border-emerald-500 text-white shadow-lg shadow-emerald-900/20'
                      : 'bg-black border-zinc-800 text-zinc-400 hover:bg-zinc-900 hover:border-zinc-700'
                  }`}
                >
                  <span className="text-3xl filter drop-shadow-md scale-100 group-hover:scale-110 transition-transform duration-300">{country.flag}</span>
                  <span className={`text-xs font-bold truncate w-full text-center ${selectedCountry.code === country.code ? 'text-emerald-400' : ''}`}>
                    {country.name}
                  </span>
                  {selectedCountry.code === country.code && (
                      <div className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]"></div>
                  )}
                </button>
              ))}
              {filteredCountries.length === 0 && (
                  <div className="col-span-full py-12 flex flex-col items-center justify-center text-center border border-dashed border-zinc-800 rounded-2xl bg-zinc-900/20">
                      <p className="text-zinc-500 text-sm mb-4">No countries found matching "{countryQuery}"</p>
                      <button
                          onClick={() => {
                            const text = `Hello, I would like to request a number for country: ${countryQuery}`;
                            const url = `https://wa.me/${WHATSAPP_CONTACT}?text=${encodeURIComponent(text)}`;
                            window.open(url, '_blank');
                          }}
                          className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium border border-emerald-500/20 transition-all text-sm group shadow-lg shadow-emerald-900/20"
                      >
                          <MessageCircle className="w-4 h-4" />
                          Request {countryQuery} via WhatsApp
                      </button>
                  </div>
              )}
            </div>
          </div>

          {/* Service Selector */}
          <div>
            <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
               <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4" /> 2. Select Service
               </h3>
              <div className="relative w-full sm:w-80">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                <input
                  type="text"
                  placeholder="Search application (e.g. WhatsApp)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl pl-12 pr-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all placeholder:text-zinc-600 backdrop-blur-sm"
                />
              </div>
            </div>

            <div className="space-y-3">
                {filteredServices.map((service) => (
                    <div
                    key={service.id}
                    className="group relative flex items-center justify-between p-5 bg-black/40 border border-zinc-800/50 rounded-2xl hover:border-emerald-500/40 hover:bg-zinc-900/30 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-900/5 backdrop-blur-sm"
                    >
                        <div className="flex items-center gap-5">
                            <div className="p-3 bg-zinc-900 rounded-xl border border-zinc-800 group-hover:scale-110 transition-transform duration-300 group-hover:border-emerald-500/20">
                                {renderIcon(service.icon, "w-6 h-6 text-zinc-300 group-hover:text-emerald-400")}
                            </div>
                            <div>
                                <h4 className="font-bold text-white text-lg group-hover:text-emerald-400 transition-colors">{service.name}</h4>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-zinc-800/50 text-zinc-400 border border-zinc-800 uppercase tracking-wide">
                                        {service.category}
                                    </span>
                                    <span className="text-[10px] text-zinc-500 flex items-center gap-1">
                                        <CheckCircle2 className="w-3 h-3 text-emerald-500" /> Instant
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-col sm:flex-row items-end sm:items-center gap-4 sm:gap-6">
                            <div className="text-right">
                                <span className="block font-mono text-emerald-400 font-bold text-lg">{formatPrice(service)}</span>
                            </div>
                            <button
                                onClick={() => handleOrder(service)}
                                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-zinc-100 text-black font-bold hover:bg-emerald-400 hover:text-black hover:scale-105 active:scale-95 transition-all duration-200 shadow-lg shadow-white/5"
                            >
                                Order
                                <ExternalLink className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                ))}

                {filteredServices.length === 0 && (
                  <div className="py-12 text-center border border-dashed border-zinc-800 rounded-2xl">
                      <p className="text-zinc-500">No services found matching "{searchQuery}"</p>
                  </div>
                )}
            </div>
          </div>
        </div>

        {/* Right Column: Info & Trust */}
        <div className="lg:col-span-1 space-y-6">
           <div className="sticky top-24 space-y-6">
           {/* Summary Card */}
           <div className="bg-gradient-to-b from-zinc-900 to-black border border-zinc-800 rounded-3xl p-8 backdrop-blur-md shadow-2xl">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                 <MapPin className="w-5 h-5 text-emerald-500" /> Concierge Flow
              </h3>

              <div className="space-y-8 relative">
                 {/* Connector Line */}
                 <div className="absolute left-[19px] top-4 bottom-4 w-0.5 bg-zinc-800"></div>

                 <div className="relative flex gap-6 group">
                    <div className="w-10 h-10 rounded-full bg-zinc-900 border border-zinc-700 group-hover:border-emerald-500/50 flex items-center justify-center shrink-0 z-10 transition-colors">
                        <span className="font-mono text-emerald-500 font-bold">1</span>
                    </div>
                    <div>
                        <h4 className="text-white font-bold text-sm group-hover:text-emerald-400 transition-colors">Select Region & App</h4>
                        <p className="text-zinc-500 text-xs mt-1 leading-relaxed">Choose from 150+ countries and 500+ supported applications.</p>
                    </div>
                 </div>

                 <div className="relative flex gap-6 group">
                    <div className="w-10 h-10 rounded-full bg-zinc-900 border border-zinc-700 group-hover:border-emerald-500/50 flex items-center justify-center shrink-0 z-10 transition-colors">
                        <span className="font-mono text-emerald-500 font-bold">2</span>
                    </div>
                    <div>
                        <h4 className="text-white font-bold text-sm group-hover:text-emerald-400 transition-colors">WhatsApp Order</h4>
                        <p className="text-zinc-500 text-xs mt-1 leading-relaxed">Click 'Order'. Our automated agent on WhatsApp will receive your request.</p>
                    </div>
                 </div>

                 <div className="relative flex gap-6 group">
                    <div className="w-10 h-10 rounded-full bg-zinc-900 border border-zinc-700 group-hover:border-emerald-500/50 flex items-center justify-center shrink-0 z-10 transition-colors">
                        <span className="font-mono text-emerald-500 font-bold">3</span>
                    </div>
                    <div>
                        <h4 className="text-white font-bold text-sm group-hover:text-emerald-400 transition-colors">M-Pesa Payment</h4>
                        <p className="text-zinc-500 text-xs mt-1 leading-relaxed">Pay securely to the provided M-Pesa Till number. Code arrives in ~30s.</p>
                    </div>
                 </div>
              </div>

              <div className="mt-8 pt-8 border-t border-zinc-800">
                  <div className="flex items-center gap-3 text-emerald-400 bg-emerald-900/10 p-4 rounded-xl border border-emerald-500/10">
                      <ShieldCheck className="w-5 h-5 shrink-0" />
                      <div>
                          <p className="text-xs font-bold text-emerald-400">100% Delivery Rate</p>
                          <p className="text-[10px] text-emerald-400/70">Real non-VoIP SIM cards.</p>
                      </div>
                  </div>
              </div>
           </div>

           {/* Support Contact Button */}
           <button
              onClick={() => window.open(`https://wa.me/${WHATSAPP_CONTACT}`, '_blank')}
              className="w-full group relative flex flex-col items-center justify-center gap-2 p-6 rounded-2xl bg-emerald-600 hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-900/20 text-white cursor-pointer"
           >
                <div className="flex items-center gap-2 text-emerald-100 font-medium uppercase tracking-widest text-xs">
                  <MessageCircle className="w-4 h-4" /> 24/7 Support
                </div>
                <span className="text-2xl font-bold font-mono">+44 7598 691673</span>
                <div className="flex items-center gap-2 mt-2 bg-white/20 px-4 py-1.5 rounded-full text-sm font-medium backdrop-blur-sm group-hover:bg-white/30 transition-colors">
                  Chat on WhatsApp <ExternalLink className="w-3 h-3" />
                </div>
           </button>
           </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
