'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export function PreloadRoutes() {
  const router = useRouter();

  useEffect(() => {
    router.prefetch('/dashboard');
    router.prefetch('/upload');
    router.prefetch('/history');
  }, []);

  return null;
}
