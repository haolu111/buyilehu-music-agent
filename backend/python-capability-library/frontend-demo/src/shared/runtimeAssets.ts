const RUNTIME_ASSETS_PREFIX = "/runtime-assets/";

export function runtimeAssetUrl(path: string, baseUrl = import.meta.env?.BASE_URL ?? "/"): string {
  const normalizedPath = path.startsWith(RUNTIME_ASSETS_PREFIX)
    ? path.slice(RUNTIME_ASSETS_PREFIX.length)
    : path.replace(/^\/+/, "");
  const normalizedBase = baseUrl.endsWith("/") ? baseUrl : `${baseUrl}/`;
  return `${normalizedBase}runtime-assets/${normalizedPath}`;
}
