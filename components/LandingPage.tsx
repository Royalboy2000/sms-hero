import React from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { ArrowRight, CheckCircle2, MessageCircle, Star, Users, Globe2, Shield } from 'lucide-react';
import { FEATURES, SERVICES, renderIcon } from '../constants';
import { useCurrency } from '../context/CurrencyContext';

const Typewriter = ({ texts, delay = 150, pause = 2000 }: { texts: string[], delay?: number, pause?: number }) => {
  const [currentTextIndex, setCurrentTextIndex] = React.useState(0);
  const [currentText, setCurrentText] = React.useState('');
  const [isDeleting, setIsDeleting] = React.useState(false);

  React.useEffect(() => {
    const timeout = setTimeout(() => {
      const fullText = texts[currentTextIndex];

      if (!isDeleting) {
        setCurrentText(fullText.substring(0, currentText.length + 1));
        if (currentText === fullText) {
          setTimeout(() => setIsDeleting(true), pause);
        }
      } else {
        setCurrentText(fullText.substring(0, currentText.length - 1));
        if (currentText === '') {
          setIsDeleting(false);
          setCurrentTextIndex((prev) => (prev + 1) % texts.length);
        }
      }
    }, isDeleting ? delay / 2 : delay);

    return () => clearTimeout(timeout);
  }, [currentText, isDeleting, currentTextIndex, texts, delay, pause]);

  return (
    <span className="relative">
      {currentText}
      <span className="ml-1 inline-block w-[4px] h-[0.8em] bg-emerald-500 animate-pulse align-middle"></span>
    </span>
  );
};

const ANIMATED_COUNTRIES = ['Saudi', 'Canada', 'UAE', 'USA', 'UK'];

