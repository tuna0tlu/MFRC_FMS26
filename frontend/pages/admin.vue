<template>
  <div
    ref="adminScrollEl"
    class="h-screen overflow-auto bg-slate-900 text-slate-100 p-4 md:p-8"
    @mousedown="onAdminMouseDown"
  >
    <div class="max-w-7xl mx-auto space-y-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <h1 class="text-3xl md:text-4xl font-black">FMS Yönetici Ekranı
        </h1>
        <div class="text-sm text-slate-300 text-right">
          <div>Backend: <span class="font-mono">{{ apiBase }}</span></div>
          <div v-if="liveCountdown !== null" class="text-amber-300 font-semibold">
            Maç {{ liveCountdown }} sn içinde başlayacak
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <section class="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <h2 class="text-xl font-bold mb-4">Teams</h2>

          <form class="grid grid-cols-1 md:grid-cols-4 gap-2 mb-4" @submit.prevent="createTeam">
            <input
              v-model="newTeam.id"
              class="bg-slate-900 border border-slate-600 rounded px-3 py-2"
              placeholder="Team ID (1001)"
              required
            />
            <input
              v-model="newTeam.name"
              class="bg-slate-900 border border-slate-600 rounded px-3 py-2 md:col-span-2"
              placeholder="Team Name"
              required
            />
            <button class="bg-emerald-600 hover:bg-emerald-500 rounded px-3 py-2 font-semibold" :disabled="loading">
              Add Team
            </button>
          </form>

          <div class="overflow-auto max-h-[500px] border border-slate-700 rounded">
            <table class="min-w-full text-sm">
              <thead class="bg-slate-700 sticky top-0">
                <tr>
                  <th class="text-left p-2">ID</th>
                  <th class="text-left p-2">Name</th>
                  <th class="text-left p-2">RP</th>
                  <th class="text-left p-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="team in teams" :key="team.id" class="border-t border-slate-700">
                  <td class="p-2 font-mono">{{ team.id }}</td>
                  <td class="p-2">
                    <input
                      v-model="teamEdits[team.id].name"
                      @input="markTeamDirty(team.id)"
                      class="w-full bg-slate-900 border border-slate-600 rounded px-2 py-1"
                    />
                  </td>
                  <td class="p-2 w-28">
                    <input
                      v-model.number="teamEdits[team.id].ranking_points"
                      @input="markTeamDirty(team.id)"
                      type="number"
                      min="0"
                      class="w-full bg-slate-900 border border-slate-600 rounded px-2 py-1"
                    />
                  </td>
                  <td class="p-2">
                    <div class="flex gap-2">
                      <button
                        class="bg-blue-600 hover:bg-blue-500 rounded px-2 py-1"
                        :disabled="loading"
                        @click="updateTeam(team.id)"
                      >
                        Save
                      </button>
                      <button
                        class="bg-red-700 hover:bg-red-600 rounded px-2 py-1"
                        :disabled="loading"
                        @click="deleteTeam(team.id)"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="teams.length === 0">
                  <td colspan="4" class="p-3 text-slate-400">No teams yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <h2 class="text-xl font-bold mb-4">Match Setup</h2>

          <form class="space-y-3" @submit.prevent="createMatch">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
              <select v-model="matchForm.match_type" class="bg-slate-900 border border-slate-600 rounded px-3 py-2">
                <option value="Qualification">Qualification</option>
                <option value="Elimination">Elimination</option>
                <option value="Final">Final</option>
              </select>
              <input
                v-model="matchForm.red"
                class="bg-slate-900 border border-slate-600 rounded px-3 py-2"
                placeholder="Red IDs: 1001,1002,1003"
                required
              />
              <input
                v-model="matchForm.blue"
                class="bg-slate-900 border border-slate-600 rounded px-3 py-2"
                placeholder="Blue IDs: 2001,2002,2003"
                required
              />
            </div>
            <button class="bg-emerald-600 hover:bg-emerald-500 rounded px-3 py-2 font-semibold" :disabled="loading">
              Create Match
            </button>
          </form>

          <div class="mt-4 space-y-4">
            <div
              v-for="group in matchTypeGroups"
              :key="`group-${group.key}`"
              class="border border-slate-700 rounded"
            >
              <div class="px-3 py-2 border-b border-slate-700 font-bold" :class="group.headerClass">
                {{ group.label }} Matches
              </div>
              <div class="overflow-auto max-h-[260px]">
                <table class="min-w-full text-sm">
                  <thead class="bg-slate-700 sticky top-0">
                    <tr>
                      <th class="text-left p-2">No</th>
                      <th class="text-left p-2">DB ID</th>
                      <th class="text-left p-2">Red</th>
                      <th class="text-left p-2">Blue</th>
                      <th class="text-left p-2">Score</th>
                      <th class="text-left p-2">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="match in groupedMatches[group.key]"
                      :key="`match-${group.key}-${match.id}`"
                      class="border-t border-slate-700"
                    >
                      <td class="p-2 font-bold">{{ matchDisplayNumberById[match.id] }}</td>
                      <td class="p-2 text-slate-400">{{ match.id }}</td>
                      <td class="p-2 font-mono">{{ match.red_team_ids.join(', ') }}</td>
                      <td class="p-2 font-mono">{{ match.blue_team_ids.join(', ') }}</td>
                      <td class="p-2">{{ match.red_score }} - {{ match.blue_score }}</td>
                      <td class="p-2">
                        <div class="flex flex-wrap gap-2">
                          <button class="bg-purple-700 hover:bg-purple-600 rounded px-2 py-1" :disabled="loading" @click="startPrematch(match.id)">
                            Prematch
                          </button>
                          <button class="bg-green-700 hover:bg-green-600 rounded px-2 py-1" :disabled="loading" @click="startMatch(match.id)">
                            Start
                          </button>
                          <button class="bg-red-700 hover:bg-red-600 rounded px-2 py-1" :disabled="loading" @click="forceEndMatch(match.id)">
                            Force End
                          </button>
                          <button class="bg-amber-700 hover:bg-amber-600 rounded px-2 py-1" :disabled="loading" @click="replayMatch(match.id)">
                            Replay
                          </button>
                          <button class="bg-rose-800 hover:bg-rose-700 rounded px-2 py-1" :disabled="loading" @click="deleteMatch(match.id)">
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="groupedMatches[group.key].length === 0">
                      <td colspan="6" class="p-3 text-slate-400">No {{ group.label.toLowerCase() }} matches yet.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>
      </div>

      <section class="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h2 class="text-xl font-bold mb-4">Broadcast Controls</h2>
        <div class="flex flex-wrap gap-2">
          <button class="bg-indigo-700 hover:bg-indigo-600 rounded px-3 py-2" :disabled="loading" @click="broadcastWelcome">
            Welcome
          </button>
          <button class="bg-indigo-700 hover:bg-indigo-600 rounded px-3 py-2" :disabled="loading" @click="broadcastLeaderboard">
            Leaderboard
          </button>
          <button class="bg-orange-700 hover:bg-orange-600 rounded px-3 py-2" :disabled="loading" @click="recalculateRanking">
            Recalculate RP
          </button>
        </div>
      </section>

      <section class="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h2 class="text-xl font-bold mb-4">Video Yayın Kontrol</h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-3 items-end">
          <div class="lg:col-span-2">
            <label class="block text-xs text-slate-300 mb-1">Yayın URL</label>
            <input
              v-model="streamSettings.stream_url"
              class="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 font-mono text-sm"
              placeholder="http://localhost:8889/live/mfrc/"
              @input="streamDirty = true"
            />
          </div>
          <label class="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded px-3 py-2">
            <input
              v-model="streamSettings.stream_enabled"
              type="checkbox"
              class="accent-emerald-500"
              @change="streamDirty = true"
            />
            <span class="text-sm">Yayın Açık</span>
          </label>
        </div>

        <div class="flex flex-wrap gap-2 mt-3">
          <button class="bg-emerald-700 hover:bg-emerald-600 rounded px-3 py-2 text-sm" :disabled="loading" @click="saveStreamSettings">
            Ayarları Kaydet
          </button>
          <button class="bg-red-700 hover:bg-red-600 rounded px-3 py-2 text-sm" :disabled="loading" @click="disableStreamNow">
            Yayını Kes
          </button>
          <button class="bg-blue-700 hover:bg-blue-600 rounded px-3 py-2 text-sm" :disabled="loading" @click="enableStreamNow">
            Yayını Aç
          </button>
          <button class="bg-slate-700 hover:bg-slate-600 rounded px-3 py-2 text-sm" :disabled="loading" @click="refreshStreamStatus">
            Yayın Status Yenile
          </button>
        </div>

        <div class="mt-3 grid grid-cols-1 md:grid-cols-4 gap-2 text-sm">
          <div class="bg-slate-900 border border-slate-700 rounded px-3 py-2">
            <span class="text-slate-400">Durum:</span>
            <span class="ml-2 font-semibold" :class="streamSettings.stream_enabled ? 'text-emerald-300' : 'text-red-300'">
              {{ streamSettings.stream_enabled ? 'AÇIK' : 'KAPALI' }}
            </span>
          </div>
          <div class="bg-slate-900 border border-slate-700 rounded px-3 py-2 md:col-span-3">
            <span class="text-slate-400">Kaynak kontrol:</span>
            <span
              class="ml-2 font-semibold"
              :class="streamStatus?.reachable ? 'text-emerald-300' : 'text-amber-300'"
            >
              {{ streamStatusLabel }}
            </span>
          </div>
        </div>

        <div class="mt-4">
          <h3 class="text-sm font-semibold text-slate-300 mb-2">Yayın Önizleme (Admin)</h3>
          <div class="rounded border border-slate-700 overflow-hidden bg-black h-56">
            <iframe
              v-if="streamSettings.stream_enabled && adminStreamPreviewUrl"
              :src="adminStreamPreviewUrl"
              class="w-full h-full border-0"
              allow="autoplay; fullscreen; picture-in-picture"
            />
            <div
              v-else
              class="w-full h-full flex items-center justify-center text-slate-400 text-sm font-semibold"
            >
              Önizleme kapalı (yayın kapalı veya URL boş).
            </div>
          </div>
        </div>
      </section>

      <section class="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h2 class="text-xl font-bold mb-2">Status</h2>
        <p class="text-sm" :class="statusError ? 'text-red-300' : 'text-emerald-300'">{{ statusText }}</p>
        <p class="text-xs text-slate-400 mt-1">Canlı senkron: 2 sn | Son sync: {{ lastSyncedAt || '-' }}</p>
      </section>

      <section class="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-xl font-bold">Log Panel</h2>
          <button class="bg-slate-700 hover:bg-slate-600 rounded px-3 py-1 text-sm" @click="clearLogs">
            Clear
          </button>
        </div>
        <div class="h-64 overflow-auto border border-slate-700 rounded bg-slate-900">
          <div
            v-for="entry in logs"
            :key="entry.id"
            class="px-3 py-2 border-b border-slate-800 text-xs font-mono"
            :class="{
              'text-red-300': entry.level === 'error',
              'text-amber-300': entry.level === 'warn',
              'text-cyan-300': entry.level === 'event',
              'text-slate-200': entry.level === 'info',
            }"
          >
            [{{ entry.ts }}] {{ entry.message }}
          </div>
          <div v-if="logs.length === 0" class="p-3 text-xs text-slate-500">
            Henüz log yok.
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { matchBar, serverData } from "~/types"

