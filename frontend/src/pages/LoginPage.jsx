// Page de connexion NEUTRE : en amont de tout groupe → ni thème, ni marque.
// Elle ne navigue jamais elle-même : une fois l'état 'authenticated', le rendu
// redirige vers `from` ; les gardes prennent le relais (mot de passe, profil).

import { useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import styles from './AuthForm.module.css'

// Messages choisis côté front : on n'affiche jamais un `detail` brut (ex. 422 Pydantic).
function errorMessage(err) {
  switch (err.response?.status) {
    case 401:
      return 'Identifiant ou mot de passe incorrect.'
    case 429:
      return 'Trop de tentatives. Réessayez dans une minute.'
    default:
      return 'Connexion impossible pour le moment. Réessayez plus tard.'
  }
}

export default function LoginPage() {
  const { status, login } = useAuth()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  if (status === 'loading') return null
  if (status === 'authenticated') {
    const from = location.state?.from?.pathname ?? '/'
    return <Navigate to={from} replace />
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(username, password)
      // Rien d'autre : l'état change → re-rendu → <Navigate> ci-dessus.
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className={styles.page}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <h1 className={styles.title}>Connexion</h1>

        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}

        <div className={styles.field}>
          <label htmlFor="username">Identifiant</label>
          <input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </div>

        <div className={styles.field}>
          <label htmlFor="password">Mot de passe</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>

        <button className={styles.submit} type="submit" disabled={submitting}>
          {submitting ? 'Connexion…' : 'Se connecter'}
        </button>
      </form>
    </main>
  )
}