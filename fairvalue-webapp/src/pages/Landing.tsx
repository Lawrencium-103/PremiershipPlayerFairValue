import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BrainCircuit, Activity, ShieldCheck, ArrowRight, TrendingUp } from 'lucide-react'

const STATS = [
  { value: '12,541', label: 'Transfers Analysed' },
  { value: '£638k',  label: 'Model Accuracy (MAE)' },
  { value: '3-Axis', label: 'Live NLP Intelligence'  },
  { value: '100%',   label: 'PSR Compliance' },
]

export default function Landing() {
  return (
    <div className="page" style={{ overflow: 'hidden' }}>

      {/* ── Cinematic Hero ────────────────────────────────────────────────── */}
      <section className="container" style={{ textAlign: 'center', padding: '80px 24px 60px' }}>
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '24px', padding: '6px 16px', background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: '100px' }}>
            <BrainCircuit size={16} color="#3b82f6" />
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#60a5fa', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              XGBoost + SHAP Enterprise Grade
            </span>
          </div>

          <h1 style={{ marginBottom: '24px' }}>
            Protect Your Transfer Budget <br/>
            From <span className="gradient-accent">Winner's Curse</span>
          </h1>

          <p style={{ maxWidth: '640px', margin: '0 auto 40px', fontSize: '1.15rem', lineHeight: 1.8, color: 'var(--text-2)' }}>
            A rigorous, data-driven transfer ceiling calculator grounded in Machine Learning and Hedonic Pricing Theory. Designed exclusively for Directors of Football who cannot afford to overpay.
          </p>

          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/estimate" className="btn btn-secondary btn-lg">
              Launch Intelligence Engine <ArrowRight size={18} />
            </Link>
            <Link to="/ffp" className="btn btn-ghost btn-lg">
              Calculate PSR Impact
            </Link>
          </div>
        </motion.div>
      </section>

      {/* ── Financial Stats ───────────────────────────────────────────────── */}
      <section style={{ borderTop: '1px solid var(--glass-border)', borderBottom: '1px solid var(--glass-border)', padding: '40px 0', marginBottom: '80px', background: 'rgba(255,255,255,0.01)' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '24px', textAlign: 'center' }}>
            {STATS.map(({ value, label }, i) => (
              <motion.div 
                key={label}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 + (i * 0.1) }}
              >
                <div style={{ fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-0.04em', color: 'var(--text-1)', fontFamily: 'Outfit' }}>{value}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>{label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Value Proposition Cards ───────────────────────────────────────── */}
      <section className="container" style={{ marginBottom: '100px' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h2 style={{ marginBottom: '16px' }}>Built for the Transfer Room</h2>
          <p style={{ maxWidth: '580px', margin: '0 auto' }}>Every output is transparent, mathematically auditable, and instantly defensible to your executive board.</p>
        </div>

        <div className="grid-3">
          <motion.div whileHover={{ y: -5 }} className="glass" style={{ padding: '32px' }}>
            <BrainCircuit size={32} color="#3b82f6" style={{ marginBottom: '20px' }} />
            <h3 style={{ marginBottom: '12px' }}>SHAP Talent Isolation</h3>
            <p style={{ fontSize: '0.9rem' }}>Decomposes every player's valuation into pure intrinsic performance metrics vs. age/contract depreciation traps.</p>
          </motion.div>

          <motion.div whileHover={{ y: -5 }} className="glass" style={{ padding: '32px' }}>
            <Activity size={32} color="#f5a623" style={{ marginBottom: '20px' }} />
            <h3 style={{ marginBottom: '12px' }}>Live NLP Intelligence</h3>
            <p style={{ fontSize: '0.9rem' }}>Real-time sentiment scraping across durability risks, recent form, and agent noise instantly adjusts your ceiling bid.</p>
          </motion.div>

          <motion.div whileHover={{ y: -5 }} className="glass" style={{ padding: '32px' }}>
            <ShieldCheck size={32} color="#22c55e" style={{ marginBottom: '20px' }} />
            <h3 style={{ marginBottom: '12px' }}>PSR Board Compliance</h3>
            <p style={{ fontSize: '0.9rem' }}>Instantly model the 5-year amortisation hit and guard against £105m Premier League breaches before you sign the contract.</p>
          </motion.div>
        </div>
      </section>

      {/* ── Enterprise CTA ────────────────────────────────────────────────── */}
      <section className="container">
        <motion.div 
          whileInView={{ opacity: 1, scale: 1 }}
          initial={{ opacity: 0, scale: 0.95 }}
          viewport={{ once: true }}
          className="glass" 
          style={{
            padding: '60px 48px', textAlign: 'center',
            background: 'linear-gradient(135deg, rgba(34,197,94,0.05), rgba(59,130,246,0.08))',
            borderColor: 'var(--glass-border-hi)',
            position: 'relative', overflow: 'hidden'
          }}
        >
          <div style={{ position: 'absolute', top: '-50%', left: '-20%', width: '400px', height: '400px', background: 'var(--accent-blue)', filter: 'blur(200px)', opacity: 0.15, pointerEvents: 'none' }} />
          <h2 style={{ marginBottom: '16px' }}>Ready to optimize your net spend?</h2>
          <p style={{ marginBottom: '32px', color: 'var(--text-2)' }}>Experience the ML model. Restrictive access applies for unverified guests.</p>
          <Link to="/estimate" className="btn btn-secondary btn-lg">
            Commence Target Profiling <TrendingUp size={20} style={{ marginLeft: 8 }} />
          </Link>
        </motion.div>
      </section>

    </div>
  )
}