type Team = {
  id: string
  name: string
  ranking_points: number
}

type Match = {
  id: number
  match_type: string
  red_team_ids: string[]
  blue_team_ids: string[]
  red_score: number
  blue_score: number
  winner: number
  played: boolean
  point_breakdown: Record<string, unknown>
}

type StreamSettings = {
  stream_url: string
  stream_enabled: boolean
}

type StreamStatus = {
  status: string
  reachable: boolean
  http_status: number | null
  detail: string | null
}

type TeamEdit = {
  name: string
  ranking_points: number
}

type MatchType = 'Qualification' | 'Elimination' | 'Final'

type LogLevel = 'info' | 'warn' | 'error' | 'event'
type LogEntry = {
  id: number
  ts: string
  level: LogLevel
  message: string
}

const { httpBase, wsUrl, streamEmbedUrl } = useBackendEndpoints()
const apiBase = computed(() => httpBase.replace(/\/$/, ''))
const { connect, disconnect } = useWebSocket()

const loading = ref(false)
const statusText = ref('Ready')
const statusError = ref(false)
const liveCountdown = ref<number | null>(null)
const lastSyncedAt = ref<string | null>(null)
const adminScrollEl = ref<HTMLElement | null>(null)

const teams = ref<Team[]>([])
const matches = ref<Match[]>([])
const teamEdits = ref<Record<string, TeamEdit>>({})
const dirtyTeamIds = ref<Set<string>>(new Set())
const logs = ref<LogEntry[]>([])
const streamSettings = ref<StreamSettings>({
  stream_url: streamEmbedUrl,
  stream_enabled: true,
})
const streamStatus = ref<StreamStatus | null>(null)
const streamDirty = ref(false)

