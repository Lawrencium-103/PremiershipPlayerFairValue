import { Link } from 'react-router-dom'

const STATS = [
  { value: '12,541', label: 'Transfers Analysed' },
  { value: '£638k',  label: 'Model MAE'          },
  { value: '17',     label: 'Features Learned'   },
  { value: '3-Axis', label: 'Live Intelligence'  },
]

const FEATURES = [
  {
    icon: '🧠',
    title: 'XGBoost + SHAP',
    desc: 'Decomposes every valuation into raw talent vs. age & contract depreciation — in pounds, not abstract scores.',
  },
  {
    icon: '📰',
    title: 'Live Market Intelligence',
    desc: 'Real-time NLP sentiment across injury news, form data, and agent noise adjusts the hard cap before you bid.',
  },
  {
    icon: '⚖️',
    title: 'PSR Compliance',
    desc: 'Instantly models the full amortisation schedule and flags breaches against the £105m 3-year Premier League limit.',
  },
]

const STEPS = [
  { n: '01', title: 'Profile the Target',   desc: 'Enter age, contract status, injury history, and market value estimate.' },
  { n: '02', title: 'AI Runs the Numbers',  desc: 'XGBoost + SHAP deconstructs talent from depreciation. Live news sentiment adjusts the hard cap.' },
  { n: '03', title: 'Receive a Hard Cap',   desc: 'A defensible, board-ready maximum bid with full mathematical transparency.' },
]

export default function Landing() {
  return (
    <div className="page">

      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <section className="container" style={{ textAlign:'center', padding:'60px 24px 48px' }}>
        <div className="animate-in">
          <span className="badge badge-green" style={{ marginBottom:20, display:'inline-flex' }}>
            Powered by XGBoost + SHAP Explainability
          </span>
          <h1 style={{ marginBottom:20 }}>
            The AI That Protects Clubs From<br/>
            <span className="gradient-text">Winner's Curse</span>
          </h1>
          <p style={{ maxWidth:580, margin:'0 auto 36px', fontSize:'1.05rem', lineHeight:1.75 }}>
            A rigorous, data-driven transfer ceiling calculator grounded in ML and
            Hedonic Pricing Theory — built for Directors of Football who can't afford
            to overpay.
          </p>
          <div style={{ display:'flex', gap:12, justifyContent:'center', flexWrap:'wrap' }}>
            <Link to="/estimate" className="btn btn-primary btn-lg">
              Evaluate a Transfer ↗
            </Link>
            <Link to="/ffp" className="btn btn-ghost btn-lg">
              Check PSR Compliance
            </Link>
          </div>
        </div>
      </section>

      {/* ── Stats Bar ─────────────────────────────────────────────────────── */}
      <section style={{ borderTop:'1px solid var(--glass-border)', borderBottom:'1px solid var(--glass-border)', padding:'28px 0', marginBottom:64 }}>
        <div className="container">
          <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:16, textAlign:'center' }}>
            {STATS.map(({ value, label }) => (
              <div key={label}>
                <div style={{ fontSize:'2rem', fontWeight:800, letterSpacing:'-0.03em', color:'var(--green)' }}>{value}</div>
                <div style={{ fontSize:'0.78rem', color:'var(--text-2)', textTransform:'uppercase', letterSpacing:'0.07em', fontWeight:600 }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────────────── */}
      <section className="container" style={{ marginBottom:72 }}>
        <h2 style={{ textAlign:'center', marginBottom:12 }}>Built for the Transfer Room</h2>
        <p style={{ textAlign:'center', marginBottom:40, maxWidth:520, margin:'0 auto 40px' }}>
          Every output is explainable, auditable, and defensible to a board.
        </p>
        <div className="grid-3">
          {FEATURES.map(({ icon, title, desc }) => (
            <div key={title} className="glass" style={{ padding:28 }}>
              <div style={{ fontSize:'2.2rem', marginBottom:14 }}>{icon}</div>
              <h3 style={{ marginBottom:10 }}>{title}</h3>
              <p style={{ fontSize:'0.88rem', lineHeight:1.7 }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────────────────────── */}
      <section className="container" style={{ marginBottom:80 }}>
        <h2 style={{ textAlign:'center', marginBottom:48 }}>How It Works</h2>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:24, position:'relative' }}>
          {/* Connector line */}
          <div style={{
            position:'absolute', top:28, left:'17%', width:'66%', height:1,
            background:'linear-gradient(90deg,var(--green),var(--blue))',
            opacity:0.3,
          }} />
          {STEPS.map(({ n, title, desc }) => (
            <div key={n} style={{ textAlign:'center' }}>
              <div style={{
                width:54, height:54, borderRadius:'50%',
                background:'linear-gradient(135deg,var(--green-dim),var(--blue-dim))',
                border:'1px solid var(--glass-border)',
                display:'flex', alignItems:'center', justifyContent:'center',
                margin:'0 auto 18px',
                fontWeight:800, fontSize:'1rem', color:'var(--green)',
              }}>{n}</div>
              <h3 style={{ marginBottom:8 }}>{title}</h3>
              <p style={{ fontSize:'0.85rem' }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────────────────────── */}
      <section className="container">
        <div className="glass" style={{
          padding:'48px 40px', textAlign:'center',
          background:'linear-gradient(135deg, rgba(0,232,122,0.05), rgba(79,142,247,0.05))',
          borderColor:'rgba(0,232,122,0.15)',
        }}>
          <h2 style={{ marginBottom:12 }}>Ready to protect the budget?</h2>
          <p style={{ marginBottom:28 }}>Run your first player evaluation in under 60 seconds.</p>
          <Link to="/estimate" className="btn btn-primary btn-lg" style={{ animation:'pulse-ring 2s infinite' }}>
            Start Evaluating →
          </Link>
        </div>
      </section>
    </div>
  )
}
