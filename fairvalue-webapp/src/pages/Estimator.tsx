import { useState } from 'react'
import {
  BarChart, Bar, Cell, XAxis, YAxis, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ── Types ─────────────────────────────────────────────────────────────────────
interface Ledger {
  intrinsic_performance_value: number
  category: string
  depreciation: number
  baseline_value: number
  external_multiplier: number
  hard_cap: number
}
interface EvalResult {
  ledger: Ledger
  nlp_results: { durability: number; recency: number; agent: number }
  nlp_cached: boolean
  logs: string[]
  shap_data: { feature: string; impact: number }[]
}

// ── Gauge (SVG speedometer) ────────────────────────────────────────────────────
function Gauge({ asking, hardCap }: { asking: number; hardCap: number }) {
  const maxVal = Math.max(asking * 1.25, hardCap * 1.25, 50)
  const cx = 150, cy = 138, r = 108

  const toRad = (deg: number) => (deg * Math.PI) / 180
  const pt = (deg: number) => ({
    x: cx + r * Math.cos(toRad(deg)),
    y: cy + r * Math.sin(toRad(deg)),
  })

  const frac = (v: number) => Math.min(v / maxVal, 1)
  const capDeg  = -180 + frac(hardCap) * 180
  const askDeg  = -180 + frac(asking)  * 180
  const isOver  = asking > hardCap

  const arc = (a1: number, a2: number) => {
    const s = pt(a1), e = pt(a2)
    const large = a2 - a1 > 180 ? 1 : 0
    return `M ${s.x.toFixed(1)} ${s.y.toFixed(1)} A ${r} ${r} 0 ${large} 1 ${e.x.toFixed(1)} ${e.y.toFixed(1)}`
  }

  return (
    <svg viewBox="0 0 300 165" style={{ width:'100%', maxWidth:320 }}>
      {/* Track */}
      <path d={arc(-180,0)} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={18} strokeLinecap="round"/>
      {/* Green zone: 0 → cap */}
      <path d={arc(-180, capDeg)} fill="none" stroke="var(--green)" strokeWidth={18} strokeLinecap="round" opacity={0.85}/>
      {/* Red zone: cap → asking (only if over) */}
      {isOver && (
        <path d={arc(capDeg, Math.min(askDeg, 0))} fill="none" stroke="var(--red)" strokeWidth={18} strokeLinecap="round" opacity={0.85}/>
      )}
      {/* Needle */}
      <line x1={cx} y1={cy} x2={pt(askDeg).x} y2={pt(askDeg).y} stroke="white" strokeWidth={2.5} strokeLinecap="round"/>
      <circle cx={cx} cy={cy} r={5} fill="white"/>
      {/* Cap label */}
      <text x={pt(capDeg).x + (capDeg < -90 ? -6 : 6)} y={pt(capDeg).y - 6}
        textAnchor={capDeg < -90 ? 'end' : 'start'}
        fill="var(--green)" fontSize={9} fontWeight={600}>
        Hard Cap £{hardCap.toFixed(0)}m
      </text>
      {/* Center: asking */}
      <text x={cx} y={cy + 22} textAnchor="middle" fill="white" fontSize={22} fontWeight={800}>
        £{asking.toFixed(0)}m
      </text>
      <text x={cx} y={cy + 40} textAnchor="middle"
        fill={isOver ? 'var(--red)' : 'var(--green)'} fontSize={12} fontWeight={600}>
        {isOver
          ? `▲ £${(asking - hardCap).toFixed(1)}m OVER CAP`
          : `✓ Within Hard Cap`}
      </text>
      {/* Scale ticks */}
      {[0, 0.25, 0.5, 0.75, 1].map(f => {
        const deg = -180 + f * 180
        const inner = { x: cx + (r-12) * Math.cos(toRad(deg)), y: cy + (r-12) * Math.sin(toRad(deg)) }
        const outer = { x: cx + (r+2)  * Math.cos(toRad(deg)), y: cy + (r+2)  * Math.sin(toRad(deg)) }
        return <line key={f} x1={inner.x} y1={inner.y} x2={outer.x} y2={outer.y} stroke="rgba(255,255,255,0.15)" strokeWidth={1}/>
      })}
    </svg>
  )
}

// ── SHAP Chart ────────────────────────────────────────────────────────────────
function ShapChart({ data }: { data: { feature: string; impact: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} layout="vertical" margin={{ left: 0, right: 24, top: 4, bottom: 4 }}>
        <XAxis type="number" tick={{ fill:'var(--text-2)', fontSize:10 }} axisLine={false} tickLine={false}/>
        <YAxis type="category" dataKey="feature" tick={{ fill:'var(--text-2)', fontSize:11 }} width={140} axisLine={false} tickLine={false}/>
        <Tooltip
          cursor={{ fill:'rgba(255,255,255,0.04)' }}
          contentStyle={{ background:'var(--bg-elevated)', border:'1px solid var(--glass-border)', borderRadius:8, fontSize:12 }}
          formatter={(v: number) => [v > 0 ? `+${v.toFixed(3)}` : v.toFixed(3), 'SHAP Impact']}
        />
        <ReferenceLine x={0} stroke="rgba(255,255,255,0.12)" strokeWidth={1}/>
        <Bar dataKey="impact" radius={3}>
          {data.map((entry, i) => (
            <Cell key={i} fill={entry.impact >= 0 ? 'var(--green)' : 'var(--red)'} fillOpacity={0.85}/>
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

// ── NLP Sentiment Score ───────────────────────────────────────────────────────
function SentimentScore({ label, value, icon }: { label: string; value: number; icon: string }) {
  const pct = Math.round(((value + 1) / 2) * 100)
  const color = value > 0.1 ? 'var(--green)' : value < -0.1 ? 'var(--red)' : 'var(--blue)'
  return (
    <div>
      <div style={{ display:'flex', justifyContent:'space-between', marginBottom:6 }}>
        <span style={{ fontSize:'0.8rem', color:'var(--text-2)', display:'flex', gap:6, alignItems:'center' }}>
          {icon} {label}
        </span>
        <span style={{ fontSize:'0.8rem', fontWeight:700, color }}>{value > 0 ? '+' : ''}{value.toFixed(2)}</span>
      </div>
      <div className="sentiment-bar-track">
        <div className="sentiment-bar-fill" style={{ width:`${pct}%`, background:color }}/>
      </div>
    </div>
  )
}

// ── Main Estimator Page ───────────────────────────────────────────────────────
export default function Estimator() {
  const [form, setForm] = useState({
    selected_name: '',
    current_club: '',
    interested_club: '',
    contract_years: 3,
    age: 24,
    injuries_24m: 10,
    asking_price: 45,
    market_value_estimation: 40,
  })
  const [result, setResult]   = useState<EvalResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)
  const [showLog, setShowLog] = useState(false)

  const set = (k: string, v: string | number) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async () => {
    if (!form.selected_name.trim()) { setError('Player name is required.'); return }
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await fetch(`${API_URL}/api/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `API error ${res.status}`)
      }
      setResult(await res.json())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error — is the API running?')
    } finally {
      setLoading(false)
    }
  }

  const L = result?.ledger

  return (
    <div className="page">
      <div className="container">

        {/* Header */}
        <div style={{ marginBottom:36 }}>
          <span className="badge badge-green" style={{ marginBottom:10, display:'inline-flex' }}>AI Valuation Engine</span>
          <h1 style={{ marginBottom:8 }}>Strategic Transfer Estimator</h1>
          <p>Evaluate a transfer ceiling guided by ML valuations and multi-axis NLP intelligence.</p>
        </div>

        <div style={{ display:'grid', gridTemplateColumns:'380px 1fr', gap:24, alignItems:'start' }}>

          {/* ── Left: Form ────────────────────────────────────────────────── */}
          <div style={{ display:'flex', flexDirection:'column', gap:16 }}>

            <div className="glass-flat" style={{ padding:24 }}>
              <h3 style={{ marginBottom:20, color:'var(--text-1)' }}>Player Profile</h3>

              <div style={{ display:'flex', flexDirection:'column', gap:14 }}>
                <div className="input-group">
                  <label className="field-label">Player Name *</label>
                  <input className="input" placeholder="e.g. Jude Bellingham"
                    value={form.selected_name}
                    onChange={e => set('selected_name', e.target.value)}/>
                  <small style={{ fontSize:'0.7rem', color:'var(--text-3)' }}>
                    Use the Transfermarkt name for best accuracy.
                  </small>
                </div>

                <div className="grid-2">
                  <div className="input-group">
                    <label className="field-label">Current Club</label>
                    <input className="input" placeholder="Real Madrid"
                      value={form.current_club}
                      onChange={e => set('current_club', e.target.value)}/>
                  </div>
                  <div className="input-group">
                    <label className="field-label">Buying Club</label>
                    <input className="input" placeholder="Arsenal"
                      value={form.interested_club}
                      onChange={e => set('interested_club', e.target.value)}/>
                  </div>
                </div>
              </div>
            </div>

            <div className="glass-flat" style={{ padding:24 }}>
              <h3 style={{ marginBottom:20 }}>Financial Parameters</h3>
              <div style={{ display:'flex', flexDirection:'column', gap:18 }}>

                {/* Contract Years */}
                <div className="input-group">
                  <label className="field-label">
                    Contract Years Remaining
                    <span className="range-val" style={{ float:'right' }}>{form.contract_years}yr</span>
                  </label>
                  <input type="range" min={0.5} max={7} step={0.5}
                    value={form.contract_years}
                    onChange={e => set('contract_years', parseFloat(e.target.value))}/>
                  <div className="range-row"><span>0.5yr</span><span>7yr</span></div>
                </div>

                {/* Age */}
                <div className="input-group">
                  <label className="field-label">
                    Age
                    <span className="range-val" style={{ float:'right' }}>{form.age}</span>
                  </label>
                  <input type="range" min={16} max={40} step={1}
                    value={form.age}
                    onChange={e => set('age', parseInt(e.target.value))}/>
                  <div className="range-row"><span>16</span><span>40</span></div>
                </div>

                {/* Injury days */}
                <div className="input-group">
                  <label className="field-label">Injury Days (last 24m)</label>
                  <input type="number" className="input" min={0} max={730}
                    value={form.injuries_24m}
                    onChange={e => set('injuries_24m', parseInt(e.target.value)||0)}/>
                </div>

                {/* Market value */}
                <div className="input-group">
                  <label className="field-label">Current Market Value (£m)</label>
                  <input type="number" className="input" min={0.1} step={0.5}
                    value={form.market_value_estimation}
                    onChange={e => set('market_value_estimation', parseFloat(e.target.value)||0)}/>
                </div>

                {/* Asking price */}
                <div className="input-group">
                  <label className="field-label">Selling Club Asking Price (£m)</label>
                  <input type="number" className="input" min={0.1} step={0.5}
                    value={form.asking_price}
                    onChange={e => set('asking_price', parseFloat(e.target.value)||0)}/>
                </div>
              </div>
            </div>

            <button className="btn btn-primary" style={{ width:'100%', justifyContent:'center', padding:14 }}
              onClick={handleSubmit} disabled={loading}>
              {loading
                ? <><span className="spinner"/> Fetching live intel… (15–30s)</>
                : '⚡ Calculate Hard Cap'}
            </button>

            {error && <div className="alert alert-danger">{error}</div>}
          </div>

          {/* ── Right: Results ────────────────────────────────────────────── */}
          <div>
            {!result && !loading && (
              <div className="glass" style={{ padding:48, textAlign:'center', color:'var(--text-3)' }}>
                <div style={{ fontSize:'3rem', marginBottom:16 }}>📊</div>
                <p>Results will appear here after evaluation.</p>
              </div>
            )}

            {loading && (
              <div className="glass" style={{ padding:48, textAlign:'center' }}>
                <div className="spinner" style={{ width:40, height:40, margin:'0 auto 20px' }}/>
                <p>Running ML inference + scraping live market signals…</p>
                <p style={{ fontSize:'0.8rem', color:'var(--text-3)', marginTop:8 }}>
                  Live DDGS intel can take 15–30 seconds first time.
                </p>
              </div>
            )}

            {result && L && (
              <div className="animate-in" style={{ display:'flex', flexDirection:'column', gap:18 }}>

                {/* Verdict alert */}
                <div className={`alert ${form.asking_price > L.hard_cap ? 'alert-danger' : 'alert-success'}`}>
                  {form.asking_price > L.hard_cap
                    ? `⚠️ OVERPAY RISK — Asking price £${form.asking_price}m exceeds our hard cap of £${L.hard_cap.toFixed(1)}m by £${(form.asking_price - L.hard_cap).toFixed(1)}m.`
                    : `✅ FAIR DEAL — Asking price £${form.asking_price}m is within the £${L.hard_cap.toFixed(1)}m hard cap. Proceed with confidence.`}
                </div>

                {/* Gauge + Ledger */}
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:18 }}>
                  <div className="glass" style={{ padding:20, display:'flex', alignItems:'center', justifyContent:'center' }}>
                    <Gauge asking={form.asking_price} hardCap={L.hard_cap}/>
                  </div>

                  <div className="glass" style={{ padding:24 }}>
                    <h3 style={{ marginBottom:20 }}>XAI Valuation Ledger</h3>
                    <div style={{ display:'flex', flexDirection:'column', gap:16 }}>
                      <div>
                        <div className="metric-label">Intrinsic Performance Value</div>
                        <div className="metric-value" style={{ color:'var(--green)' }}>£{L.intrinsic_performance_value.toFixed(1)}m</div>
                        <span className="badge badge-green" style={{ marginTop:4 }}>{L.category}</span>
                      </div>
                      <div className="divider" style={{ margin:'8px 0' }}/>
                      <div>
                        <div className="metric-label">Age & Contract Depreciation</div>
                        <div className="metric-value" style={{ color: L.depreciation < 0 ? 'var(--red)' : 'var(--blue)' }}>
                          {L.depreciation >= 0 ? '+' : ''}£{L.depreciation.toFixed(1)}m
                        </div>
                        <span className="badge badge-blue" style={{ marginTop:4 }}>SHAP Calculated Penalty</span>
                      </div>
                      <div className="divider" style={{ margin:'8px 0' }}/>
                      <div>
                        <div className="metric-label">ML Baseline</div>
                        <div className="metric-value">£{L.baseline_value.toFixed(1)}m</div>
                      </div>
                      <div>
                        <div className="metric-label">NLP Multiplier</div>
                        <div className="metric-value" style={{ color: L.external_multiplier > 1 ? 'var(--green)' : 'var(--red)' }}>
                          ×{L.external_multiplier.toFixed(3)}
                        </div>
                      </div>
                      <div style={{ padding:'12px 14px', background:'var(--green-dim)', borderRadius:10, border:'1px solid rgba(0,232,122,0.2)' }}>
                        <div className="metric-label">🎯 Hard Cap</div>
                        <div style={{ fontSize:'2.2rem', fontWeight:900, color:'var(--green)', letterSpacing:'-0.03em' }}>
                          £{L.hard_cap.toFixed(1)}m
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* SHAP Chart */}
                <div className="glass" style={{ padding:24 }}>
                  <div style={{ marginBottom:14 }}>
                    <h3>SHAP Deep Dive — Top 10 Valuation Drivers</h3>
                    <p style={{ fontSize:'0.82rem', marginTop:4 }}>
                      Green = value driver. Red = value drag. Measured in log-price space.
                    </p>
                  </div>
                  <ShapChart data={result.shap_data}/>
                </div>

                {/* NLP Results */}
                <div className="glass" style={{ padding:24 }}>
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:18 }}>
                    <h3>Live Market Intelligence</h3>
                    {result.nlp_cached && <span className="badge badge-blue">Cached</span>}
                  </div>
                  <div style={{ display:'flex', flexDirection:'column', gap:14 }}>
                    <SentimentScore label="Injury / Availability"    icon="🏥" value={result.nlp_results.durability}/>
                    <SentimentScore label="Recent Form & Impact"     icon="📈" value={result.nlp_results.recency}/>
                    <SentimentScore label="Transfer Speculation"     icon="🗞️" value={result.nlp_results.agent}/>
                  </div>
                  <div style={{ marginTop:16 }}>
                    <button className="btn btn-ghost" style={{ fontSize:'0.78rem', padding:'6px 14px' }}
                      onClick={() => setShowLog(!showLog)}>
                      {showLog ? '▲ Hide' : '▼ Show'} Recon Log ({result.logs.length} entries)
                    </button>
                    {showLog && (
                      <div style={{ marginTop:12, background:'var(--bg-elevated-2)', borderRadius:8, padding:'12px 14px' }}>
                        {result.logs.map((l, i) => (
                          <div key={i} style={{ fontSize:'0.75rem', color:'var(--text-2)', padding:'3px 0', borderBottom:'1px solid var(--glass-border)' }}>{l}</div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
