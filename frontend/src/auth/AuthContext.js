// Objet Context + hook d'accès. Séparé du provider : un fichier .jsx qui
// exporte autre chose qu'un composant casse le Fast Refresh de Vite.

import { createContext, useContext } from 'react'

export const AuthContext = createContext(null)

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === null) {
        // Erreur de câblage, pas d'utilisateur : on échoue fort et tôt.
        throw new Error('useAuth doit être utilisé sous AuthProvider')
    }
    return context
}