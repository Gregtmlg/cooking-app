import styles from './KitchenSketch.module.css'

function KitchenSketch() {
  return (
    <svg
      className={styles.sketch}
      viewBox="0 0 240 240"
      aria-hidden="true"       /* décoratif : masqué aux lecteurs d'écran */
    >
      <path d="M 74 116 L 82 178 Q 86 194 106 194 L 134 194 Q 154 194 158 178 L 166 116" pathLength="1" />
      <path d="M 62 116 L 178 116" pathLength="1" />
      <path d="M 106 104 Q 98 88 108 76 Q 118 64 108 50" pathLength="1" />
      <path d="M 134 104 Q 142 88 132 76 Q 122 64 132 50" pathLength="1" />
    </svg>
  )
}

export default KitchenSketch