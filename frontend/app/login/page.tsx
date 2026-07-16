'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { loginUser } from '@/lib/api'
import { Mail, Lock, Loader } from 'lucide-react'
import Image from 'next/image'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await loginUser(email, password)
      router.push('/chat')
    } catch (err: any) {
      setError(err.message || 'Erreur de connexion. Veuillez réessayer.')
      console.error('[v0] Login error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mb-6 flex justify-center">
            <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-accent/30 flex items-center justify-center bg-card">
              <Image
                src="/logo.png"
                alt="Assistant Juridique Tunisien"
                width={128}
                height={128}
                className="w-full h-full object-cover"
              />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-foreground mb-2">
            Bienvenue
          </h1>
          <p className="text-muted-foreground">
            Connectez-vous pour continuer
          </p>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="bg-background rounded-xl border border-border shadow-lg p-6 space-y-4"
        >
          {/* Error message */}
          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 text-sm">
              {error}
            </div>
          )}

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Adresse e-mail
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                placeholder="vous@exemple.com"
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-card border border-input focus:border-accent outline-none transition-colors disabled:opacity-50"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Mot de passe
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                placeholder="••••••••"
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-card border border-input focus:border-accent outline-none transition-colors disabled:opacity-50"
              />
            </div>
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={isLoading || !email || !password}
            className="w-full py-2.5 rounded-lg bg-accent hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Connexion en cours...
              </>
            ) : (
              'Se connecter'
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-muted-foreground">
            Pas encore de compte ?{' '}
            <Link
              href="/register"
              className="text-accent hover:opacity-80 transition-opacity font-medium"
            >
              S&apos;inscrire
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