const syncInFlight = ref(false)
const lastDataSignature = ref('')
const logSeq = ref(0)
const autoRefreshTimer = ref<ReturnType<typeof setInterval> | null>(null)
let wsSyncTimer: ReturnType<typeof setTimeout> | null = null
let isMiddleDragScroll = false
let dragStartY = 0
let dragStartX = 0
let startScrollTop = 0
let startScrollLeft = 0

const lastWsPage = ref<string | null>(null)
const lastWsAttacker = ref<number | null>(null)
const lastWsScoreCheck = ref<boolean | null>(null)
const matchTypeGroups: { key: MatchType; label: string; headerClass: string }[] = [
  { key: 'Qualification', label: 'Qualification', headerClass: 'text-emerald-300 bg-emerald-950/30' },
  { key: 'Elimination', label: 'Elimination', headerClass: 'text-amber-300 bg-amber-950/30' },
  { key: 'Final', label: 'Final', headerClass: 'text-fuchsia-300 bg-fuchsia-950/30' },
]

const newTeam = ref({ id: '', name: '' })
const matchForm = ref({
  match_type: 'Qualification' as MatchType,
  red: '',
  blue: '',
})

definePageMeta({
  layout: 'bottombar',
})

const nowLabel = (): string =>
  new Date().toLocaleTimeString('tr-TR', { hour12: false })