const LandingPage: React.FC = () => {
  const { formatPrice } = useCurrency();
  return (
    <div className="flex flex-col bg-black">
      <Helmet>
        <title>SMSKenya - United States & Canada Numbers in Kenya</title>
        <meta name="description" content="Get premium United States & Canada Numbers for WhatsApp verification in Kenya. Instant WhatsApp, Telegram, and PayPal activation with secure M-PESA payments. Online 24/7." />
        <meta name="keywords" content="WhatsApp Verification Kenya, US Number Kenya, Buy International Number Kenya, Verify WhatsApp, Receive SMS Online, Activation Code Kenya" />
        <link rel="canonical" href="https://smskenya.net/" />
      </Helmet>

      {/* Hero Section */}
      <section className="relative pt-32 pb-32 overflow-hidden">
        {/* Background Grid */}
        <div className="absolute inset-0 grid-bg opacity-20 pointer-events-none"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/80 to-black pointer-events-none"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-emerald-600/10 rounded-full blur-[120px] -z-10 pointer-events-none"></div>

          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-300 text-xs font-medium mb-8 animate-fade-in-up hover:border-emerald-500/50 transition-colors cursor-default shadow-lg shadow-black/50">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            Proudly Kenyan • Based in Germany
          </div>

          <h1 className="text-5xl md:text-8xl font-bold tracking-tighter text-white mb-8 leading-[0.95] min-h-[2em]">
            Buy a <span className="text-emerald-500"><Typewriter texts={ANIMATED_COUNTRIES} /></span> WhatsApp <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-600 drop-shadow-[0_0_30px_rgba(16,185,129,0.3)]">
              Account in 2 Minutes.
            </span>
          </h1>

          <p className="mt-8 max-w-2xl mx-auto text-lg md:text-xl text-zinc-400 mb-12 font-light leading-relaxed">
            Get your WhatsApp Activation Code instantly. Works for WhatsApp, Telegram, TikTok, and more.
          </p>

          {/* Visual Proof */}
          <div className="mx-auto max-w-sm w-full bg-zinc-900/80 backdrop-blur-xl border border-zinc-800 rounded-2xl p-4 shadow-2xl mb-12 animate-fade-in-up delay-200">
             <div className="flex items-center gap-3">
                 <div className="w-10 h-10 rounded-full bg-[#25D366] flex items-center justify-center shrink-0">
                      <MessageCircle className="w-6 h-6 text-white" />
                 </div>
                 <div className="flex-1 text-left">
                      <div className="flex justify-between items-center mb-0.5">
                          <span className="font-bold text-white text-sm">WhatsApp</span>
                          <span className="text-xs text-zinc-500">now</span>
                      </div>
                      <div className="text-xs text-zinc-300">Your verification code is: <span className="text-white font-bold text-sm ml-1">123-456</span></div>
                 </div>
             </div>
          </div>

          <div className="flex flex-col sm:flex-row justify-center gap-6">
            <Link
              to="/app"
              className="inline-flex items-center justify-center px-8 py-4 bg-emerald-600 text-white rounded-full font-bold text-lg hover:bg-emerald-500 transition-all shadow-[0_0_50px_rgba(16,185,129,0.3)] gap-2 group hover:scale-105"
            >
              Get My International Number <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          {/* Stats Strip */}
          <div className="mt-32 grid grid-cols-2 md:grid-cols-4 gap-8 border-y border-white/5 py-12 bg-white/[0.01]">
            {[
              { label: 'Success Rate', value: '100%' },
              { label: 'Active Numbers', value: '50k+' },
              { label: 'Countries', value: '180+' },
              { label: 'Avg Time', value: '<2m' },
            ].map((stat, i) => (
              <div key={i} className="flex flex-col items-center">
                <span className="text-3xl md:text-4xl font-bold text-white font-mono tracking-tight">{stat.value}</span>
                <span className="text-xs text-zinc-500 uppercase tracking-widest mt-2">{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Showcase */}
      <section className="py-24 bg-zinc-950 border-t border-white/5 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
           <div className="flex flex-col md:flex-row justify-between items-end mb-16">
              <div>
                <h2 className="text-4xl font-bold text-white mb-3">Apps You Can Verify</h2>
                <p className="text-zinc-500 text-lg">Works for WhatsApp, Telegram, TikTok, and more.</p>
              </div>
              <Link to="/app" className="hidden md:flex items-center gap-2 text-emerald-400 hover:text-emerald-300 transition-colors text-sm font-medium">
                View all apps <ArrowRight className="w-4 h-4" />
              </Link>
           </div>

           <div className="grid grid-cols-2 md:grid-cols-6 gap-6">
              {SERVICES.slice(0, 6).map((service) => (
                <Link to="/app" key={service.id} className="group glass-panel p-8 rounded-3xl flex flex-col items-center justify-center gap-6 hover:bg-zinc-900 transition-all duration-300 hover:border-emerald-500/30">
                  <div className="p-4 bg-zinc-900 rounded-2xl border border-zinc-800 group-hover:scale-110 transition-transform duration-300 shadow-xl">
                     {renderIcon(service.icon, "w-8 h-8 opacity-90 group-hover:opacity-100")}
                  </div>
                  <div className="text-center">
                    <span className="block text-sm font-bold text-zinc-200">{service.name}</span>
                    <span className="block text-[10px] text-zinc-500 mt-2 uppercase tracking-wide">Start {formatPrice(service)}</span>
                  </div>
                </Link>
              ))}
           </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-32 relative overflow-hidden bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
             <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Simple & Secure</h2>
             <p className="text-zinc-400 max-w-2xl mx-auto">We use real phone lines to make sure you get your code. It works 100% of the time.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {FEATURES.map((feature, index) => (
              <div key={index} className="p-10 rounded-3xl bg-zinc-900/30 border border-white/5 hover:border-emerald-500/20 transition-all group hover:bg-zinc-900/50">
                <div className="w-14 h-14 bg-zinc-900 rounded-2xl border border-zinc-800 flex items-center justify-center mb-8 group-hover:bg-emerald-500/10 group-hover:border-emerald-500/20 transition-colors shadow-lg">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-white mb-4">{feature.title}</h3>
                <p className="text-zinc-400 leading-relaxed text-sm">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-32 bg-zinc-900/30 border-y border-white/5 relative">
         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
               <div className="space-y-8">
                  <div className="inline-flex items-center gap-2 text-emerald-500 font-bold text-sm tracking-widest uppercase">
                     <Star className="w-4 h-4" /> About SMSKenya
                  </div>
                  <h2 className="text-4xl md:text-6xl font-bold text-white leading-tight">
                     Redefining Digital <br/>
                     <span className="text-zinc-500">Privacy in Kenya.</span>
                  </h2>
                  <p className="text-zinc-400 text-lg leading-relaxed">
                     Founded with a mission to provide secure, accessible, and anonymous communication tools for Kenyan professionals. SMSKenya has grown to become the nation's leading provider of temporary virtual numbers.
                  </p>
                  <div className="grid grid-cols-2 gap-8 pt-8">
                      <div>
                         <div className="flex items-center gap-2 text-white font-bold mb-2">
                            <Users className="w-5 h-5 text-emerald-500" /> 50,000+
                         </div>
                         <p className="text-sm text-zinc-500">Happy Customers</p>
                      </div>
                      <div>
                         <div className="flex items-center gap-2 text-white font-bold mb-2">
                            <Globe2 className="w-5 h-5 text-emerald-500" /> Global Reach
                         </div>
                         <p className="text-sm text-zinc-500">180+ Countries</p>
                      </div>
                  </div>
               </div>
               <div className="relative">
                  <div className="absolute inset-0 bg-emerald-500/20 blur-[100px] rounded-full"></div>
                  <div className="relative bg-black border border-zinc-800 rounded-3xl p-8 shadow-2xl">
                     <div className="space-y-6">
                        <div className="flex items-start gap-4">
                           <div className="w-10 h-10 rounded-full bg-zinc-900 flex items-center justify-center shrink-0 border border-zinc-800">
                              <Shield className="w-5 h-5 text-white" />
                           </div>
                           <div>
                              <h4 className="text-white font-bold">Privacy First</h4>
                              <p className="text-sm text-zinc-500 mt-1">We never store your personal data or verification codes.</p>
                           </div>
                        </div>
                        <div className="h-px bg-zinc-800"></div>
                        <div className="flex items-start gap-4">
                           <div className="w-10 h-10 rounded-full bg-zinc-900 flex items-center justify-center shrink-0 border border-zinc-800">
                              <Users className="w-5 h-5 text-white" />
                           </div>
                           <div>
                              <h4 className="text-white font-bold">Local Support</h4>
                              <p className="text-sm text-zinc-500 mt-1">Based in Germany. Real human support via WhatsApp.</p>
                           </div>
                        </div>
                     </div>
                  </div>
               </div>
            </div>
         </div>
      </section>

      {/* Trust/CTA */}
      <section className="py-32 relative">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass-panel rounded-[3rem] p-16 text-center relative overflow-hidden border border-emerald-500/20 bg-zinc-900/20">
            <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-600/10 rounded-full blur-[100px] -z-10"></div>
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-emerald-600/10 rounded-full blur-[100px] -z-10"></div>

            <h2 className="text-4xl md:text-6xl font-bold text-white mb-8 tracking-tight">Ready to verify?</h2>
            <p className="text-xl text-zinc-400 mb-10 max-w-2xl mx-auto font-light">
              Join thousands of Kenyans using our service today. No contracts. Instant access.
            </p>

            <div className="flex flex-col items-center gap-8">
                <Link
                  to="/app"
                  className="inline-flex items-center justify-center px-12 py-5 bg-emerald-600 text-white rounded-full font-bold text-lg hover:bg-emerald-500 transition-all shadow-xl shadow-emerald-900/30 hover:scale-105"
                >
                  Contact Support
                </Link>
                <div className="flex items-center gap-6 text-xs text-zinc-500 font-mono uppercase tracking-widest">
                    <span className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Secure M-PESA</span>
                    <span className="w-1.5 h-1.5 bg-zinc-800 rounded-full"></span>
                    <span className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" /> Instant Refund</span>
                </div>
            </div>

          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
