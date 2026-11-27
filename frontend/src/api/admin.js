// src/api/admin.js
// Couche d'accès au back-office. Fonctions « bêtes », comme auth.js et recipes.js :
// elles traduisent HTTP en JS et lèvent sur erreur. Toutes ces routes sont gardées
// côté serveur par require_admin : un non-admin reçoit 403, quoi que fasse le front.

import api from './client'

export async function getInventory() {
  const response = await api.get('/api/v1/admin/inventory')
  return response.data
}
