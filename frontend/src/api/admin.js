// src/api/admin.js
// Couche d'accès au back-office. Fonctions « bêtes », comme auth.js et recipes.js :
// elles traduisent HTTP en JS et lèvent sur erreur. Toutes ces routes sont gardées
// côté serveur par require_admin : un non-admin reçoit 403, quoi que fasse le front.
// Conversion camelCase (JS) → snake_case (API) faite ici, et seulement ici.
// Les corps envoyés ne contiennent QUE les champs attendus : extra="forbid" refuserait
// tout champ en trop (422) — la confirmation du mot de passe ne part donc jamais.

import api from './client'

const ADMIN = '/api/v1/admin'

export async function getInventory() {
  const response = await api.get(`${ADMIN}/inventory`)
  return response.data
}

// --- Comptes ---------------------------------------------------------------------

export async function createAccount({ username, password, displayName, group }) {
  const response = await api.post(`${ADMIN}/accounts`, {
    username,
    password,
    display_name: displayName || null, // vide → le serveur prend l'identifiant
    group: group || null, // vide → sans groupe
  })
  return response.data
}

export async function resetPassword(accountId, password) {
  const response = await api.post(`${ADMIN}/accounts/${accountId}/reset-password`, { password })
  return response.data
}

export async function addProfile(accountId, { displayName, group }) {
  const response = await api.post(`${ADMIN}/accounts/${accountId}/profiles`, {
    display_name: displayName,
    group: group || null,
  })
  return response.data
}

export async function deactivateAccount(accountId) {
  const response = await api.post(`${ADMIN}/accounts/${accountId}/deactivate`)
  return response.data
}

export async function purgeAccount(accountId, confirm) {
  const response = await api.post(`${ADMIN}/accounts/${accountId}/purge`, { confirm })
  return response.data
}

// --- Profils ---------------------------------------------------------------------

export async function deactivateProfile(profileId) {
  const response = await api.post(`${ADMIN}/profiles/${profileId}/deactivate`)
  return response.data
}

export async function reactivateProfile(profileId) {
  const response = await api.post(`${ADMIN}/profiles/${profileId}/reactivate`)
  return response.data
}

export async function purgeProfile(profileId, confirm) {
  const response = await api.post(`${ADMIN}/profiles/${profileId}/purge`, { confirm })
  return response.data
}
