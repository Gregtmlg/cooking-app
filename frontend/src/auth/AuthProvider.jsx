// Source unique de l'état d'authentification côté front.
// Il ne navigue jamais : il expose un état ; les gardes décident des redirections.

import { useCallback, useEffect, useState } from 'react'
import { AuthContext } from './AuthContext'
import * as authApi from '../api/auth'

const ANONYMOUS = { status: 'anonymous', account: null, profile: null }

// Traduit une réponse SessionRead du backend en état du contexte.
// Fonction pure, hors du composant : utilisée par le chargement initial ET par refresh.
function authenticated(session) {
  return { status: 'authenticated', account: session.account, profile: session.profile }
}

export default function AuthProvider({ children }) {
  // 'loading' tant que /me n'a pas répondu : évite de rediriger vers /login
  // un utilisateur dont le cookie est en cours de vérification.
  const [state, setState] = useState({ status: 'loading', account: null, profile: null })

  // Chargement initial : une fois, au montage.
  // setState n'est appelé que dans les callbacks .then/.catch (quand le réseau répond),
  // jamais directement dans le corps de l'effet.
  useEffect(() => {
    let ignore = false
    authApi
      .getMe()
      .then((session) => {
        if (!ignore) setState(authenticated(session))
      })
      .catch(() => {
        // 401 (pas de cookie / session expirée) ou backend injoignable → anonyme
        if (!ignore) setState(ANONYMOUS)
      })
    // Nettoyage : si l'effet est annulé avant la réponse, on ignore celle-ci.
    return () => {
      ignore = true
    }
  }, [])

  // Resynchronisation à la demande (utilisée par l'intercepteur, jalon 5).
  // useCallback(…, []) : même fonction d'un rendu à l'autre (référence stable).
  const refresh = useCallback(async () => {
    try {
      setState(authenticated(await authApi.getMe()))
    } catch {
      setState(ANONYMOUS)
    }
  }, [])

  async function login(username, password) {
    const session = await authApi.login(username, password) // lève si 401 → la page affiche
    setState(authenticated(session))
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      setState(ANONYMOUS) // déconnexion locale garantie, même si le réseau échoue
    }
  }

  async function selectProfile(profileId) {
    const profile = await authApi.selectProfile(profileId)
    setState((prev) => ({ ...prev, profile }))
  }

  async function changePassword(oldPassword, newPassword) {
    const account = await authApi.changePassword(oldPassword, newPassword)
    setState((prev) => ({ ...prev, account })) // must_change_password repasse à false
  }

  const value = { ...state, login, logout, selectProfile, changePassword, refresh }
  return <AuthContext value={value}>{children}</AuthContext>
}