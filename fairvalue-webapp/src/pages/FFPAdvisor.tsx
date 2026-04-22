import { useState } from 'react'
import {
  PieChart, Pie, Cell, Legend, Tooltip,
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer,
} from 'recharts'

// ── PSR Maths (all pure frontend — no API call) ────────────────────────────────
function calcPSR(feeMm: number, contractYrs: number, weeklyWageK: number, agentFeeMm: number) {
  const annualAmort    = feeMm / contractYrs
  const annualWage     = (weeklyWageK * 52) / 1000
  const annualAgent    = agentFeeMm / contractYrs
  const totalAnnual    = annualAmort + annualWage + annualAgent
  const totalContract  = feeMm + annualWage * contractYrs + agentFeeMm
  return { annualAmort, annualWage, annualAgent, totalAnnual, totalContract }
}

const DONUT_COLORS = ['#505070', '#4f8ef7', '#00e87a']

export default function FFPAdvisor() {
  const [feeMm,       setFeeMm]       = useState(50)
  const [contractYrs, setContractYrs] = useState(5)
  const [weeklyWageK, setWeeklyWageK] = useState(120)
  const [agentFeeMm,  setAgentFeeMm]  = useState(5)
  const [psrLossMm,   setPsrLossMm]   = useState(50)
  const [psrMaxMm,    setPsrMaxMm]    = useState(105)

  const { annualAmort, annualWage, annualAgent, totalAnnual, totalContract } =
    calcPSR(feeMm, contractYrs, weeklyWageK, agentFeeMm)

  const newPsrLoss   = psrLossMm + totalAnnual
  const psrRemaining = Math.max(psrMaxMm - newPsrLoss, 0)
  const isBreach     = newPsrLoss > psrMaxMm
  const overageM     = isBreach ? newPsrLoss - psrMaxMm : 0

  const donutData = [
    { name: 'Existing PSR Loss',  value: psrLossMm },
    { name: 'This Transfer (Yr1)', value: totalAnnual },
    { name: 'Remaining Allowance', value: psrRemaining },
  ]

  const years   = Array.from({ length: contractYrs }, (_, i) => `Yr ${i + 1}`)
  const barData = years.map(y => ({
    name: y,
    Amortisation: +annualAmort.toFixed(2),
    Wages:        +annualWage.toFixed(2),
    'Agent Fees': +annualAgent.toFixed(2),
  }))

  return (
    <div className="page">
      <div className="container">

        {/* Header */}
        <div style={{ marginBottom:36 }}>
          <span className="badge badge-blue" style={{ marginBottom:10, display:'inline-flex' }}>Regulatory Compliance Tool</span>
          <h1 style={{ marginBottom:8 }}>💼 PSR / Financial Fair Play Advisor</h1>
          <p>Model the precise P&L impact of any transfer on your 3-year Profitability &amp; Sustainability Rules allowance.</p>
        </div>

        <div style={{ display:'grid', gridTemplateColumns:'320px 1fr', gap:24, alignItems:'start' }}>

          {/* ── Left: Inputs ─────────────────────────────────────────────── */}
          <div style={{ display:'flex', flexDirection:'column', gap:16 }}>

            <div className="glass-flat" style={{ padding:24 }}>
              <h3 style={{ marginBottom:20 }}>Transfer Financials</h3>
              <div style={{ display:'flex', flexDirection:'column', gap:16 }}>

                <div className="input-group">
                  <label className="field-label">
                    Transfer Fee (£m)
                    <span className="range-val" style={{ float:'right' }}>£{feeMm}m</span>
                  </label>
                  <input type="range" min={1} max={300} step={1} value={feeMm} onChange={e => setFeeMm(+e.target.value)}/>
                  <div className="range-row"><span>£1m</span><span>£300m</span></div>
                </div>

                <div className="input-group">
                  <label className="field-label">
                    Contract Length (Years)
                    <span className="range-val" style={{ float:'right' }}>{contractYrs}yr</span>
                  </label>
                  <input type="range" min={1} max={7} step={1} value={contractYrs} onChange={e => setContractYrs(+e.target.value)}/>
                  <div className="range-row"><span>1yr</span><span>7yr</span></div>
                </div>

                <div className="input-group">
                  <label className="field-label">Weekly Wage (£k)</label>
                  <input type="number" className="input" min={5} max={1000} step={5}
                    value={weeklyWageK} onChange={e => setWeeklyWageK(+e.target.value)}/>
                </div>

                <div className="input-group">
                  <label className="field-label">Agent / Sign-on Fees (£m)</label>
                  <input type="number" className="input" min={0} max={50} step={0.5}
                    value={agentFeeMm} onChange={e => setAgentFeeMm(+e.target.value)}/>
                </div>
              </div>
            </div>

            <div className="glass-flat" style={{ padding:24 }}>
              <h3 style={{ marginBottom:20 }}>Club Economics</h3>
              <div style={{ display:'flex', flexDirection:'column', gap:16 }}>
                <div className="input-group">
                  <label className="field-label">Current 3-Yr PSR Loss (£m)</label>
                  <input type="number" className="input" min={0} max={200} step={5}
                    value={psrLossMm} onChange={e => setPsrLossMm(+e.target.value)}/>
                </div>
                <div className="input-group">
                  <label className="field-label">Max Allowed Loss (£m)</label>
                  <input type="number" className="input" min={0} max={200} step={5}
                    value={psrMaxMm} onChange={e => setPsrMaxMm(+e.target.value)}/>
                </div>
              </div>
            </div>
          </div>

          {/* ── Right: Results ────────────────────────────────────────────── */}
          <div style={{ display:'flex', flexDirection:'column', gap:18 }}>

            {/* Verdict */}
            <div className={`alert ${isBreach ? 'alert-danger' : 'alert-success'}`} style={{ fontSize:'0.95rem', fontWeight:600 }}>
              {isBreach
                ? `⚠️ BREACH RISK — This transfer pushes the club £${overageM.toFixed(1)}m over the £${psrMaxMm}m PSR limit in Year 1.`
                : `✅ COMPLIANT — The club remains £${psrRemaining.toFixed(1)}m under the £${psrMaxMm}m PSR limit.`}
            </div>

            {/* Summary metrics */}
            <div className="glass" style={{ padding:24 }}>
              <h3 style={{ marginBottom:20 }}>Financial Impact Summary</h3>
              <div className="grid-4" style={{ marginBottom:20 }}>
                <div className="metric">
                  <div className="metric-label">Amortisation / yr</div>
                  <div className="metric-value">£{annualAmort.toFixed(1)}m</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Wages / yr</div>
                  <div className="metric-value">£{annualWage.toFixed(1)}m</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Agent Accrual / yr</div>
                  <div className="metric-value">£{annualAgent.toFixed(1)}m</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Total Annual P&L Hit</div>
                  <div className="metric-value" style={{ color:'var(--red)' }}>£{totalAnnual.toFixed(1)}m</div>
                </div>
              </div>
              <div style={{ padding:'12px 16px', background:'rgba(79,142,247,0.08)', borderRadius:8, border:'1px solid rgba(79,142,247,0.18)' }}>
                <span style={{ color:'var(--blue)', fontWeight:700 }}>
                  Total Package Cost over {contractYrs} Years: £{totalContract.toFixed(1)}m
                </span>
              </div>
            </div>

            {/* Charts row */}
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:18 }}>

              <div className="glass" style={{ padding:24 }}>
                <h3 style={{ marginBottom:12 }}>PSR Budget Overview</h3>
                <PieChart width={280} height={230}>
                  <Pie data={donutData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} dataKey="value" paddingAngle={2}>
                    {donutData.map((_, i) => <Cell key={i} fill={DONUT_COLORS[i]}/>)}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background:'var(--bg-elevated)', border:'1px solid var(--glass-border)', borderRadius:8, fontSize:12 }}
                    formatter={(v: number) => [`£${v.toFixed(1)}m`]}/>
                  <Legend wrapperStyle={{ fontSize:'0.75rem', color:'var(--text-2)' }}/>
                </PieChart>
              </div>

              <div className="glass" style={{ padding:24 }}>
                <h3 style={{ marginBottom:12 }}>Annual Accounting Schedule</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={barData} margin={{ top:4, right:8, left:-16, bottom:4 }}>
                    <XAxis dataKey="name" tick={{ fill:'var(--text-2)', fontSize:10 }} axisLine={false} tickLine={false}/>
                    <YAxis tick={{ fill:'var(--text-2)', fontSize:10 }} axisLine={false} tickLine={false}/>
                    <Tooltip
                      contentStyle={{ background:'var(--bg-elevated)', border:'1px solid var(--glass-border)', borderRadius:8, fontSize:11 }}
                      formatter={(v: number) => [`£${v.toFixed(1)}m`]}/>
                    <Bar dataKey="Amortisation" stackId="a" fill="#4f8ef7" radius={[0,0,2,2]}/>
                    <Bar dataKey="Wages"        stackId="a" fill="#00e87a"/>
                    <Bar dataKey="Agent Fees"   stackId="a" fill="#f5a623" radius={[2,2,0,0]}/>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Disclaimer */}
            <p style={{ fontSize:'0.72rem', color:'var(--text-3)', textAlign:'center', lineHeight:1.5 }}>
              PSR calculations are illustrative. The 3-year rolling assessment includes prior years.
              Always verify with your club's finance team. PL limit = £105m over 3 seasons (2025 rules).
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
