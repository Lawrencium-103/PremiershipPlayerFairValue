import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Estimator from './pages/Estimator'
import FFPAdvisor from './pages/FFPAdvisor'
import Intel from './pages/Intel'

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/"        element={<Landing   />} />
        <Route path="/estimate" element={<Estimator />} />
        <Route path="/ffp"      element={<FFPAdvisor />} />
        <Route path="/intel"    element={<Intel     />} />
      </Routes>
    </>
  )
}