const pushLog = (message: string, level: LogLevel = 'info') => {
  logs.value.unshift({
    id: ++logSeq.value,
    ts: nowLabel(),
    level,
    message,
  })
  if (logs.value.length > 300) {
    logs.value = logs.value.slice(0, 300)
  }
}

const clearLogs = () => {
  logs.value = []
}

const setStatus = (text: string, isError = false) => {
  statusText.value = text
  statusError.value = isError
  pushLog(text, isError ? 'error' : 'info')
}

const parseApiError = (error: any): string => {
  return error?.data?.detail || error?.data?.message || error?.message || 'Unknown error'
}

const callApi = async <T>(path: string, options?: Parameters<typeof $fetch<T>>[1]): Promise<T> => {
  return await $fetch<T>(`${apiBase.value}${path}`, options)
}

const markTeamDirty = (teamId: string) => {
  dirtyTeamIds.value.add(teamId)
}

const buildDataSignature = (teamData: Team[], matchData: Match[], streamData: StreamSettings) => {
  return JSON.stringify({
    teams: teamData.map((team) => `${team.id}:${team.name}:${team.ranking_points}`),
    matches: matchData.map(
      (match) =>
        `${match.id}:${match.match_type}:${match.red_team_ids.join(',')}:${match.blue_team_ids.join(',')}:${match.red_score}:${match.blue_score}:${match.winner}:${Number(match.played)}`
    ),
    stream: `${streamData.stream_url}:${Number(streamData.stream_enabled)}`,
  })
}

const applyTeamData = (teamData: Team[]) => {
  const currentEdits = teamEdits.value
  const nextEdits: Record<string, TeamEdit> = {}
  const activeIds = new Set(teamData.map((team) => team.id))

  for (const dirtyId of Array.from(dirtyTeamIds.value)) {
    if (!activeIds.has(dirtyId)) {
      dirtyTeamIds.value.delete(dirtyId)
    }
  }

  for (const team of teamData) {
    const hasDirtyLocalEdit = dirtyTeamIds.value.has(team.id) && currentEdits[team.id]
    nextEdits[team.id] = hasDirtyLocalEdit
      ? { ...currentEdits[team.id] }
      : { name: team.name, ranking_points: team.ranking_points }
  }

  teams.value = teamData
  teamEdits.value = nextEdits
}

