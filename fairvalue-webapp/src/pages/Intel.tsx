import { useState } from 'react'
import { motion } from 'framer-motion'
import { useUsageLimiter } from '../hooks/useUsageLimiter'
import AccessModal from '../components/AccessModal'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface ScoutResult {
  player: string
  durability: number
  recency: number
  agent: number
  logs: string[]
  from_cache: boolean
}

function ScoreCard({
  label, value, icon, desc,
}: { label: string; value: number; icon: string; desc: string }) {
  const norm  = (value + 1) / 2             // –1..+1 → 0..1
  const pct   = Math.round(norm * 100)
  const color = value > 0.1 ? 'var(--green)' : value < -0.1 ? 'var(--red)' : 'var(--blue)'
  const label2 = value > 0.15 ? 'Positive' : value < -0.15 ? 'Negative' : 'Neutral'
  const badge  = value > 0.15 ? 'badge-green' : value < -0.15 ? 'badge-red' : 'badge-blue'

  return (
    <div className="glass" style={{ padding:24 }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:14 }}>
        <div>
          <div style={{ fontSize:'1.6rem', marginBottom:4 }}>{icon}</div>
          <h3 style={{ marginBottom:2 }}>{label}</h3>
          <p style={{ fontSize:'0.78rem', lineHeight:1.5 }}>{desc}</p>
        </div>
        <div style={{ textAlign:'right' }}>
          <div style={{ fontSize:'2rem', fontWeight:900, color, letterSpacing:'-0.03em', lineHeight:1 }}>
            {value > 0 ? '+' : ''}{value.toFixed(2)}
          </div>
          <span className={`badge ${badge}`} style={{ marginTop:6 }}>{label2}</span>
        </div>
      </div>
      {/* Bar */}
      <div style={{ position:'relative', height:8, borderRadius:4, background:'var(--bg-elevated-2)', overflow:'hidden' }}>
        {/* Neutral marker at 50% */}
        <div style={{ position:'absolute', left:'50%', top:0, width:1, height:'100%', background:'rgba(255,255,255,0.15)', zIndex:1 }}/>
        <div style={{
          position:'absolute',
          left: value >= 0 ? '50%' : `${pct}%`,
          width: `${Math.abs(value) * 50}%`,
          height:'100%', borderRadius:4,
          background: color,
          transition:'all 0.5s cubic-bezier(0.4,0,0.2,1)',
        }}/>
      </div>
      <div style={{ display:'flex', justifyContent:'space-between', marginTop:4 }}>
        <span style={{ fontSize:'0.68rem', color:'var(--text-3)' }}>−1.0 Negative</span>
        <span style={{ fontSize:'0.68rem', color:'var(--text-3)' }}>+1.0 Positive</span>
      </div>
    </div>
  )
}

