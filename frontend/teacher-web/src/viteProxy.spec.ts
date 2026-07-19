import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const teacherConfig = readFileSync(resolve(process.cwd(), 'vite.config.ts'), 'utf8')
const studentConfig = readFileSync(resolve(process.cwd(), '../student-web/vite.config.ts'), 'utf8')

describe('activity asset proxy configuration', () => {
  it('serves activity assets from the Python capability library in both classroom apps', () => {
    for (const config of [studentConfig, teacherConfig]) {
      expect(config).toMatch(/'\/static':\s*\{\s*target:\s*'http:\/\/localhost:8001',\s*changeOrigin:\s*true,\s*\}/s)
    }
  })
})
