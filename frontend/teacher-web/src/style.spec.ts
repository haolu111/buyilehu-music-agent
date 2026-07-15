import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const styles = readFileSync(resolve(process.cwd(), 'src/style.css'), 'utf8')

describe('global mobile navigation styles', () => {
  it('keeps a single approved token root and does not restore horizontal sidebar navigation', () => {
    expect(styles.match(/^:root\s*\{/gm)).toHaveLength(1)
    expect(styles).not.toContain('.sidebar{position:static')
    expect(styles).not.toContain('grid-template-columns:repeat(5,120px)')
    expect(styles).not.toContain('button,.button { min-height:38px')
    expect(styles).toContain('.nav-label-mobile')
    expect(styles).toContain('.nav-label-desktop')
  })

  it('keeps proposal evidence styles consolidated after the details-panel refresh', () => {
    expect(styles.match(/\.proposal-evidence-grid\{/g)).toHaveLength(2)
    expect(styles.match(/\.objective-list\{/g)).toHaveLength(1)
    expect(styles.match(/\.source-section-list\{/g)).toHaveLength(2)
    expect(styles).toContain('.proposal-evidence>summary')
  })
})
