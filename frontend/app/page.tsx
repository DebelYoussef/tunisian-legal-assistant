'use client'

import { useState } from 'react'
import { useTheme } from 'next-themes'
import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, CheckCircle, Search, Clock, Shield, BookOpen, Menu, X, Sun, Moon } from 'lucide-react'

export default function HomePage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { theme, setTheme } = useTheme()

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-border/50 backdrop-blur-md bg-background/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3 flex-shrink-0">
              <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-accent flex items-center justify-center bg-card">
                <Image
                  src="/logo.png"
                  alt="Assistant Juridique Tunisien"
                  width={40}
                  height={40}
                  className="w-full h-full object-cover"
                />
              </div>
              <span className="text-lg font-bold text-foreground hidden sm:inline">
                Assistant Juridique
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              <Link href="#features" className="text-muted-foreground hover:text-foreground transition-colors text-sm font-medium">
                Fonctionnalités
              </Link>
              <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors text-sm font-medium">
                Tarification
              </Link>
              <Link href="#contact" className="text-muted-foreground hover:text-foreground transition-colors text-sm font-medium">
                Contact
              </Link>
            </div>

            {/* CTA Buttons */}
            <div className="hidden md:flex items-center gap-3">
              <button
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="p-2 rounded-lg hover:bg-card transition-colors"
                title="Toggle theme"
              >
                {theme === 'dark' ? (
                  <Sun className="w-5 h-5 text-accent" />
                ) : (
                  <Moon className="w-5 h-5 text-accent" />
                )}
              </button>
              <Link
                href="/login"
                className="px-4 py-2 text-foreground hover:text-accent transition-colors text-sm font-medium"
              >
                Se connecter
              </Link>
              <Link
                href="/register"
                className="px-6 py-2 rounded-lg bg-accent text-accent-foreground hover:bg-accent/90 text-sm font-medium transition-colors flex items-center gap-2"
              >
                Commencer
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-card transition-colors"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {/* Mobile Navigation */}
          {isMenuOpen && (
            <div className="md:hidden pb-4 space-y-3 border-t border-border/50">
              <Link href="#features" className="block px-4 py-2 text-muted-foreground hover:text-foreground transition-colors">
                Fonctionnalités
              </Link>
              <Link href="#" className="block px-4 py-2 text-muted-foreground hover:text-foreground transition-colors">
                Tarification
              </Link>
              <Link href="#contact" className="block px-4 py-2 text-muted-foreground hover:text-foreground transition-colors">
                Contact
              </Link>
              <div className="flex gap-2 pt-2 px-4">
                <Link href="/login" className="flex-1 px-4 py-2 text-center text-foreground hover:text-accent transition-colors text-sm">
                  Se connecter
                </Link>
                <Link href="/register" className="flex-1 px-4 py-2 rounded-lg bg-accent text-accent-foreground hover:bg-accent/90 text-center text-sm font-medium">
                  Commencer
                </Link>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center px-4 py-20 overflow-hidden">
        {/* Background gradient elements */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-20 left-1/4 w-96 h-96 bg-accent/8 rounded-full filter blur-3xl" />
          <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-accent/8 rounded-full filter blur-3xl" />
        </div>

        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block mb-6 px-4 py-2 rounded-full border border-accent/30 bg-accent/5">
            <p className="text-sm font-medium text-accent">Assistant Juridique Intelligent</p>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Votre Assistant Juridique Tunisien
            <span className="text-accent block md:inline"> Intelligent</span>
          </h1>

          <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Obtenez des réponses juridiques instantanées, explorez les lois tunisiennes, et bénéficiez d&apos;une assistance 24/7 basée sur la jurisprudence et les textes de loi.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link
              href="/register"
              className="px-8 py-3 rounded-lg bg-accent text-accent-foreground hover:bg-accent/90 font-semibold flex items-center justify-center gap-2 transition-colors"
            >
              Commencer Gratuitement
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="#features"
              className="px-8 py-3 rounded-lg border-2 border-accent/50 text-foreground hover:border-accent/80 hover:bg-accent/5 font-semibold transition-colors"
            >
              Découvrir
            </Link>
          </div>

          {/* Hero Image - Using legal/chat interface themed placeholder */}
          <div className="relative mt-16">
            <div className="absolute inset-0 bg-gradient-to-r from-accent/20 via-transparent to-accent/20 rounded-2xl" />
            <div className="relative rounded-2xl border border-accent/20 overflow-hidden bg-card/50 p-8">
              <div className="grid grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-32 rounded-lg bg-muted/30 border border-border/50 flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-8 h-8 rounded bg-accent/20 mx-auto mb-2" />
                      <div className="text-xs text-muted-foreground">Interface</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-card/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Pourquoi Choisir Notre Assistant?
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Des outils puissants conçus pour simplifier la recherche juridique et l&apos;accès au droit tunisien.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: Search,
                title: 'Recherche RAG',
                description: 'Accès instantané aux textes de loi tunisiens',
              },
              {
                icon: Clock,
                title: 'Disponible 24/7',
                description: 'Assistance juridique à tout moment',
              },
              {
                icon: Shield,
                title: 'Sécurisé',
                description: 'Vos données protégées et confidentielles',
              },
              {
                icon: BookOpen,
                title: 'Base Complète',
                description: 'Documentation juridique exhaustive',
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="p-6 rounded-xl border border-border/50 hover:border-accent/50 bg-background hover:bg-card/50 transition-all duration-300"
              >
                <feature.icon className="w-12 h-12 text-accent mb-4" />
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">
                Réponses Juridiques Précises et Rapides
              </h2>
              <ul className="space-y-4">
                {[
                  'Accès aux articles du code civil tunisien',
                  'Consultation sur les droits du travail',
                  'Conseils en droit commercial',
                  'Assistance pour les contrats',
                  'Explications claires et simples',
                ].map((benefit, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                    <span className="text-foreground">{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-card/50 border border-border/50 rounded-xl p-8">
              <div className="space-y-4">
                <div className="h-32 rounded-lg bg-muted/30 border border-border/50" />
                <div className="h-16 rounded-lg bg-muted/30 border border-border/50" />
                <div className="h-16 rounded-lg bg-muted/30 border border-border/50" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-card/30">
        <div className="max-w-4xl mx-auto">
          <div className="relative rounded-2xl border border-accent/30 bg-gradient-to-r from-accent/10 to-transparent p-8 sm:p-12 text-center overflow-hidden">
            <div className="absolute inset-0 -z-10">
              <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full filter blur-3xl" />
            </div>

            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Prêt à Commencer?
            </h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              Rejoignez des milliers d&apos;utilisateurs qui font confiance à notre assistant juridique pour leurs besoins légaux.
            </p>
            <Link
              href="/register"
              className="inline-flex px-8 py-3 rounded-lg bg-accent text-accent-foreground hover:bg-accent/90 font-semibold items-center gap-2 transition-colors"
            >
              Créer mon Compte
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="contact" className="border-t border-border/50 py-12 px-4 bg-background">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div>
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <div className="w-8 h-8 rounded-full overflow-hidden border-2 border-accent flex items-center justify-center bg-card">
                  <Image
                    src="/logo.png"
                    alt="Logo"
                    width={32}
                    height={32}
                    className="w-full h-full object-cover"
                  />
                </div>
                Assistant Juridique
              </h3>
              <p className="text-sm text-muted-foreground">
                Votre assistant juridique tunisien intelligent et fiable.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-sm">Navigation</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="#features" className="hover:text-accent transition-colors">Fonctionnalités</Link></li>
                <li><Link href="#" className="hover:text-accent transition-colors">Tarification</Link></li>
                <li><Link href="/login" className="hover:text-accent transition-colors">Se connecter</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-sm">Légal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="#" className="hover:text-accent transition-colors">Conditions d&apos;utilisation</Link></li>
                <li><Link href="#" className="hover:text-accent transition-colors">Politique de confidentialité</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-sm">Contact</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>Email: info@assistant-juridique.tn</li>
                <li>Tél: +216 XX XXX XXX</li>
              </ul>
            </div>
          </div>

          <div className="border-t border-border/50 pt-8 text-center text-sm text-muted-foreground">
            <p>&copy; 2024 Assistant Juridique Tunisien. Tous droits réservés.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
