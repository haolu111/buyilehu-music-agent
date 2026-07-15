export const RAW_PREVIEW_MAX_LENGTH = 8_000

export interface TextPreview {
  content: string
  truncated: boolean
}

export function createTextPreview(value: string | null | undefined): TextPreview {
  const content = value || ''
  return {
    content: content.slice(0, RAW_PREVIEW_MAX_LENGTH),
    truncated: content.length > RAW_PREVIEW_MAX_LENGTH,
  }
}
