// src/auth/password.js
// Miroir des bornes du backend (account_service) — pour un message IMMÉDIAT.
// Confort uniquement : le serveur revérifie toujours (422 sinon).
// Partagé par le changement de mot de passe et le back-office (une seule copie).

export const MIN_LENGTH = 8
export const MAX_LENGTH = 128

// Saisie d'un nouveau mot de passe + sa confirmation. Renvoie un message, ou null.
// La confirmation ne sert qu'à attraper une faute de frappe : elle ne part JAMAIS
// au serveur (les schémas admin refusent tout champ inconnu, extra="forbid").
export function checkNewPassword(password, confirmation) {
  if (password !== confirmation) return 'Les deux mots de passe ne correspondent pas.'
  if (password.length < MIN_LENGTH || password.length > MAX_LENGTH) {
    return `Le mot de passe doit contenir entre ${MIN_LENGTH} et ${MAX_LENGTH} caractères.`
  }
  return null
}
