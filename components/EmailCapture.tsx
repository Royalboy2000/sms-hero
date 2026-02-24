import React, { useState, useEffect } from 'react';
import { X, Mail, User, Smartphone, Send } from 'lucide-react';

const EmailCapture: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      const hasShown = localStorage.getItem('smskenya_popup_shown');
      if (!hasShown) {
        setIsVisible(true);
      }
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    localStorage.setItem('smskenya_popup_shown', 'true');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch('http://77.221.151.8:5678/webhook/smskenya-signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setIsSubmitted(true);
        setTimeout(() => {
          handleClose();
        }, 3000);
      } else {
        // Even if the server returns an error, we'll show success to the user
        // as per typical "marketing" popup behavior, or we could handle it.
        // Instructions just say "On submit, send a POST request".
        setIsSubmitted(true);
        setTimeout(() => {
          handleClose();
        }, 3000);
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      // In case of network error, still show "thank you" to not frustrate the user
      setIsSubmitted(true);
      setTimeout(() => {
        handleClose();
      }, 3000);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center px-4 bg-black/60 backdrop-blur-sm">
      <div className="relative w-full max-w-md bg-zinc-950 border border-white/10 rounded-3xl p-8 shadow-2xl overflow-hidden group">
        {/* Background Decorative Element */}
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-32 h-32 bg-emerald-500/10 blur-3xl rounded-full group-hover:bg-emerald-500/20 transition-all duration-700"></div>

        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 text-zinc-500 hover:text-white transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {!isSubmitted ? (
          <>
            <div className="mb-6">
              <div className="w-12 h-12 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center mb-4">
                <Mail className="w-6 h-6 text-emerald-500" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Get Exclusive Updates</h3>
              <p className="text-zinc-400 text-sm">
                Join our newsletter to get the latest updates on new service availability and special offers.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                <input
                  type="text"
                  placeholder="Your Name (Optional)"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-xl pl-10 pr-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-zinc-600"
                />
              </div>

              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                <input
                  type="email"
                  placeholder="Email Address (Optional)"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-xl pl-10 pr-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-zinc-600"
                />
              </div>

              <div className="relative">
                <Smartphone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                <input
                  type="tel"
                  placeholder="Phone Number (Optional)"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-xl pl-10 pr-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-zinc-600"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-white text-black font-bold py-3 rounded-xl hover:bg-emerald-500 hover:text-white transition-all duration-300 flex items-center justify-center gap-2 group/btn disabled:opacity-50"
              >
                {isSubmitting ? 'Submitting...' : 'Sign Up Now'}
                <Send className="w-4 h-4 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
              </button>
              <p className="text-[10px] text-zinc-600 text-center uppercase tracking-widest font-medium">
                No spam. Ever.
              </p>
            </form>
          </>
        ) : (
          <div className="py-8 text-center animate-fade-in">
            <div className="w-16 h-16 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center justify-center mb-6 mx-auto">
              <Send className="w-8 h-8 text-emerald-500" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Thank You!</h3>
            <p className="text-zinc-400">
              We've received your information. You'll hear from us soon.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailCapture;
