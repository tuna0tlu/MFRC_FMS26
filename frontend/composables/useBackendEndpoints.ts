const trimTrailingSlash = (value: string): string => value.replace(/\/+$/, "")

const resolveHost = (): string => {
  if (import.meta.client && window?.location?.hostname) {
    return window.location.hostname
  }
  return "localhost"
}

export const useBackendEndpoints = () => {
  const config = useRuntimeConfig()

  const configuredHttpBase = String(config.public.refereeUrl || "").trim()
  const configuredWsUrl = String(config.public.websocketUrl || "").trim()
  const configuredStreamUrl = String(config.public.streamEmbedUrl || "").trim()

  const httpBase =
    configuredHttpBase && configuredHttpBase.toLowerCase() !== "auto"
      ? trimTrailingSlash(configuredHttpBase)
      : `http://${resolveHost()}:5022`

  const wsUrl =
    configuredWsUrl && configuredWsUrl.toLowerCase() !== "auto"
      ? configuredWsUrl
      : `${import.meta.client && window?.location?.protocol === "https:" ? "wss" : "ws"}://${resolveHost()}:5022/audis/ws`

  const streamEmbedUrl =
    configuredStreamUrl && configuredStreamUrl.toLowerCase() !== "auto"
      ? configuredStreamUrl
      : `http://${resolveHost()}:8889/live/mfrc/`

  return {
    httpBase,
    wsUrl,
    streamEmbedUrl,
  }
}
