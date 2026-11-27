// Gardes de route — miroir frontend de la cascade de deps.py :
// RequireAuth (≈ CurrentAccount) → RequirePasswordChanged (≈ PasswordChanged)
// → RequireProfile (≈ CurrentProfile).
// Imbriquées dans App.jsx : chaque page se place au niveau exact dont elle a besoin.
// ⚠️ Confort UX uniquement : la vraie protection est côté serveur

import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'
import { ROUTES } from '../routes'

export function RequireAuth() {
    const {status} = useAuth()
    const location = useLocation()

    if (status === 'loading') return null // /me en vol : ni afficher, ni rediriger
    if (status === 'anonymous') {
        // replace : pas d'entrée d'historique vers une page qui nous rejetterait
        return <Navigate to={ROUTES.login} replace state={{from: location}} />
    }
    return <Outlet/>
}

// Les deux gardes suivantes sont toujours imbriquées sous RequireAuth :
// status vaut forcément 'authenticated' ici, account n'est jamais null.

export function RequirePasswordChanged() {
    const {account} = useAuth()
    if (account.must_change_password) {
        return <Navigate to={ROUTES.changePassword} replace/>
    }
    return <Outlet />
}

export function RequireProfile() {
    const {profile} = useAuth()
    if (profile === null) return <Navigate to={ROUTES.selectProfile} replace/>
    return <Outlet />
}

// Garde du back-office (J6a). Toujours sous RequireProfile : account n'est jamais null.
// Un non-admin est CONNECTÉ : on le renvoie à l'accueil, pas au login.
// Confort uniquement : le serveur refuse de toute façon (require_admin → 403).
export function RequireAdmin() {
    const {account} = useAuth()
    if (!account.is_admin) return <Navigate to={ROUTES.home} replace/>
    return <Outlet />
}
