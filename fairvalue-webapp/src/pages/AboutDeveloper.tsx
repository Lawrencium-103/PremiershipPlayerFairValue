import { motion } from 'framer-motion'
import { Linkedin, Github, Mail, Phone, ExternalLink, Briefcase, GraduationCap, Code, Database, BrainCircuit, LineChart } from 'lucide-react'

const PROJECTS = [
  {
    title: 'FairValue Player Estimator',
    tags: ['XGBoost', 'SHAP', 'React'],
    desc: 'Advanced sport analytics platform deploying Hedonic Pricing models and NLP transfer intelligence to compute PSR compliance and mitigate winner\'s curse.',
    link: '#', 
  },
  {
    title: 'WHO ESPEN Nigeria Portal',
    tags: ['Vercel Edge', 'Leaflet', 'Node.js'],
    desc: 'A premium analytics platform deployed for international public health monitoring. Engineered real-time supply chain latency algorithms bridging SQL logic with JavaScript, enveloped in a stunning glassmorphism geospatial UX.',
    link: 'https://who-espen-nigeria-ntd.vercel.app/',
  },
  {
    title: 'LinkyGen Intelligence',
    tags: ['LangGraph', 'Agentic AI'],
    desc: 'Advanced AI application utilizing a multi-agentic LangGraph architecture to streamline high-quality dynamic content pipelines.',
    link: 'https://linkygen.streamlit.app/',
  },
  {
    title: 'SESA AI Optimization',
    tags: ['Multi-Agent', 'Python'],
    desc: 'Stochastic optimization engine built on Agentic AI orchestration to minimize smart building electricity via BESS arbitrage.',
    link: 'https://sesa-energy.streamlit.app/',
  },
  {
    title: 'Stratos Content Empire',
    tags: ['LangGraph', 'Streamlit'],
    desc: 'Strategic AI marketing tool powered by LangGraph multi-agent orchestration mapping pinpoint audience intent.',
    link: 'https://stratos-content.streamlit.app/',
  },
  {
    title: 'XGen Studio',
    tags: ['CrewAI', 'LangChain'],
    desc: 'Viral writing assistant leveraging a multi-agent LLM workflow to scale brand growth via highly-humanized narratives.',
    link: 'https://xgenstudio.streamlit.app/',
  },
  {
    title: 'Finstratz Analytics',
    tags: ['TensorFlow', 'Python'],
    desc: 'Python-based financial suite utilizing deep learning (TensorFlow) to forecast stock trends and price variations.',
    link: 'https://finstratz.streamlit.app/',
  },
  {
    title: 'Stanbic IBTC Simulator',
    tags: ['Financial Modeling', 'Data Science'],
    desc: 'App generating robust performance forecasts across complex Money Market portfolios.',
    link: 'https://stanbic-ibtc-portfolio-simulation.streamlit.app/',
  },
]

