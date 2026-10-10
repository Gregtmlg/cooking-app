// src/api/client.js
// Instance Axios UNIQUE de l'application : tous les appels API passent par elle.
// Elle porte l'intercepteur qui détecte un changement d'état d'authentification
// côté serveur (session perdue, profil manquant, mot de passe à changer) et
// demande au contexte de se resynchroniser. Il ne navigue JAMAIS lui-même :
// ce sont les gardes de route qui décident où aller.

import axios from 'axios'

const api = axios.create({
  baseURL: '', // dev : proxy Vite ; prod : Nginx — même origine dans les deux cas
})

// Codes machine des 403 « état intermédiaire » — miroir de backend/app/api/deps.py.
// Un 403 sans l'un de ces codes (ex. compte partagé sur /change-password) est ignoré.
const STATE_CODES = ['PROFILE_REQUIRED', 'PASSWORD_CHANGE_REQUIRED']

// Requêtes dont le 401 ne signifie PAS « session perdue » :
// - login : mauvais identifiants → la page affiche son message ;
// - me    : c'est l'appel de resynchronisation lui-même → sinon boucle infinie.
const IGNORED_401 = ['/api/v1/auth/login', '/api/v1/auth/me']

// « Boîte aux lettres » : AuthProvider y dépose sa fonction refresh au démarrage.
// client.js n'a ainsi aucune dépendance vers React.
let onAuthStateChanged = null

export function setAuthStateChangedHandler(handler) {
  onAuthStateChanged = handler
}

// Cette erreur signale-t-elle que l'état d'authentification a changé ?
function signalsAuthChange(error) {
  const status = error.response?.status
  if (status === 401) {
    return !IGNORED_401.includes(error.config?.url)
  }
  if (status === 403) {
    return STATE_CODES.includes(error.response.data?.detail?.code)
  }
  return false
}

api.interceptors.response.use(
  // Réponse OK : on la laisse passer telle quelle.
  (response) => response,
  // Réponse en erreur : on prévient le contexte si besoin, puis on RE-LANCE l'erreur
  // pour que la page appelante la reçoive quand même (arrêt du chargement, message…).
  (error) => {
    if (onAuthStateChanged && signalsAuthChange(error)) {
      onAuthStateChanged()
    }
    return Promise.reject(error)
  },
)

export default api