<template>
  <div class="stadium-map-view">

    <!-- ── Loading ── -->
    <div v-if="loading" class="state-block">
      <span class="spinner" />
      <p>Loading stadium map…</p>
    </div>

    <!-- ── Error ── -->
    <div v-else-if="error" class="state-block state-error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadMapData">Retry</button>
    </div>

    <template v-else-if="mapData">

      <!-- ── Header ── -->
      <div class="controls">
        <div class="stadium-meta">
          <p class="stadium-name">{{ mapData.stadium_name }}</p>
          <p class="stadium-sub">{{ mapData.city }}, {{ mapData.country }}</p>
        </div>

        <div class="mode-tabs">
          <button
            v-for="m in MODES"
            :key="m.value"
            :class="['tab-btn', { active: mode === m.value }]"
            @click="setMode(m.value)"
          >
            {{ m.label }}
          </button>
        </div>
      </div>

      <!-- ── Heat index banner (when present) ── -->
      <div
        v-if="mapData.weather?.heat_index != null"
        :class="['heat-banner', heatIndexClass(mapData.weather.heat_index)]"
      >
        <span class="heat-label">Heat index</span>
        <span class="heat-value">{{ mapData.weather.heat_index }}°C</span>
        <span class="heat-desc">— {{ getHeatIndexDescription(mapData.weather.heat_index) }}</span>
      </div>

      <!-- ── Map component ── -->
      <StadiumMap
        :zones="zones"
        :mode="mode"
        :selected-id="selectedZone?.id ?? null"
        :selected-zone="selectedZone"
        @select-zone="handleZoneSelect"
      />

      <!-- ── Zone card grid ── -->
      <div class="zone-grid">
        <div
          v-for="zone in zones"
          :key="zone.id"
          :class="['zone-card', { active: selectedZone?.id === zone.id }]"
          @click="handleZoneSelect(zone)"
        >
          <div class="zone-card-header">
            <p class="zone-card-name">{{ zone.name }}</p>
            <span :class="['risk-badge', `risk-${zone.level}`]">{{ capitalize(zone.level) }}</span>
          </div>
          <p class="zone-card-meta">
            Risk: {{ zone.score }}/100 · Sun: {{ pct(zone.sun) }} · Air: {{ pct(zone.airflow) }}
          </p>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { matchAPI } from '@/services/api'
import StadiumMap from '@/components/StadiumMap.vue'

// ─── Constants ────────────────────────────────────────────────────────────────

const MODES = [
  { value: 'seating', label: 'Seating zones' },
  { value: 'pitch',   label: 'Pitch zones'   },
]

// ─── State ────────────────────────────────────────────────────────────────────

const route        = useRoute()
const loading      = ref(true)
const error        = ref(null)
const mapData      = ref(null)
const matchId      = ref(null)
const mode         = ref('seating')
const selectedZone = ref(null)

// ─── Data fetching ────────────────────────────────────────────────────────────

onMounted(loadMapData)

async function loadMapData() {
  loading.value = true
  error.value   = null

  try {
    matchId.value = parseInt(route.params.matchId)
    const response = await matchAPI.getMatchPreview(matchId.value)
    mapData.value  = response.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load stadium map data'
    console.error('Error loading map:', err)
  } finally {
    loading.value = false
  }
}

// ─── Zone derivation ──────────────────────────────────────────────────────────
//
// The API returns pre-scored zones inside player_risk.zone_risks (pitch) and
// fan_risk.zone_risks (seating). We normalise both shapes into the flat zone
// object that StadiumMap.vue expects, using the API's risk_score / risk_level
// directly rather than recomputing them locally.

const zones = computed(() => {
  if (!mapData.value) return []

  const riskData = mode.value === 'pitch'
    ? mapData.value.player_risk
    : mapData.value.fan_risk

  return getZonesFromRisk(riskData, mode.value)
})

/**
 * Normalise a risk block (player_risk or fan_risk) into the zone array shape
 * consumed by StadiumMap.vue.
 *
 * @param {Object} riskData  - player_risk or fan_risk from the API response
 * @param {'pitch'|'seating'} type
 * @returns {Array}
 */
function getZonesFromRisk(riskData, type) {
  const zoneRisks = riskData?.zone_risks || {}

  return Object.entries(zoneRisks).map(([zoneId, z]) => ({
    // StadiumMap uses `id`, `name`, `sun`, `airflow`, `has_roof`, `score`, `level`
    id:       zoneId,
    name:     z.zone_name  || zoneId,
    zone_type: type,
    sun:      z.sun_exposure    ?? 0.5,
    airflow:  z.airflow_quality ?? 0.5,
    has_roof: z.has_roof,
    score:    z.risk_score  ?? 0,
    level:    z.risk_level  || 'low',
  }))
}

// ─── High-risk / safe-zone helpers (available to parent via expose if needed) ─

