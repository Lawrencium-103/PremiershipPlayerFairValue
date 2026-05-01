import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, KeyRound, AlertTriangle } from 'lucide-react';

const SECRET_CODE = 'FairValue-103';
const STORAGE_KEY = 'fv_access_granted';

export function useAccessControl() {
  const [granted, setGranted] = useState<boolean>(() => {
    return sessionStorage.getItem(STORAGE_KEY) === 'true';
  });

  const grant = () => {
    sessionStorage.setItem(STORAGE_KEY, 'true');
    setGranted(true);
  };

  return { granted, grant };
}

interface SecretGateProps {
  onGranted: () => void;
}

export default function SecretGate({ onGranted }: SecretGateProps) {
  const [code, setCode] = useState('');
  const [error, setError] = useState(false);
  const [shake, setShake] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (code === SECRET_CODE) {
      setError(false);
      onGranted();
    } else {
      setAttempts(a => a + 1);
      setError(true);
      setShake(true);
      setCode('');
      setTimeout(() => setShake(false), 600);
    }
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      background: 'radial-gradient(ellipse at 30% 20%, rgba(59,130,246,0.12) 0%, transparent 60%), radial-gradient(ellipse at 70% 80%, rgba(34,197,94,0.08) 0%, transparent 60%), var(--bg-0)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      backdropFilter: 'blur(12px)',
    }}>
      {/* Ambient orbs */}
      <div style={{ position: 'absolute', top: '10%', left: '15%', width: 400, height: 400, background: 'rgba(59,130,246,0.06)', borderRadius: '50%', filter: 'blur(120px)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', bottom: '15%', right: '10%', width: 350, height: 350, background: 'rgba(34,197,94,0.05)', borderRadius: '50%', filter: 'blur(100px)', pointerEvents: 'none' }} />

      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.96 }}
        animate={shake ? { x: [-12, 12, -8, 8, -4, 4, 0] } : { opacity: 1, y: 0, scale: 1 }}
        transition={shake ? { duration: 0.5 } : { duration: 0.5, ease: 'easeOut' }}
        style={{
          width: '100%', maxWidth: '460px', margin: '0 24px',
          background: 'rgba(255,255,255,0.04)',
          border: error ? '1px solid rgba(239,68,68,0.4)' : '1px solid rgba(255,255,255,0.08)',
          borderRadius: '20px',
          padding: '48px 40px',
          backdropFilter: 'blur(24px)',
          boxShadow: error
            ? '0 0 0 1px rgba(239,68,68,0.2), 0 32px 80px rgba(0,0,0,0.5)'
            : '0 32px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.04)',
          transition: 'border-color 0.3s, box-shadow 0.3s',
          position: 'relative',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '36px' }}>
          <motion.div
            animate={{ rotate: [0, -5, 5, -3, 3, 0] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 4 }}
            style={{
              width: 72, height: 72, borderRadius: '50%',
              background: 'linear-gradient(135deg, rgba(59,130,246,0.15), rgba(34,197,94,0.1))',
              border: '1px solid rgba(59,130,246,0.25)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 24px',
            }}
          >
            <KeyRound size={30} color="#60a5fa" />
          </motion.div>

          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '4px 14px',
            background: 'rgba(59,130,246,0.1)',
            border: '1px solid rgba(59,130,246,0.2)',
            borderRadius: 100, marginBottom: 20,
          }}>
            <ShieldCheck size={12} color="#3b82f6" />
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#60a5fa', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
              Restricted Access
            </span>
          </div>

          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: 12, letterSpacing: '-0.03em' }}
              className="display-font">
            Enter Access Code
          </h2>
          <p style={{ color: 'var(--text-3)', fontSize: '0.9rem', lineHeight: 1.7 }}>
            This platform is restricted to authorised personnel. Enter your secret access code to continue.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ position: 'relative' }}>
            <input
              ref={inputRef}
              type="password"
              value={code}
              onChange={e => { setCode(e.target.value); setError(false); }}
              placeholder="Enter secret code…"
              autoComplete="off"
              style={{
                width: '100%',
                padding: '14px 18px',
                background: 'rgba(255,255,255,0.05)',
                border: error ? '1px solid rgba(239,68,68,0.6)' : '1px solid rgba(255,255,255,0.1)',
                borderRadius: 12,
                color: 'var(--text-1)',
                fontSize: '1rem',
                letterSpacing: '0.15em',
                outline: 'none',
                transition: 'border-color 0.2s',
                boxSizing: 'border-box',
              }}
            />
          </div>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  padding: '10px 14px',
                  background: 'rgba(239,68,68,0.08)',
                  border: '1px solid rgba(239,68,68,0.2)',
                  borderRadius: 10,
                  color: '#f87171', fontSize: '0.85rem',
                }}
              >
                <AlertTriangle size={15} />
                Incorrect code{attempts > 1 ? ` (${attempts} attempts)` : ''}. Please try again.
              </motion.div>
            )}
          </AnimatePresence>

          <button
            type="submit"
            className="btn btn-secondary"
            style={{ width: '100%', padding: '14px', fontSize: '0.95rem', fontWeight: 700, marginTop: 4, cursor: 'pointer' }}
          >
            Unlock Platform →
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 24, fontSize: '0.78rem', color: 'var(--text-3)' }}>
          Don't have an access code?{' '}
          <a href="mailto:oladeji.lawrence@gmail.com" style={{ color: '#60a5fa', textDecoration: 'none' }}>
            Request access →
          </a>
        </p>
      </motion.div>
    </div>
  );
}
