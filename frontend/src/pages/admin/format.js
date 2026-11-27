// src/pages/admin/format.js
// Petites fonctions d'AFFICHAGE du back-office (aucune règle métier ici).

// Le backend stocke des dates naïves en UTC (dette notée en T4a J3) : sans « Z »,
// le navigateur les lirait comme une heure locale, avec une heure d'écart.
export function formatDate(iso) {
  if (!iso) return ''
  const hasZone = /[zZ]|[+-]\d\d:\d\d$/.test(iso)
  return new Date(hasZone ? iso : `${iso}Z`).toLocaleDateString('fr-FR')
}

// Nom lisible d'un groupe à partir de son slug (repli sur le slug s'il est inconnu).
export function groupNames(slugs, groups) {
  if (slugs.length === 0) return 'sans groupe'
  const bySlug = Object.fromEntries(groups.map((g) => [g.slug, g.name]))
  return slugs.map((slug) => bySlug[slug] ?? slug).join(', ')
}