export default function AboutDeveloper() {
  return (
    <div className="page" style={{ overflow: 'hidden' }}>
      
      {/* ── Cinematic Hero ────────────────────────────────────────────────── */}
      <section className="container" style={{ padding: '40px 24px 60px', borderBottom: '1px solid var(--glass-border)' }}>
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) auto', gap: '48px', alignItems: 'center' }}
        >
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '24px', padding: '6px 16px', background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.2)', borderRadius: '100px' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22C55E', animation: 'pulse-ring 2s infinite' }} />
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#4ade80', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                Open to Mid/Senior Roles Globally
              </span>
            </div>

            <h1 className="display-font" style={{ marginBottom: '16px', fontSize: ' clamp(2.5rem, 5vw, 4rem)' }}>Lawrence Oladeji</h1>
            <h2 style={{ fontSize: '1.4rem', color: 'var(--accent-blue)', marginBottom: '24px', fontWeight: 600 }}>
              AI-Native Data Scientist & Sports Pricing Strategist
            </h2>

            <p style={{ maxWidth: '720px', fontSize: '1.1rem', lineHeight: 1.8, color: 'var(--text-2)', marginBottom: '32px' }}>
              I am an AI-Native Data Associate with 3+ years of experience transforming complex datasets into strategic insights for executive decision-making. 
              My expertise encompasses sports analytics, hedonic pricing models, AI-driven transfer logic, and traditional Business Intelligence heavily augmented 
              by deep expertise in Generative AI and LLM orchestration (LangGraph, CrewAI). I am profoundly passionate about architecting scalable, data-driven solutions at the intersection of quantitative sport economics and Agentic AI.
            </p>

            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              <a href="mailto:oladeji.lawrence@gmail.com" className="btn btn-secondary">
                <Mail size={18} /> oladeji.lawrence@gmail.com
              </a>
              <a href="https://github.com/Lawrencium-103" target="_blank" rel="noreferrer" className="btn btn-ghost">
                <Github size={18} /> GitHub: Lawrencium-103
              </a>
              <span className="btn btn-ghost" style={{ cursor: 'default' }}>
                <Phone size={18} /> +234 903 881 9790
              </span>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ── Expertise Grid ────────────────────────────────────────────────── */}
      <section className="container" style={{ padding: '80px 24px' }}>
        <h2 className="display-font" style={{ marginBottom: '40px', textAlign: 'center' }}>Core Competencies</h2>
        <div className="grid-3">
          <motion.div whileHover={{ y: -5 }} className="glass" style={{ padding: '32px' }}>
            <LineChart size={32} color="#f5a623" style={{ marginBottom: '20px' }} />
            <h3 style={{ marginBottom: '12px' }}>Sports Pricing & BI</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-2)', marginBottom: '16px' }}>
              Transforming raw datasets into executive C-Suite narratives. Expert in translating complex valuations (Transfer Estimators) and multi-million-dollar portfolios into interactive command centers.
            </p>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <span className="badge badge-gold">Power BI / DAX</span>
              <span className="badge badge-gold">Tableau</span>
              <span className="badge badge-gold">XGBoost / SHAP</span>
            </div>
          </motion.div>

          <motion.div whileHover={{ y: -5 }} className="glass" style={{ padding: '32px' }}>
            <Database size={32} color="#22c55e" style={{ marginBottom: '20px' }} />
            <h3 style={{ marginBottom: '12px' }}>Data Engineering</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-2)', marginBottom: '16px' }}>
              Architecting scalable pipelines and robust data models. Proven track record dropping query latency by 15% across global health databanks using optimized SQL architectures.
            </p>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <span className="badge badge-green">PostgreSQL</span>
              <span className="badge badge-green">BigQuery</span>
              <span className="badge badge-green">Airflow ETL</span>
            </div>
          </motion.div>

          <motion.div whileHover={{ y: -5 }} className="glass" style={{ padding: '32px' }}>
            <BrainCircuit size={32} color="#3b82f6" style={{ marginBottom: '20px' }} />
            <h3 style={{ marginBottom: '12px' }}>Agentic AI & LLMs</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-2)', marginBottom: '16px' }}>
              Designing autonomous workflows orchestrating complex data routing via LLMs. Pioneering the integration of multi-agentic reasoning frameworks into traditional data domains.
            </p>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <span className="badge badge-blue">LangGraph</span>
              <span className="badge badge-blue">CrewAI</span>
              <span className="badge badge-blue">Python</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Professional Blueprint ────────────────────────────────────────── */}
      <section style={{ background: 'rgba(255,255,255,0.01)', borderTop: '1px solid var(--glass-border)', borderBottom: '1px solid var(--glass-border)' }}>
        <div className="container" style={{ padding: '80px 24px' }}>
          <h2 className="display-font" style={{ marginBottom: '48px', color: 'var(--text-1)' }}>Professional Blueprint & Background</h2>
          
          <div className="grid-2">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
              
              <div className="glass-flat" style={{ padding: '32px', position: 'relative' }}>
                <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '4px', background: 'var(--accent-blue)', borderTopLeftRadius: 'var(--radius-lg)', borderBottomLeftRadius: 'var(--radius-lg)' }} />
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <Briefcase size={20} color="var(--accent-blue)" />
                  <h3 style={{ margin: 0 }}>Data Associate</h3>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-3)', marginBottom: '20px', fontWeight: 600 }}>May 2024 – Present</div>
                <ul style={{ paddingLeft: '20px', color: 'var(--text-2)', fontSize: '0.95rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <li>Designed and deployed executive-level Power BI dashboards for C-Suite stakeholders, optimizing multi-million-dollar portfolios.</li>
                  <li>Engineered complex SQL data models on BigQuery & PostgreSQL, cutting query latency by 15% across 50+ key indicators.</li>
                  <li>Centralized 56,000+ data points across 1,450+ indicators from world-class sources (World Bank, WHO) to ensure 100% regulatory reporting accuracy.</li>
                  <li>Constructed AI content frameworks utilizing multi-agent reasoning to automate reporting, saving significant overhead blocks.</li>
                </ul>
              </div>

              <div className="glass-flat" style={{ padding: '32px', position: 'relative' }}>
                <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '4px', background: 'var(--text-3)', borderTopLeftRadius: 'var(--radius-lg)', borderBottomLeftRadius: 'var(--radius-lg)' }} />
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <Briefcase size={20} color="var(--text-3)" />
                  <h3 style={{ margin: 0 }}>Junior BI / Data Operations Analyst</h3>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-3)', marginBottom: '20px', fontWeight: 600 }}>2019 – April 2024</div>
                <ul style={{ paddingLeft: '20px', color: 'var(--text-2)', fontSize: '0.95rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <li>Synthesized business requirements into actionable data models for E-mobility.</li>
                  <li>Executed statistical modeling predicting demand, cutting lifecycles by 20%.</li>
                  <li>Identified high ROI cost-savings via exploratory spatial geospatial analysis.</li>
                </ul>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingBottom: '12px', borderBottom: '1px solid var(--glass-border)' }}>
                <GraduationCap size={22} color="var(--green)" /> Academic Background
              </h3>
              
              <div>
                <h4 style={{ fontSize: '1.1rem', marginBottom: '4px' }}>MSc in Mechanical Engineering</h4>
                <div style={{ color: 'var(--text-2)', fontSize: '0.9rem' }}>University of Ibadan · 2023 - 2024</div>
              </div>

              <div>
                <h4 style={{ fontSize: '1.1rem', marginBottom: '4px' }}>BSc in Mechanical Engineering (2:1 Honors)</h4>
                <div style={{ color: 'var(--text-2)', fontSize: '0.9rem' }}>Federal Univ. of Agriculture, Abeokuta · CGPA: 3.99/5.0</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Portfolio Grid ────────────────────────────────────────────────── */}
      <section className="container" style={{ padding: '80px 24px' }}>
        <div style={{ textAlign: 'center', marginBottom: '56px' }}>
          <h2 className="display-font" style={{ marginBottom: '16px' }}>Agentic & Analytics Portfolio</h2>
          <p style={{ maxWidth: '600px', margin: '0 auto' }}>A selection of high-impact production dashboards and multi-agent AI ecosystems built across multiple domains.</p>
        </div>

        <div className="grid-2">
          {PROJECTS.map((proj, i) => (
            <motion.a 
              href={proj.link}
              target="_blank"
              rel="noreferrer"
              key={i}
              whileHover={{ y: -4, borderColor: 'rgba(255,255,255,0.2)' }}
              className="glass" 
              style={{ padding: '32px', display: 'flex', flexDirection: 'column', cursor: proj.link === '#' ? 'default' : 'pointer', textDecoration: 'none' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <h3 className="display-font" style={{ color: 'var(--text-1)', fontSize: '1.4rem' }}>{proj.title}</h3>
                {proj.link !== '#' && <ExternalLink size={20} color="var(--text-3)" />}
              </div>
              
              <p style={{ fontSize: '0.95rem', color: 'var(--text-2)', lineHeight: 1.6, flexGrow: 1, marginBottom: '24px' }}>
                {proj.desc}
              </p>
              
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {proj.tags.map(tag => (
                  <span key={tag} style={{ padding: '4px 10px', fontSize: '0.75rem', background: 'var(--bg-elevated)', border: '1px solid var(--glass-border)', borderRadius: '6px', color: 'var(--text-1)' }}>
                    {tag}
                  </span>
                ))}
              </div>
            </motion.a>
          ))}
        </div>
      </section>

    </div>
  )
}