const highRiskZones = computed(() =>
  [...getZonesFromRisk(mapData.value?.player_risk, 'pitch'),
   ...getZonesFromRisk(mapData.value?.fan_risk,    'seating')]
    .filter(z => z.score > 70)
    .slice(0, 5)
)

const safeZones = computed(() =>
  [...getZonesFromRisk(mapData.value?.player_risk, 'pitch'),
   ...getZonesFromRisk(mapData.value?.fan_risk,    'seating')]
    .filter(z => z.score < 40)
    .slice(0, 5)
)

defineExpose({ highRiskZones, safeZones })

// ─── Handlers ─────────────────────────────────────────────────────────────────

function setMode(m) {
  mode.value         = m
  selectedZone.value = null
}

/** Toggle-to-deselect; also handles null emitted by the tooltip close button. */
function handleZoneSelect(zone) {
  if (!zone || selectedZone.value?.id === zone.id) {
    selectedZone.value = null
  } else {
    selectedZone.value = zone
  }
}

// ─── Formatting / display helpers ────────────────────────────────────────────

function pct(val) {
  return `${Math.round((val ?? 0) * 100)}%`
}

function capitalize(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : ''
}

function getHeatIndexDescription(heatIndex) {
  if (heatIndex < 27) return 'Comfortable'
  if (heatIndex < 32) return 'Caution advised'
  if (heatIndex < 39) return 'Extreme caution'
  if (heatIndex < 51) return 'Danger'
  return 'Extreme danger'
}

function heatIndexClass(heatIndex) {
  if (heatIndex < 27) return 'heat-low'
  if (heatIndex < 32) return 'heat-moderate'
  if (heatIndex < 39) return 'heat-high'
  return 'heat-critical'
}

function getRiskColor(level) {
  const map = {
    low:      'text-green-600',
    moderate: 'text-yellow-600',
    high:     'text-orange-600',
    critical: 'text-red-600',
  }
  return map[level] ?? 'text-gray-600'
}
</script>

<style scoped>
.stadium-map-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: var(--font-sans, system-ui, sans-serif);
}

/* ── Loading / error states ── */
.state-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 0;
  color: #888;
  font-size: 14px;
}

.state-error { color: #A32D2D; }

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #e0e0dc;
  border-top-color: #378ADD;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.retry-btn {
  padding: 5px 16px;
  font-size: 13px;
  border: 0.5px solid #ccc;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
}
.retry-btn:hover { background: #f5f5f3; }

/* ── Controls ── */
.controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.stadium-meta { flex: 1; }

.stadium-name {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.3;
}

.stadium-sub {
  margin: 2px 0 0;
  font-size: 12px;
  color: #888;
}

.mode-tabs {
  display: flex;
  gap: 6px;
  margin-left: auto;
}

.tab-btn {
  padding: 5px 14px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  border: 0.5px solid #ccc;
  background: transparent;
  color: #666;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}

.tab-btn.active {
  background: #222;
  color: #fff;
  border-color: transparent;
}

.tab-btn:not(.active):hover {
  background: #f5f5f3;
  border-color: #bbb;
}

/* ── Heat index banner ── */
.heat-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 13px;
  border: 0.5px solid transparent;
}

.heat-label { color: inherit; opacity: 0.7; }
.heat-value { font-weight: 500; }
.heat-desc  { opacity: 0.8; }

.heat-low      { background: #EAF3DE; color: #3B6D11; border-color: #C0DD97; }
.heat-moderate { background: #FAEEDA; color: #854F0B; border-color: #FAC775; }
.heat-high     { background: #FAECE7; color: #993C1D; border-color: #F5C4B3; }
.heat-critical { background: #FCEBEB; color: #A32D2D; border-color: #F7C1C1; }

/* ── Zone card grid ── */
.zone-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

.zone-card {
  cursor: pointer;
  padding: 10px 12px;
  border: 0.5px solid #e0e0dc;
  border-radius: 8px;
  background: #fff;
  transition: border-color 0.15s, background 0.15s;
}

.zone-card:hover {
  border-color: #bbb;
  background: #fafaf8;
}

.zone-card.active {
  border: 1.5px solid #378ADD;
  background: #EAF3FB;
}

.zone-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.zone-card-name {
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.3;
}

.zone-card-meta {
  margin: 4px 0 0;
  font-size: 12px;
  color: #888;
}

/* ── Risk badges ── */
.risk-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 500;
  padding: 2px 9px;
  border-radius: 99px;
  white-space: nowrap;
  flex-shrink: 0;
}
.risk-low      { background: #EAF3DE; color: #3B6D11; }
.risk-moderate { background: #FAEEDA; color: #854F0B; }
.risk-high     { background: #FAECE7; color: #993C1D; }
.risk-critical { background: #FCEBEB; color: #A32D2D; }
</style>
