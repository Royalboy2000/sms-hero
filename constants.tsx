import React from 'react';
import { Service, Country } from './types';
import {
  Zap,
  Globe,
  Lock,
  Smartphone,
  ShieldCheck,
  Server,
  Clock,
  Award
} from 'lucide-react';

export const WHATSAPP_CONTACT = "447598691673";

// Pricing in Kenyan Shillings (KSh) - Premium Tier (Min 2000)
export const SERVICES: Service[] = [
  { id: 'wa', name: 'WhatsApp', icon: 'whatsapp', price: 2500, category: 'messenger' },
  { id: 'tg', name: 'Telegram', icon: 'telegram', price: 2200, category: 'messenger' },
  { id: 'ig', name: 'Instagram', icon: 'instagram', price: 2000, category: 'social' },
  { id: 'fb', name: 'Facebook', icon: 'facebook', price: 2000, category: 'social' },
  { id: 'goo', name: 'Google', icon: 'google', price: 2800, category: 'other' },
  { id: 'tt', name: 'TikTok', icon: 'tiktok', price: 2000, category: 'social' },
  { id: 'tw', name: 'Twitter/X', icon: 'twitter', price: 2100, category: 'social' },
  { id: 'li', name: 'LinkedIn', icon: 'linkedin', price: 2400, category: 'social' },
  { id: 'pp', name: 'PayPal', icon: 'paypal', price: 3000, category: 'other' },
  { id: 'airbnb', name: 'Airbnb', icon: 'airbnb', price: 2200, category: 'other' },
  { id: 'bolt', name: 'Bolt', icon: 'bolt', price: 2000, category: 'other' },
];

export const COUNTRIES: Country[] = [
  { code: 'KE', name: 'Kenya', dialCode: '+254', flag: '🇰🇪' },
  { code: 'US', name: 'United States', dialCode: '+1', flag: '🇺🇸' },
  { code: 'GB', name: 'United Kingdom', dialCode: '+44', flag: '🇬🇧' },
  { code: 'CA', name: 'Canada', dialCode: '+1', flag: '🇨🇦' },
  { code: 'ZA', name: 'South Africa', dialCode: '+27', flag: '🇿🇦' },
  { code: 'AE', name: 'UAE', dialCode: '+971', flag: '🇦🇪' },
  { code: 'CN', name: 'China', dialCode: '+86', flag: '🇨🇳' },
  { code: 'DE', name: 'Germany', dialCode: '+49', flag: '🇩🇪' },
  { code: 'IN', name: 'India', dialCode: '+91', flag: '🇮🇳' },
  { code: 'NG', name: 'Nigeria', dialCode: '+234', flag: '🇳🇬' },
  { code: 'AU', name: 'Australia', dialCode: '+61', flag: '🇦🇺' },
  { code: 'FR', name: 'France', dialCode: '+33', flag: '🇫🇷' },
  { code: 'NL', name: 'Netherlands', dialCode: '+31', flag: '🇳🇱' },
  { code: 'BR', name: 'Brazil', dialCode: '+55', flag: '🇧🇷' },
  { code: 'RU', name: 'Russia', dialCode: '+7', flag: '🇷🇺' },
  { code: 'TZ', name: 'Tanzania', dialCode: '+255', flag: '🇹🇿' },
  { code: 'UG', name: 'Uganda', dialCode: '+256', flag: '🇺🇬' },
  { code: 'SA', name: 'Saudi Arabia', dialCode: '+966', flag: '🇸🇦' },
  { code: 'QA', name: 'Qatar', dialCode: '+974', flag: '🇶🇦' },
  { code: 'JP', name: 'Japan', dialCode: '+81', flag: '🇯🇵' },
  { code: 'KR', name: 'South Korea', dialCode: '+82', flag: '🇰🇷' },
  { code: 'SG', name: 'Singapore', dialCode: '+65', flag: '🇸🇬' },
  { code: 'TR', name: 'Turkey', dialCode: '+90', flag: '🇹🇷' },
  { code: 'ES', name: 'Spain', dialCode: '+34', flag: '🇪🇸' },
  { code: 'IT', name: 'Italy', dialCode: '+39', flag: '🇮🇹' },
  { code: 'SE', name: 'Sweden', dialCode: '+46', flag: '🇸🇪' },
  { code: 'CH', name: 'Switzerland', dialCode: '+41', flag: '🇨🇭' },
  { code: 'PL', name: 'Poland', dialCode: '+48', flag: '🇵🇱' },
  { code: 'ID', name: 'Indonesia', dialCode: '+62', flag: '🇮🇩' },
  { code: 'PH', name: 'Philippines', dialCode: '+63', flag: '🇵🇭' },
];

