// src/components/ThemeSelect.jsx
// Choix du thème pour un profil MULTI-GROUPES (décision J6, 22/10/2026).
// Provisoire dans l'en-tête : rejoindra la future page « profil » (épopée C).
// Les options et le thème actif viennent du serveur ; ce composant ne décide rien.

import { useAuth } from '../auth/AuthContext'
import { brandOf } from '../theme/theme'
import styles from './Layout.module.css'

export default function ThemeSelect() {
  const { theme, themeOptions, chooseTheme } = useAuth()

  // Un seul groupe (ou aucun) : rien à choisir, rien à afficher.
  if (themeOptions.length < 2) return null

  async function handleChange(e) {
    try {
      await chooseTheme(e.target.value)
    } catch (err) {
      console.error('Changement de thème impossible', err)
    }
  }

  return (
    <label className={styles.themeLabel}>
      Thème
      <select className={styles.themeSelect} value={theme?.slug ?? ''} onChange={handleChange}>
        {themeOptions.map((option) => (
          <option key={option.slug} value={option.slug}>
            {brandOf(option)}
          </option>
        ))}
      </select>
    </label>
  )
}
