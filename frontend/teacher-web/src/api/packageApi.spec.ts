import { describe, expect, it, vi } from 'vitest'

const { get, post } = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('./request', () => ({
  default: { get, post },
  unwrap: vi.fn((promise) => promise),
}))

import { packageApi } from './packageApi'

describe('packageApi proposal requests', () => {
  it('allows large generated proposals enough time to load and confirm', () => {
    packageApi.getProposal(22)
    packageApi.confirmProposal(22)

    expect(get).toHaveBeenCalledWith('/packages/22/proposal', { timeout: 180000 })
    expect(post).toHaveBeenCalledWith('/packages/22/proposal/confirm', undefined, { timeout: 180000 })
  })
})
