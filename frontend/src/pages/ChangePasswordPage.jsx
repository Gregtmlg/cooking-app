// src/pages/ChangePasswordPage.jsx
// Changement de mot de passe : flux forcé (must_change_password) ou volontaire.
// Hors de RequirePasswordChanged (sinon boucle) : c'est le clic qui navigue après succès.
// Les vérifications locales sont du confort ; l'autorité reste le backend.

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import styles from './AuthForm.module.css'

// Miroir des bornes backend (account_service) — pour un message immédiat.
const MIN_LENGTH = 8
const MAX_LENGTH = 128

function errorMessage(err) {
  const status = err.response?.status
  if (status === 403) {
    return "Ce compte est partagé : seul l'administrateur peut changer son mot de passe."
  }
  if (status === 400) {
    // WrongPassword / InvalidPassword : messages métier déjà rédigés pour l'humain.
    return err.response.data.detail
  }
  return 'Changement impossible pour le moment. Réessayez plus tard.'
}

export default function ChangePasswordPage() {
  const { account, changePassword, logout } = useAuth()
  const navigate = useNavigate()
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)

    if (newPassword !== confirmation) {
      setError('Les deux nouveaux mots de passe ne correspondent pas.')
      return
    }
    if (newPassword.length < MIN_LENGTH || newPassword.length > MAX_LENGTH) {
      setError(`Le mot de passe doit contenir entre ${MIN_LENGTH} et ${MAX_LENGTH} caractères.`)
      return
    }

    setSubmitting(true)
    try {
      await changePassword(oldPassword, newPassword)
      // Succès : on quitte la page ; les gardes décident de la suite
      // (sélection de profil si besoin, sinon accueil).
      navigate('/', { replace: true })
    } catch (err) {
      setError(errorMessage(err))
      setSubmitting(false)
    }
  }

  return (
    <main className={styles.page}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <h1 className={styles.title}>Nouveau mot de passe</h1>

        {account.must_change_password && (
          <p className={styles.info}>
            Votre mot de passe actuel est provisoire. Choisissez-en un nouveau pour continuer.
          </p>
        )}

        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}

        <div className={styles.field}>
          <label htmlFor="old-password">Mot de passe actuel</label>
          <input
            id="old-password"
            type="password"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>

        <div className={styles.field}>
          <label htmlFor="new-password">Nouveau mot de passe</label>
          <input
            id="new-password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            autoComplete="new-password"
            required
          />
          <p className={styles.hint}>
            Entre {MIN_LENGTH} et {MAX_LENGTH} caractères.
          </p>
        </div>

        <div className={styles.field}>
          <label htmlFor="confirmation">Confirmer le nouveau mot de passe</label>
          <input
            id="confirmation"
            type="password"
            value={confirmation}
            onChange={(e) => setConfirmation(e.target.value)}
            autoComplete="new-password"
            required
          />
        </div>

        <button className={styles.submit} type="submit" disabled={submitting}>
          {submitting ? 'Enregistrement…' : 'Changer le mot de passe'}
        </button>

        <button className={styles.secondary} type="button" onClick={logout}>
          Se déconnecter
        </button>
      </form>
    </main>
  )
}