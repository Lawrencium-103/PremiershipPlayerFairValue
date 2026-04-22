import { NavLink } from 'react-router-dom'

const links = [
  { to: '/estimate', label: 'Transfer Estimator' },
  { to: '/ffp',      label: 'PSR Advisor' },
  { to: '/intel',    label: 'Live Intel' },
]

export default function Navbar() {
  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 100,
      background: 'rgba(7,7,17,0.85)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255,255,255,0.07)',
      height: 68,
      display: 'flex', alignItems: 'center',
    }}>
      <div className="container" style={{ display:'flex', alignItems:'center', justifyContent:'space-between', width:'100%' }}>

        {/* Wordmark */}
        <NavLink to="/" style={{ display:'flex', alignItems:'center', gap:10, textDecoration:'none' }}>
          <div style={{
            width:34, height:34, borderRadius:9,
            background:'linear-gradient(135deg,#00e87a,#4f8ef7)',
            display:'flex', alignItems:'center', justifyContent:'center',
            fontWeight:900, fontSize:14, color:'#000', letterSpacing:'-0.04em',
            boxShadow:'0 0 14px rgba(0,232,122,0.35)',
          }}>FV</div>
          <span style={{ fontWeight:800, fontSize:'1.05rem', letterSpacing:'-0.03em' }}>
            Fair<span className="gradient-text">Value</span>
          </span>
        </NavLink>

        {/* Nav links */}
        <div style={{ display:'flex', alignItems:'center', gap:4 }}>
          {links.map(({ to, label }) => (
            <NavLink
              key={to} to={to}
              style={({ isActive }) => ({
                padding: '7px 16px',
                borderRadius: 8,
                fontSize: '0.85rem',
                fontWeight: isActive ? 600 : 400,
                color: isActive ? 'var(--green)' : 'var(--text-2)',
                background: isActive ? 'var(--green-dim)' : 'transparent',
                transition: 'all 0.2s',
                textDecoration: 'none',
              })}
            >{label}</NavLink>
          ))}
        </div>

        {/* Badge */}
        <span className="badge badge-blue" style={{ fontSize:'0.68rem', display:'flex', alignItems:'center', gap:5 }}>
          <span style={{ width:6, height:6, borderRadius:'50%', background:'var(--green)', display:'inline-block', animation:'pulse-ring 2s infinite' }}/>
          XGBoost + SHAP
        </span>
      </div>
    </nav>
  )
}