const groupedMatches = computed<Record<MatchType, Match[]>>(() => {
  return {
    Qualification: matches.value
      .filter((match) => match.match_type === 'Qualification')
      .sort((a, b) => a.id - b.id),
    Elimination: matches.value
      .filter((match) => match.match_type === 'Elimination')
      .sort((a, b) => a.id - b.id),
    Final: matches.value
      .filter((match) => match.match_type === 'Final')
      .sort((a, b) => a.id - b.id),
  }
})

const matchDisplayNumberById = computed<Record<number, number>>(() => {
  const map: Record<number, number> = {}
  for (const group of matchTypeGroups) {
    groupedMatches.value[group.key].forEach((match, index) => {
      map[match.id] = index + 1
    })
  }
  return map
})

const streamStatusLabel = computed(() => {
  if (!streamStatus.value) return 'Henüz kontrol edilmedi'
  const statusCode = streamStatus.value.http_status !== null ? ` (HTTP ${streamStatus.value.http_status})` : ''
  const detail = streamStatus.value.detail ? ` - ${streamStatus.value.detail}` : ''
  if (streamStatus.value.reachable) return `Ulaşılabilir${statusCode}${detail}`
  return `Ulaşılamıyor${statusCode}${detail}`
})

const adminStreamPreviewUrl = computed(() => streamSettings.value.stream_url.trim())

const syncAllData = async (source: 'initial' | 'poll' | 'ws' | 'action' = 'poll') => {
  if (syncInFlight.value) return

  syncInFlight.value = true
  try {
    const [teamData, matchData, streamData] = await Promise.all([
      callApi<Team[]>('/admin/teams'),
      callApi<Match[]>('/admin/matches'),
      callApi<StreamSettings>('/admin/stream-settings'),
    ])

    applyTeamData(teamData)
    matches.value = matchData
    if (!streamDirty.value) {
      streamSettings.value = {
        stream_url: streamData.stream_url,
        stream_enabled: streamData.stream_enabled,
      }
    }

    const nextSignature = buildDataSignature(teamData, matchData, streamData)
    const changed = nextSignature !== lastDataSignature.value
    const hadPreviousData = lastDataSignature.value.length > 0

    lastDataSignature.value = nextSignature
    lastSyncedAt.value = nowLabel()

    if (source === 'initial') {
      setStatus('Canlı veri senkronizasyonu aktif')
    } else if (changed && hadPreviousData) {
      pushLog(`Veri güncellendi (${source})`, 'event')
    }
  } catch (error: any) {
    const detail = parseApiError(error)
    if (source === 'initial') {
      setStatus(`İlk veri yükleme hatası: ${detail}`, true)
    } else {
      pushLog(`Senkron hatası (${source}): ${detail}`, 'warn')
    }
  } finally {
    syncInFlight.value = false
  }
}

const scheduleWebsocketSync = () => {
  if (wsSyncTimer) return
  wsSyncTimer = setTimeout(() => {
    wsSyncTimer = null
    void syncAllData('ws')
  }, 250)
}

