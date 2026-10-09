// Source unique de l'état d'authentification côté front.
// Il ne navigue jamais : il expose un état ; les gardes décident des redirections.


import { useCallback, useEffect, useState } from 'react'
import { AuthContext } from './AuthContext'
import * as authApi from '../api/auth'

const ANONYMOUS = {status: 'anonymous', account: null, profile: null}

export default function AuthProvider({ children }) {
    // 'loading' tant que /me n'a pas répondu : évite de rediriger vers /login
    // un utilisateur dont le cookie est en cours de vérification.
    const [state, setState] = useState({status: 'loading', account: null, profile: null})

    // useCallback(…, []) : même référence à chaque rendu → pas de boucle d'effet,
    // et référence stable pour l'intercepteur
    const refresh = useCallback(async () => {
        try {
            const session = await authApi.getMe()
            setState({status: 'authenticated', account: session.account, profile: session.profile})
        } catch {
            // 401 (pas de cookie / session expirée) → anonyme.
            // Backend injoignable → anonyme aussi : la page de login affichera l'erreur au submit.
            setState(ANONYMOUS)
        }
    }, [])

    useEffect(() => {
        refresh()
    }, [refresh])

    async function login(username, password) {
        const session = await authApi.login(username, password)
        setState({status: 'authenticated', account: session.account, profile: session.profile})
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
        setState((prev) => ({...prev, profile}))
    }

    async function changePassword(oldPassword, newPassword) {
        const account = await authApi.changePassword(oldPassword, newPassword)
        setState((prev) => ({...prev, account})) // must_change_password repasse à false
    }

    const value = {...state, login, logout, selectProfile, changePassword, refresh}
    return <AuthContext value={value}>{children}</AuthContext>
}
