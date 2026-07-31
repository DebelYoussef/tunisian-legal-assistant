'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      router.push('/login?error=missing_token');
      return;
    }

    localStorage.setItem('auth_token', token);
    router.push('/chat');
  }, [searchParams, router]);

  return (
    <div className="flex flex-col items-center gap-4">
      <Loader2 className="w-8 h-8 animate-spin text-primary" />
      <p className="text-sm text-muted-foreground">Connexion en cours...</p>
    </div>
  );
}

export default function CallbackPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <Suspense fallback={<Loader2 className="w-8 h-8 animate-spin text-primary" />}>
        <CallbackHandler />
      </Suspense>
    </div>
  );
}