function HypeFactorDisplay({ durability, recency, agent }: { durability: number; recency: number; agent: number }) {
  // Mirror the tier logic from api/main.py but use a generic baseline
  const dur_adj  = Math.min(0.0, durability) * 0.15
  const rec_adj  = Math.max(0.0, recency)    * 0.25   // Elite ceiling assumed
  const agt_adj  = Math.min(0.0, agent)      * 0.05
  const mult     = 1.0 + rec_adj + dur_adj + agt_adj
  const pct      = ((mult - 1) * 100).toFixed(1)
  const isPos    = mult >= 1

  return (
    <div className="glass" style={{
      padding:24,
      background: isPos ? 'var(--green-dim)' : 'var(--red-dim)',
      borderColor: isPos ? 'rgba(0,232,122,0.2)' : 'rgba(255,77,109,0.2)',
    }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <div>
          <div className="metric-label" style={{ marginBottom:4 }}>🔥 Derived Hype Factor</div>
          <p style={{ fontSize:'0.8rem', maxWidth:380 }}>
            NLP multiplier applied to the ML baseline in the Transfer Estimator.
            Computed from weighted sentiment across all three axes.
          </p>
        </div>
        <div style={{ textAlign:'right' }}>
          <div style={{ fontSize:'2.8rem', fontWeight:900, color: isPos ? 'var(--green)' : 'var(--red)', letterSpacing:'-0.04em' }}>
            ×{mult.toFixed(3)}
          </div>
          <div style={{ fontSize:'0.82rem', color: isPos ? 'var(--green)' : 'var(--red)', fontWeight:600 }}>
            {isPos ? `+${pct}% sentiment premium` : `${pct}% sentiment discount`}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Intel() {
  const { isLocked, incrementUsage } = useUsageLimiter()
  const [player,        setPlayer]        = useState('')
  const [club,          setClub]          = useState('')
  const [result,        setResult]        = useState<ScoutResult | null>(null)
  const [loading,       setLoading]       = useState(false)
  const [error,         setError]         = useState<string | null>(null)
  const [showLog,       setShowLog]       = useState(false)

  const handleFetch = async () => {
    if (!incrementUsage()) return;
    if (!player.trim()) { setError('Enter a player name first.'); return }
    setLoading(true); setError(null); setResult(null)
    try {
      const params = new URLSearchParams({ player: player.trim(), club: club.trim() })
      const res = await fetch(`${API_URL}/api/scout?${params}`)
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `API error ${res.status}`)
      }
      setResult(await res.json())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch intel.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page" style={{ position: 'relative' }}>
      {isLocked && <AccessModal />}
      <motion.div 
        className="container"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >

        {/* Header */}
        <div style={{ marginBottom:36 }}>
          <span className="badge badge-gold" style={{ marginBottom:10, display:'inline-flex' }}>Live Intelligence</span>
          <h1 style={{ marginBottom:8 }}>🔍 Live Player Intel</h1>
          <p>Scrape real-time news across three NLP axes to compute the market sentiment multiplier before bidding.</p>
        </div>

        {/* Search card */}
        <div className="glass-flat" style={{ padding:28, marginBottom:24 }}>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr auto', gap:12, alignItems:'flex-end' }}>
            <div className="input-group">
              <label className="field-label">Player Name *</label>
              <input className="input" placeholder="e.g. Jude Bellingham"
                value={player} onChange={e => setPlayer(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleFetch()}/>
            </div>
            <div className="input-group">
              <label className="field-label">Current Club (optional)</label>
              <input className="input" placeholder="e.g. Real Madrid"
                value={club} onChange={e => setClub(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleFetch()}/>
            </div>
            <button className="btn btn-primary" style={{ height:42 }}
              onClick={handleFetch} disabled={loading}>
              {loading ? <><span className="spinner"/> Scraping…</> : '⚡ Fetch Intel'}
            </button>
          </div>
          {error && <div className="alert alert-danger" style={{ marginTop:14 }}>{error}</div>}
          <p style={{ fontSize:'0.72rem', color:'var(--text-3)', marginTop:12 }}>
            ℹ️ First request per player takes 15–30 seconds (live DDGS scrape). Subsequent requests within 1 hour are instant (cached).
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="glass" style={{ padding:48, textAlign:'center' }}>
            <div className="spinner" style={{ width:40, height:40, margin:'0 auto 20px' }}/>
            <p>Scraping live transfer news, injury reports, and agent whispers…</p>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="animate-in" style={{ display:'flex', flexDirection:'column', gap:18 }}>

            {/* Cache badge */}
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
              <h2>{result.player}</h2>
              <span className={`badge ${result.from_cache ? 'badge-blue' : 'badge-green'}`}>
                {result.from_cache ? '⚡ Cached (< 1hr)' : '🔴 Live Scraped'}
              </span>
            </div>

            {/* Hype Factor */}
            <HypeFactorDisplay
              durability={result.durability}
              recency={result.recency}
              agent={result.agent}
            />

            {/* Three score cards */}
            <div className="grid-3">
              <ScoreCard
                icon="🏥" label="Durability"
                value={result.durability}
                desc="Based on injury reports, games missed, and fitness news. Negative = active concerns."
              />
              <ScoreCard
                icon="📈" label="Recent Form"
                value={result.recency}
                desc="Based on match ratings, goal/assist data, and performance commentary."
              />
              <ScoreCard
                icon="🗞️" label="Transfer Heat"
                value={result.agent}
                desc="Based on rumour intensity, agent activity, and bid speculation volume."
              />
            </div>

            {/* Methodology note */}
            <div className="glass" style={{ padding:20 }}>
              <h4 style={{ marginBottom:8 }}>Methodology</h4>
              <p style={{ fontSize:'0.8rem', lineHeight:1.7 }}>
                Sentiment is derived from TextBlob polarity analysis applied to DDGS (DuckDuckGo) 
                search snippets scraped in real time. Scores range from −1.0 (very negative) to 
                +1.0 (very positive). The Hype Factor multiplier is then applied to the XGBoost 
                ML baseline in the Transfer Estimator to compute the PSR hard cap.
              </p>
            </div>

            {/* Recon log */}
            <div>
              <button className="btn btn-ghost" style={{ fontSize:'0.78rem', padding:'6px 14px' }}
                onClick={() => setShowLog(!showLog)}>
                {showLog ? '▲ Hide' : '▼ Show'} Raw Recon Log ({result.logs.length} entries)
              </button>
              {showLog && (
                <div style={{ marginTop:10, background:'var(--bg-elevated-2)', borderRadius:8, padding:'12px 14px' }}>
                  {result.logs.length === 0
                    ? <span style={{ color:'var(--text-3)', fontSize:'0.78rem' }}>No log entries.</span>
                    : result.logs.map((l, i) => (
                      <div key={i} style={{ fontSize:'0.75rem', color:'var(--text-2)', padding:'4px 0', borderBottom:'1px solid var(--glass-border)' }}>{l}</div>
                    ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Empty state */}
        {!result && !loading && !error && (
          <div className="glass" style={{ padding:56, textAlign:'center', color:'var(--text-3)' }}>
            <div style={{ fontSize:'3rem', marginBottom:16 }}>🔍</div>
            <p>Enter a player name above and click Fetch Intel.</p>
          </div>
        )}
      </motion.div>
    </div>
  )
}
