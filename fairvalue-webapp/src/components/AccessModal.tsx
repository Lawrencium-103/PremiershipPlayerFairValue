import { motion } from 'framer-motion';
import { Lock } from 'lucide-react';

interface AccessModalProps {
  onBetaRequest?: () => void;
}

export default function AccessModal({ onBetaRequest }: AccessModalProps) {
  return (
    <div className="modal-overlay">
      <motion.div 
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="modal-content"
      >
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ 
            width: 64, height: 64, borderRadius: '50%', 
            background: 'rgba(59, 130, 246, 0.1)', 
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 20px',
            border: '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            <Lock size={28} color="#3b82f6" />
          </div>
          <h2 style={{ marginBottom: '12px', fontSize: '1.6rem' }} className="display-font">Premium Access Required</h2>
          <p style={{ fontSize: '0.95rem' }}>
            You have reached the maximum limit of 3 free AI transfer evaluations. 
            Request full enterprise access to unlock unlimited SHAP profiling, live intelligence grids, and PSR compliance modeling.
          </p>
        </div>

        <form 
          action="https://formsubmit.co/oladeji.lawrence@gmail.com" 
          method="POST"
          style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
        >
          {/* Honeypot & Config for FormSubmit */}
          <input type="text" name="_honey" style={{ display: 'none' }} />
          <input type="hidden" name="_subject" value="FairValue Enterprise Access Request!" />
          <input type="hidden" name="_captcha" value="false" />

          <div className="input-group">
            <label className="field-label">Full Name</label>
            <input type="text" name="name" className="input" placeholder="e.g. Edu Gaspar" required />
          </div>

          <div className="input-group">
            <label className="field-label">Work Email</label>
            <input type="email" name="email" className="input" placeholder="director@club.com" required />
          </div>

          <div className="input-group">
            <label className="field-label">Organisation / Club</label>
            <input type="text" name="organisation" className="input" placeholder="Arsenal FC" required />
          </div>

          <button type="submit" className="btn btn-secondary" style={{ marginTop: '12px', width: '100%' }}>
            Request Enterprise Access
          </button>
        </form>
      </motion.div>
    </div>
  );
}
