// src/pages/SelectProfilePage.jsx
// Sélection du profil actif (façon Netflix).
// Hors de RequireProfile (sinon boucle). Accessible même avec un profil déjà choisi
// (changer de profil) → c'est le clic qui navigue, pas l'état.

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { getProfiles } from '../api/auth'
import styles from './SelectProfilePage.module.css'

export default function SelectProfilePage() {
  const { selectProfile, logout } = useAuth()
  const navigate = useNavigate()
  const [profiles, setProfiles] = useState(null) // null = pas encore chargés
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  // Chargement de la liste au montage — même motif que AuthProvider :
  // setState seulement dans les callbacks, drapeau `ignore` contre les réponses périmées.
  useEffect(() => {
    let ignore = false
    getProfiles()
      .then((data) => {
        if (!ignore) setProfiles(data)
      })
      .catch(() => {
        if (!ignore) setError('Impossible de charger les profils.')
      })
    return () => {
      ignore = true
    }
  }, [])

  async function handleSelect(profileId) {
    setError(null)
    setSubmitting(true)
    try {
      await selectProfile(profileId)
      navigate('/', { replace: true })
    } catch {
      setError("Ce profil n'est pas disponible.")
      setSubmitting(false)
    }
  }

  return (
    <main className={styles.page}>
      <h1 className={styles.title}>Qui cuisine aujourd'hui ?</h1>

      {error && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}

      {profiles === null && !error && <p className={styles.loading}>Chargement…</p>}

      {profiles !== null && (
        <ul className={styles.grid}>
          {profiles.map((p) => (
            <li key={p.id}>
              <button
                type="button"
                className={styles.profile}
                onClick={() => handleSelect(p.id)}
                disabled={submitting}
              >
                <span className={styles.avatar} aria-hidden="true">
                  {p.display_name.charAt(0).toUpperCase()}
                </span>
                <span className={styles.name}>{p.display_name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      <button className={styles.logout} type="button" onClick={logout}>
        Se déconnecter
      </button>
    </main>
  )
}