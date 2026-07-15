import { describe, expect, it } from 'vitest'
import { RAW_PREVIEW_MAX_LENGTH, createTextPreview } from './textPreview'

describe('createTextPreview', () => {
  it('caps oversized content and marks the preview as truncated', () => {
    const preview = createTextPreview('教'.repeat(RAW_PREVIEW_MAX_LENGTH + 1))

    expect(preview.content).toHaveLength(RAW_PREVIEW_MAX_LENGTH)
    expect(preview.truncated).toBe(true)
  })
})
