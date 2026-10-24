// src/theme/theme.js
// Le front n'ARBITRE rien : le serveur (theme_for) dit quel thème est actif.
// Ce module ne fait que l'appliquer (attribut data-theme) et fournir le libellé neutre.

// Libellé de marque quand aucun groupe ne s'applique (sans groupe, admin, pages de connexion).
// C'est la seule marque qui vit dans le code : les autres sont des DONNÉES des groupes.
export const NEUTRAL_BRAND = 'La cuisine des copains'

// Libellé à afficher pour un thème venu du serveur ({ slug, key, brand } ou null).
export function brandOf(theme) {
  return theme?.brand ?? NEUTRAL_BRAND
}

// Pose (ou retire) la palette sur <html>. Sans attribut : variables du :root = neutre.
export function applyTheme(key) {
  const root = document.documentElement
  if (key) {
    root.dataset.theme = key // ⇔ <html data-theme="famille">
  } else {
    delete root.dataset.theme
  }
}
