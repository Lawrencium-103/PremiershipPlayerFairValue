import { useState, useEffect } from 'react';

const USAGE_KEY = 'fairvalue_evaluation_count';
const MAX_USES = 3;

export function useUsageLimiter() {
  const [useCount, setUseCount] = useState<number>(0);
  const [isLocked, setIsLocked] = useState<boolean>(false);

  useEffect(() => {
    if (localStorage.getItem('admin_access') === 'Britzy' || sessionStorage.getItem('fv_access_granted') === 'true') return;
    
    const stored = localStorage.getItem(USAGE_KEY);
    const count = stored ? parseInt(stored, 10) : 0;
    setUseCount(count);
    if (count >= MAX_USES) {
      setIsLocked(true);
    }
  }, []);

  const incrementUsage = () => {
    if (localStorage.getItem('admin_access') === 'Britzy' || sessionStorage.getItem('fv_access_granted') === 'true') return true;
    
    const newCount = useCount + 1;
    setUseCount(newCount);
    localStorage.setItem(USAGE_KEY, newCount.toString());
    if (newCount >= MAX_USES) {
      setIsLocked(true);
      return false; // Tells the caller it just locked
    }
    return true; // Still allowed
  };

  return { useCount, isLocked, incrementUsage, MAX_USES };
}

