// src/routes.js
// Chemins de l'interface (barre d'adresse du navigateur) — écrits ICI et nulle part ailleurs.
// Renommer une route = changer une ligne ; aucun lien mort oublié dans une page.
// Un chemin à paramètre garde UNE seule écriture : le motif sert à <Route path>, et
// generatePath(ROUTES.recipeEdit, { id }) de React Router construit le lien.
// ⚠️ Ne concerne PAS les URL du backend (/api/v1/…) : elles vivent dans src/api/*.js.
// Ce module n'importe rien : tout le monde peut l'importer sans créer de boucle.

export const ROUTES = {
  home: '/',
  login: '/login',
  changePassword: '/change-password',
  selectProfile: '/select-profile',

  recipes: '/recipes',
  recipeNew: '/recipes/new',
  recipe: '/recipes/:id',
  recipeEdit: '/recipes/:id/edit',

  admin: '/admin',
  adminInventory: '/admin/inventaire',
  adminAccounts: '/admin/comptes',
  adminProfiles: '/admin/profils',
  adminGroups: '/admin/groupes',
  adminReassign: '/admin/reattributions',
}