export const FEATURES = [
  {
    title: 'Concierge Service',
    description: 'Personalized setup via WhatsApp.',
    icon: <Zap className="w-5 h-5 text-emerald-400" />
  },
  {
    title: 'Tier-1 Carriers',
    description: 'Real non-VoIP SIMs for 100% delivery.',
    icon: <Globe className="w-5 h-5 text-emerald-400" />
  },
  {
    title: 'Encrypted Privacy',
    description: 'Your identity is protected.',
    icon: <Lock className="w-5 h-5 text-emerald-400" />
  },
  {
    title: 'Instant Refunds',
    description: 'Automatic refunds for failed codes.',
    icon: <Clock className="w-5 h-5 text-emerald-400" />
  }
];

// SVG Components for Real Logos - Styled for Dark Theme
const WhatsAppIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="#25D366" className={className} xmlns="http://www.w3.org/2000/svg"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
);

const TelegramIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="#229ED9" className={className} xmlns="http://www.w3.org/2000/svg"><path d="M12 0C5.37 0 0 5.37 0 12s5.37 12 12 12 12-5.37 12-12S18.63 0 12 0zm5.562 8.161c-.18 1.897-.962 6.502-1.359 8.627-.168.9-.5 1.201-.82 1.23-.697.064-1.226-.46-1.901-.903-1.056-.692-1.653-1.123-2.678-1.799-1.185-.781-.417-1.21.258-1.911.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.139-5.062 3.345-.479.329-.913.489-1.302.481-.428-.008-1.252-.241-1.865-.44-.751-.244-1.349-.374-1.297-.789.027-.216.324-.437.893-.663 3.498-1.524 5.831-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.477-1.635.099-.002.321.023.465.141.119.098.152.228.166.319.016.104.031.305.025.466z"/></svg>
);

const FacebookIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="#1877F2" className={className} xmlns="http://www.w3.org/2000/svg"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
);

const InstagramIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="ig-grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stopColor="#833AB4"/><stop offset="50%" stopColor="#FD1D1D"/><stop offset="100%" stopColor="#FCB045"/></linearGradient></defs><path fill="url(#ig-grad)" d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.789.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.336.935 20.667.523 19.878.217 19.113.131 18.243.131 16.966.072 15.687.012 15.276 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.897 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.897-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"/></svg>
);

const GoogleIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} xmlns="http://www.w3.org/2000/svg"><path fill="#4285F4" d="M23.745 12.27c0-.743-.067-1.467-.19-2.162H12.25v4.09h6.47c-.28 1.487-1.12 2.747-2.38 3.59v2.964h3.843c2.246-2.066 3.562-5.118 3.562-8.482z"/><path fill="#34A853" d="M12.25 23.935c3.24 0 5.957-1.074 7.942-2.906l-3.843-2.964c-1.072.716-2.44 1.144-4.099 1.144-3.15 0-5.815-2.127-6.766-4.99H1.474v3.136C3.475 21.282 7.568 23.935 12.25 23.935z"/><path fill="#FBBC05" d="M5.484 14.22a7.18 7.18 0 010-4.44V6.643H1.475a11.96 11.96 0 000 10.713l4.009-3.136z"/><path fill="#EA4335" d="M12.25 4.886c1.764 0 3.35.607 4.596 1.796l3.435-3.447C18.204 1.306 15.484 0 12.25 0 7.568 0 3.475 2.653 1.475 6.643l4.01 3.136c.95-2.862 3.615-4.893 6.765-4.893z"/></svg>
);

const TwitterIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="#fff" className={className} xmlns="http://www.w3.org/2000/svg"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
);

const TikTokIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="#fff" className={className} xmlns="http://www.w3.org/2000/svg"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.49-3.35-3.98-5.6-.54-2.25-.24-4.65.87-6.75 1.18-2.2 3.53-3.79 6-3.93.47-.04.95-.02 1.42.03v4.08c-.72-.03-1.44.25-2.01.75-.54.47-.85 1.12-.87 1.81.01.4.09.81.25 1.19.46 1.09 1.68 1.69 2.78 1.54.91-.12 1.65-.75 1.97-1.57.24-.62.22-1.3.22-1.96V.02z"/></svg>
);

const LinkedInIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="#0A66C2" className={className} xmlns="http://www.w3.org/2000/svg"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
);

const PayPalIcon = ({ className }: { className?: string }) => (
    <svg viewBox="0 0 24 24" className={className} xmlns="http://www.w3.org/2000/svg"><path fill="#003087" d="M23.94 4.54c-.58 6.23-4.66 9.69-9.33 10.99l-.05.01c-.13.04-.26.13-.3.27l-2.18 10.74c-.06.33-.35.56-.69.56H5.25c-.47 0-.83-.43-.75-.89l3.49-21.65c.07-.4.42-.69.83-.69h8.04c4.66 0 7.54 2.5 7.08 6.84z"/><path fill="#009cde" d="M20.34 3.93c-1.63 7.23-9.56 8.71-9.56 8.71l-1.46 7.18c-.06.33-.35.56-.69.56h-3.9c-.31 0-.57-.22-.62-.53l.72-3.56 3.65-17.96c.07-.4.42-.69.83-.69h7.45c3.67 0 5.4 1.9 4.14 6.29z"/><path fill="#012169" d="M8.82 10.99l-1.5 7.37c-.07.41.24.79.66.79h3.41c.34 0 .63-.23.69-.56l.54-2.65c.16-.8.87-1.37 1.68-1.37h.17c3.94 0 7.34-2.06 7.63-6.51.01-.15.02-.31.02-.46-.35 2.15-2.07 3.39-4.8 3.39H8.82z"/></svg>
);

const AirbnbIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="#FF5A5F" className={className} xmlns="http://www.w3.org/2000/svg"><path d="M12 1.5C9.7 1.5 7.7 2.3 6.3 3.6c-2.4 2.4-2.4 6.3 0 8.7L12 18l5.7-5.7c2.4-2.4 2.4-6.3 0-8.7-1.4-1.3-3.4-2.1-5.7-2.1zm0 13c-1.7 0-3-1.3-3-3s1.3-3 3-3 3 1.3 3 3-1.3 3-3 3z"/></svg>
);

const BoltIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="#34D186" className={className} xmlns="http://www.w3.org/2000/svg"><path d="M14.5 2L5 13h5.5l-2.5 9 9.5-11H12l2.5-9z"/></svg>
);


// Helper to render lucide icons from string IDs
export const renderIcon = (iconName: string, className: string = "w-6 h-6") => {
  switch (iconName) {
    case 'whatsapp': return <WhatsAppIcon className={className} />;
    case 'telegram': return <TelegramIcon className={className} />;
    case 'instagram': return <InstagramIcon className={className} />;
    case 'facebook': return <FacebookIcon className={className} />;
    case 'twitter': return <TwitterIcon className={className} />;
    case 'linkedin': return <LinkedInIcon className={className} />;
    case 'google': return <GoogleIcon className={className} />;
    case 'tiktok': return <TikTokIcon className={className} />;
    case 'paypal': return <PayPalIcon className={className} />;
    case 'airbnb': return <AirbnbIcon className={className} />;
    case 'bolt': return <BoltIcon className={className} />;
    default: return <Smartphone className={className} />;
  }
};