const createTeam = async () => {
  loading.value = true
  try {
    await callApi('/admin/teams', {
      method: 'POST',
      body: {
        id: newTeam.value.id.trim(),
        name: newTeam.value.name.trim(),
      },
    })
    newTeam.value = { id: '', name: '' }
    await syncAllData('action')
    setStatus('Team created')
  } catch (error: any) {
    setStatus(`Create team failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const updateTeam = async (teamId: string) => {
  loading.value = true
  try {
    const edit = teamEdits.value[teamId]
    await callApi(`/admin/teams/${teamId}`, {
      method: 'PUT',
      body: {
        name: edit.name,
        ranking_points: Number(edit.ranking_points),
      },
    })
    dirtyTeamIds.value.delete(teamId)
    await syncAllData('action')
    setStatus(`Team ${teamId} updated`)
  } catch (error: any) {
    setStatus(`Update team failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const deleteTeam = async (teamId: string) => {
  if (!confirm(`Delete team ${teamId}?`)) {
    return
  }

  loading.value = true
  try {
    await callApi(`/admin/teams/${teamId}`, { method: 'DELETE' })
    dirtyTeamIds.value.delete(teamId)
    await syncAllData('action')
    setStatus(`Team ${teamId} deleted`)
  } catch (error: any) {
    setStatus(`Delete team failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const parseIds = (raw: string): string[] => {
  return raw
    .split(',')
    .map((x) => x.trim())
    .filter((x) => x.length > 0)
}

const createMatch = async () => {
  const red = parseIds(matchForm.value.red)
  const blue = parseIds(matchForm.value.blue)

  if (red.length === 0 || blue.length === 0) {
    setStatus('Red and blue team lists are required', true)
    return
  }

  loading.value = true
  try {
    await callApi('/admin/matches', {
      method: 'POST',
      body: {
        match_type: matchForm.value.match_type,
        red_team_ids: red,
        blue_team_ids: blue,
      },
    })
    matchForm.value.red = ''
    matchForm.value.blue = ''
    await syncAllData('action')
    setStatus('Match created')
  } catch (error: any) {
    setStatus(`Create match failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const startPrematch = async (matchId: number) => {
  loading.value = true
  try {
    await callApi(`/admin/matches/${matchId}/prematch`, { method: 'POST' })
    await syncAllData('action')
    setStatus(`Prematch started for match ${matchId}`)
  } catch (error: any) {
    setStatus(`Prematch failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const startMatch = async (matchId: number) => {
  loading.value = true
  try {
    await callApi(`/admin/matches/${matchId}/start`, { method: 'POST' })
    await syncAllData('action')
    setStatus(`Match ${matchId} started`)
  } catch (error: any) {
    setStatus(`Start match failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const forceEndMatch = async (matchId: number) => {
  loading.value = true
  try {
    await callApi(`/admin/matches/${matchId}/force-end`, { method: 'POST' })
    await syncAllData('action')
    setStatus(`Force end requested for match ${matchId}`)
  } catch (error: any) {
    setStatus(`Force end failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const replayMatch = async (matchId: number) => {
  if (!confirm(`Replay match ${matchId}? Previous RP from this match will be removed.`)) {
    return
  }

  loading.value = true
  try {
    await callApi(`/admin/matches/${matchId}/replay`, { method: 'POST' })
    await syncAllData('action')
    setStatus(`Match ${matchId} is ready for replay`)
  } catch (error: any) {
    setStatus(`Replay failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const deleteMatch = async (matchId: number) => {
  if (!confirm(`Delete match ${matchId}? RP gained from this match will be removed.`)) {
    return
  }

  loading.value = true
  try {
    await callApi(`/admin/matches/${matchId}`, { method: 'DELETE' })
    await syncAllData('action')
    setStatus(`Match ${matchId} deleted`)
  } catch (error: any) {
    setStatus(`Delete match failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const broadcastWelcome = async () => {
  loading.value = true
  try {
    await callApi('/admin/welcome', { method: 'POST' })
    setStatus('Welcome broadcast sent')
  } catch (error: any) {
    setStatus(`Welcome broadcast failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const broadcastLeaderboard = async () => {
  loading.value = true
  try {
    await callApi('/admin/leaderboard/broadcast', { method: 'POST' })
    setStatus('Leaderboard broadcast sent')
  } catch (error: any) {
    setStatus(`Leaderboard broadcast failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const recalculateRanking = async () => {
  loading.value = true
  try {
    await callApi('/admin/recalculate-ranking', { method: 'POST' })
    await syncAllData('action')
    setStatus('Ranking recalculated from played matches')
  } catch (error: any) {
    setStatus(`Recalculate ranking failed: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const saveStreamSettings = async () => {
  const streamUrl = streamSettings.value.stream_url.trim()
  if (!streamUrl) {
    setStatus('Yayın URL boş olamaz', true)
    return
  }

  loading.value = true
  try {
    const updated = await callApi<StreamSettings>('/admin/stream-settings', {
      method: 'PUT',
      body: {
        stream_url: streamUrl,
        stream_enabled: streamSettings.value.stream_enabled,
      },
    })
    streamSettings.value = updated
    streamDirty.value = false
    await refreshStreamStatus()
    await syncAllData('action')
    setStatus('Yayın ayarları güncellendi')
  } catch (error: any) {
    setStatus(`Yayın ayarı güncelleme hatası: ${parseApiError(error)}`, true)
  } finally {
    loading.value = false
  }
}

const disableStreamNow = async () => {
  streamSettings.value.stream_enabled = false
  streamDirty.value = true
  await saveStreamSettings()
}

const enableStreamNow = async () => {
  streamSettings.value.stream_enabled = true
  streamDirty.value = true
  await saveStreamSettings()
}

const refreshStreamStatus = async () => {
  try {
    streamStatus.value = await callApi<StreamStatus>('/admin/stream-status')
    pushLog(
      `Yayın status: ${streamStatus.value.reachable ? 'ulaşılabilir' : 'ulaşılamıyor'}${
        streamStatus.value.http_status !== null ? ` (HTTP ${streamStatus.value.http_status})` : ''
      }`,
      streamStatus.value.reachable ? 'info' : 'warn'
    )
  } catch (error: any) {
    pushLog(`Yayın status alınamadı: ${parseApiError(error)}`, 'warn')
  }
}

const stopMiddleDragScroll = () => {
  if (!isMiddleDragScroll) return
  isMiddleDragScroll = false
  document.removeEventListener('mousemove', onMiddleDragMove)
  document.removeEventListener('mouseup', stopMiddleDragScroll)
  document.body.style.userSelect = ''
  document.body.style.cursor = ''
}

const onMiddleDragMove = (event: MouseEvent) => {
  if (!isMiddleDragScroll || !adminScrollEl.value) return
  const deltaY = event.clientY - dragStartY
  const deltaX = event.clientX - dragStartX
  adminScrollEl.value.scrollTop = startScrollTop - deltaY
  adminScrollEl.value.scrollLeft = startScrollLeft - deltaX
}

const onAdminMouseDown = (event: MouseEvent) => {
  if (event.button !== 1 || !adminScrollEl.value) return
  event.preventDefault()
  isMiddleDragScroll = true
  dragStartY = event.clientY
  dragStartX = event.clientX
  startScrollTop = adminScrollEl.value.scrollTop
  startScrollLeft = adminScrollEl.value.scrollLeft
  document.addEventListener('mousemove', onMiddleDragMove)
  document.addEventListener('mouseup', stopMiddleDragScroll)
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'grabbing'
}

const handleLiveBroadcast = (payload: serverData) => {
  if (lastWsPage.value !== payload.page) {
    pushLog(`Yayın ekranı değişti: ${payload.page}`, 'event')
    lastWsPage.value = payload.page
  }

  if (payload.page !== 'matchbar') {
    liveCountdown.value = null
    lastWsAttacker.value = null
    lastWsScoreCheck.value = null
    scheduleWebsocketSync()
    return
  }

  const data = payload.data as matchBar
  liveCountdown.value = typeof data.preStartCountdown === 'number' ? data.preStartCountdown : null

  if (lastWsAttacker.value !== null && lastWsAttacker.value !== data.attackerAlliance) {
    const allianceLabel =
      data.attackerAlliance === 0 ? 'KIRMIZI' : data.attackerAlliance === 1 ? 'MAVİ' : 'ENDGAME'
    pushLog(`Alliance shift: ${allianceLabel}`, 'event')
  }
  if (lastWsScoreCheck.value === false && data.scoreCheckInProgress) {
    pushLog('Score check başladı', 'event')
  }

  lastWsAttacker.value = data.attackerAlliance
  lastWsScoreCheck.value = data.scoreCheckInProgress
  scheduleWebsocketSync()
}

onMounted(async () => {
  pushLog('Admin panel açıldı', 'info')
  connect(wsUrl, handleLiveBroadcast)
  await syncAllData('initial')
  await refreshStreamStatus()
  autoRefreshTimer.value = setInterval(() => {
    void syncAllData('poll')
  }, 2000)
})

onBeforeUnmount(() => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value)
    autoRefreshTimer.value = null
  }
  if (wsSyncTimer) {
    clearTimeout(wsSyncTimer)
    wsSyncTimer = null
  }
  stopMiddleDragScroll()
  disconnect()
})
</script>
