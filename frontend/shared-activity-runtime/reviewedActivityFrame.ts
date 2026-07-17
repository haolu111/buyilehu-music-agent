const ELEMENT_NAME = 'buyilehu-reviewed-activity'

class ReviewedActivityElement extends HTMLElement {
  static get observedAttributes() { return ['url', 'title'] }
  private activityFrame: HTMLIFrameElement | null = null
  private activityConfig: Record<string, unknown> = {}

  set config(value: Record<string, unknown> | null | undefined) {
    this.activityConfig = value && typeof value === 'object' ? value : {}
    this.sendConfig()
  }

  get config() {
    return this.activityConfig
  }

  connectedCallback() {
    this.render()
    window.addEventListener('message', this.receiveActivityEvent)
  }

  disconnectedCallback() {
    window.removeEventListener('message', this.receiveActivityEvent)
  }

  attributeChangedCallback() {
    if (this.isConnected) this.render()
  }

  private receiveActivityEvent = (event: MessageEvent) => {
    if (event.origin !== window.location.origin) return
    if (event.source !== this.activityFrame?.contentWindow) return
    const message = event.data
    if (message?.type === 'buyilehu:activity-ready') {
      this.sendConfig()
      return
    }
    if (!message || (
      message.type !== 'buyilehu:activity-completed'
      && message.type !== 'buyilehu:virtual-instrument-completed'
    )) return
    const result = message.result ?? message.payload?.result
    this.emitCompleted(
      result && typeof result === 'object' ? result : {},
    )
  }

  private emitCompleted(result: Record<string, unknown>) {
    this.dispatchEvent(new CustomEvent('completed', {
      detail: {
        result,
      },
      bubbles: true,
      composed: true,
    }))
  }

  private sendConfig() {
    this.activityFrame?.contentWindow?.postMessage({
      type: 'buyilehu:load-music-content',
      config: this.activityConfig,
    }, window.location.origin)
  }

  private render() {
    const url = this.getAttribute('url') || ''
    const title = this.getAttribute('title') || '课堂活动'
    this.replaceChildren()
    if (!url) return
    const iframe = document.createElement('iframe')
    iframe.src = url
    iframe.title = title
    iframe.loading = 'eager'
    iframe.allow = 'autoplay; microphone'
    iframe.style.display = 'block'
    iframe.style.width = '100%'
    iframe.style.height = '100%'
    iframe.style.minHeight = 'var(--reviewed-activity-min-height, 620px)'
    iframe.style.border = '0'
    iframe.style.borderRadius = '20px'
    iframe.style.background = '#fff'
    iframe.addEventListener('load', () => this.sendConfig())
    this.activityFrame = iframe

    const completeButton = document.createElement('button')
    completeButton.type = 'button'
    completeButton.textContent = '确认完成本活动'
    completeButton.style.display = 'block'
    completeButton.style.margin = 'var(--reviewed-activity-action-gap, 16px) auto 0'
    completeButton.style.padding = '10px 22px'
    completeButton.style.border = '0'
    completeButton.style.borderRadius = '999px'
    completeButton.style.background = '#178c79'
    completeButton.style.color = '#fff'
    completeButton.style.fontWeight = '700'
    completeButton.style.cursor = 'pointer'
    completeButton.addEventListener('click', () => {
      completeButton.textContent = '已确认完成'
      completeButton.disabled = true
      completeButton.style.opacity = '0.7'
      this.emitCompleted({ completed: true, confirmation: 'manual' })
    })

    this.append(iframe, completeButton)
  }
}

export function registerReviewedActivityElement() {
  if (!customElements.get(ELEMENT_NAME)) {
    customElements.define(ELEMENT_NAME, ReviewedActivityElement)
  }
}
