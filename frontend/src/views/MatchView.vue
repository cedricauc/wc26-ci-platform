<template>
  <div class="match-view">
    <!-- Loading -->
    <div v-if="loading" class="state-center">
      <i class="ti ti-loader-2 spin"></i>
      <span>Loading match data…</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert--error">
      <i class="ti ti-alert-circle"></i>
      {{ error }}
    </div>

    <div v-else-if="matchData" class="stack">

      <!-- ── Match header ─────────────────────────── -->
      <div class="card">
        <div class="match-header">
          <div>
            <h1 class="match-title">
              {{ matchData.match.home_team }}
              <span class="vs">vs</span>
              {{ matchData.match.away_team }}
            </h1>
            <p class="match-date">
              <i class="ti ti-calendar"></i>
              {{ formatDate(matchData.match.kickoff_datetime) }}
            </p>
          </div>
          <span :class="['badge', 'badge--overall', getOverallRiskClass()]">
            {{ getOverallRiskLevel() }}
          </span>
        </div>

        <div class="meta-grid">
          <div class="meta-tile">
            <p class="meta-label">Stadium</p>
            <p class="meta-value">{{ matchData.match.stadium_data.name }}</p>
            <p class="meta-sub">{{ matchData.match.city }}, {{ matchData.match.country }}</p>
          </div>
          <div class="meta-tile">
            <p class="meta-label">Stage</p>
            <p class="meta-value">{{ matchData.match.stage }}</p>
            <p v-if="matchData.match.group_name" class="meta-sub">{{ matchData.match.group_name }}</p>
          </div>
          <div class="meta-tile">
            <p class="meta-label">Kickoff</p>
            <p class="meta-value">{{ formatTime(matchData.match.kickoff_datetime) }}</p>
          </div>
        </div>
      </div>

      <!-- ── Weather ──────────────────────────────── -->
      <div class="card">
        <h2 class="section-title">
          <i class="ti ti-cloud"></i> Weather forecast
        </h2>
        <div class="weather-grid">
          <div class="metric-tile">
            <p class="metric-label">Temperature</p>
            <p class="metric-value metric-value--heat">
              {{ matchData.weather_forecast.temperature }}<sup>°C</sup>
            </p>
          </div>
          <div class="metric-tile">
            <p class="metric-label">Humidity</p>
            <p class="metric-value metric-value--purple">
              {{ matchData.weather_forecast.humidity }}<sup>%</sup>
            </p>
          </div>
          <div class="metric-tile">
            <p class="metric-label">Heat index</p>
            <p class="metric-value metric-value--amber">
              {{ matchData.weather_forecast.heat_index }}<sup>°C</sup>
            </p>
          </div>
          <div class="metric-tile">
            <p class="metric-label">UV index</p>
            <p class="metric-value metric-value--red">
              {{ matchData.weather_forecast.uv_index || '—' }}
            </p>
          </div>
        </div>
      </div>

      <!-- ── Risk panels ──────────────────────────── -->
      <div class="two-col">

        <!-- Player risk -->
        <div class="card">
          <h3 class="section-title">
            <i class="ti ti-run"></i> Player risk
          </h3>
          <div class="risk-header">
            <span class="body-muted">Risk score</span>
            <span :class="['badge', getRiskClass(matchData.player_risk.risk_level)]">
              {{ matchData.player_risk.risk_level }}
            </span>
          </div>
          <div class="progress-track">
            <div
              :class="['progress-fill', getBarClass(matchData.player_risk.risk_level)]"
              :style="{ width: matchData.player_risk.risk_score + '%' }"
            ></div>
          </div>
          <p class="progress-label">{{ matchData.player_risk.risk_score }} / 100</p>

          <div class="stat-rows">
            <div class="stat-row">
              <span>Heat stress</span>
              <strong>{{ matchData.player_risk.heat_stress_factor }}</strong>
            </div>
            <div class="stat-row">
              <span>Humidity impact</span>
              <strong>{{ matchData.player_risk.humidity_factor }}</strong>
            </div>
            <div class="stat-row">
              <span>UV exposure</span>
              <strong>{{ matchData.player_risk.uv_factor }}</strong>
            </div>
          </div>

          <div v-if="matchData.player_risk.cooling_breaks_recommended" class="alert alert--warning">
            <i class="ti ti-alert-triangle"></i>
            Cooling breaks recommended
          </div>
        </div>

        <!-- Fan risk -->
        <div class="card">
          <h3 class="section-title">
            <i class="ti ti-users"></i> Fan safety
          </h3>
          <div class="risk-header">
            <span class="body-muted">Risk score</span>
            <span :class="['badge', getRiskClass(matchData.fan_risk.risk_level)]">
              {{ matchData.fan_risk.risk_level }}
            </span>
          </div>
          <div class="progress-track">
            <div
              :class="['progress-fill', getBarClass(matchData.fan_risk.risk_level)]"
              :style="{ width: matchData.fan_risk.risk_score + '%' }"
            ></div>
          </div>
          <p class="progress-label">{{ matchData.fan_risk.risk_score }} / 100</p>

          <div class="stat-rows">
            <div class="stat-row">
              <span>Heat stress</span>
              <strong>{{ matchData.fan_risk.heat_stress_factor }}</strong>
            </div>
            <div class="stat-row">
              <span>Humidity impact</span>
              <strong>{{ matchData.fan_risk.humidity_factor }}</strong>
            </div>
            <div class="stat-row">
              <span>UV exposure</span>
              <strong>{{ matchData.fan_risk.uv_factor }}</strong>
            </div>
          </div>

          <div
            v-if="matchData.fan_risk.high_risk_zones?.length"
            class="alert alert--error"
          >
            <i class="ti ti-alert-circle"></i>
            High-risk seating areas detected
          </div>
        </div>
      </div>

      <!-- ── Recommendations ──────────────────────── -->
      <div class="two-col">

        <!-- Player recommendations -->
        <div class="card">
          <h3 class="section-title">
            <i class="ti ti-clipboard-list"></i> Player recommendations
          </h3>
          <div class="rec-list">
            <div
              v-for="(rec, i) in matchData.player_recommendations"
              :key="i"
              class="rec-card rec-card--blue"
            >
              <div class="rec-header">
                <span class="rec-title">{{ rec.title }}</span>
                <span :class="['badge', 'badge--sm', getPriorityClass(rec.priority)]">
                  {{ rec.priority }}
                </span>
              </div>
              <p class="rec-desc">{{ rec.description }}</p>
              <p v-if="rec.timing" class="rec-timing">
                <i class="ti ti-clock"></i> {{ rec.timing }}
              </p>
            </div>
          </div>
        </div>

        <!-- Fan recommendations -->
        <div class="card">
          <h3 class="section-title">
            <i class="ti ti-shield-check"></i> Fan safety recommendations
          </h3>
          <div class="rec-list">
            <div
              v-for="(rec, i) in matchData.fan_recommendations"
              :key="i"
              class="rec-card rec-card--teal"
            >
              <div class="rec-header">
                <span class="rec-title">{{ rec.title }}</span>
                <span :class="['badge', 'badge--sm', getPriorityClass(rec.priority)]">
                  {{ rec.priority }}
                </span>
              </div>
              <p class="rec-desc">{{ rec.description }}</p>
              <p v-if="rec.timing" class="rec-timing">
                <i class="ti ti-clock"></i> {{ rec.timing }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Stadium map CTA ──────────────────────── -->
      <div class="card card--cta">
        <h3 class="section-title" style="justify-content: center">
          <i class="ti ti-map"></i> Interactive stadium map
        </h3>
        <p class="body-muted">View detailed heat-risk zones on an interactive stadium map</p>
        <router-link
          :to="`/stadium-map/${matchData.match.match_number}`"
          class="btn-primary"
        >
          <i class="ti ti-map-2"></i> View stadium map
        </router-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { matchAPI } from '@/services/api'
import { format, parseISO } from 'date-fns'

const route = useRoute()
const loading = ref(true)
const error   = ref(null)
const matchData = ref(null)

onMounted(async () => {
  await loadMatchData()
})

const loadMatchData = async () => {
  loading.value = true
  error.value   = null
  try {
    const matchId = parseInt(route.params.id)
    const response = await matchAPI.getMatchPreview(matchId)
    matchData.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load match data'
    console.error('Error loading match:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (d) => format(parseISO(d), 'EEEE, MMMM d, yyyy')
const formatTime = (d) => format(parseISO(d), 'h:mm a')

const getRiskClass = (level) => ({
  low:      'badge--low',
  moderate: 'badge--moderate',
  high:     'badge--high',
  critical: 'badge--critical',
}[level] ?? 'badge--neutral')

const getBarClass = (level) => ({
  low:      'fill--low',
  moderate: 'fill--moderate',
  high:     'fill--high',
  critical: 'fill--critical',
}[level] ?? 'fill--neutral')

const getPriorityClass = (p) => ({
  critical: 'badge--critical',
  high:     'badge--high',
  medium:   'badge--moderate',
  low:      'badge--low',
}[p] ?? 'badge--neutral')

const getOverallRiskLevel = () => {
  if (!matchData.value) return 'Unknown'
  const avg = (matchData.value.player_risk.risk_score + matchData.value.fan_risk.risk_score) / 2
  if (avg < 40) return 'Low risk'
  if (avg < 65) return 'Moderate risk'
  if (avg < 85) return 'High risk'
  return 'Critical risk'
}

const getOverallRiskClass = () => {
  if (!matchData.value) return 'badge--neutral'
  const avg = (matchData.value.player_risk.risk_score + matchData.value.fan_risk.risk_score) / 2
  if (avg < 40) return 'badge--low'
  if (avg < 65) return 'badge--moderate'
  if (avg < 85) return 'badge--high'
  return 'badge--critical'
}
</script>

<style scoped>
/* ── Reset & base ───────────────────────────────────── */
*,
*::before,
*::after { box-sizing: border-box; }

.match-view {
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 15px;
  line-height: 1.6;
  color: #1a1a1a;
  padding: 1.5rem;
  max-width: 900px;
  margin: 0 auto;
}

/* ── Layout helpers ─────────────────────────────────── */
.stack { display: flex; flex-direction: column; gap: 1rem; }

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 640px) {
  .two-col { grid-template-columns: 1fr; }
}

/* ── Cards ──────────────────────────────────────────── */
.card {
  background: #fff;
  border: 0.5px solid rgba(0, 0, 0, 0.12);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
}

.card--cta {
  text-align: center;
  padding: 1.75rem;
}

/* ── States ─────────────────────────────────────────── */
.state-center {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 3rem;
  color: #6b7280;
  font-size: 15px;
}

.spin {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Match header ───────────────────────────────────── */
.match-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.match-title {
  font-size: 22px;
  font-weight: 500;
  margin: 0 0 4px;
  line-height: 1.3;
}

.match-title .vs {
  font-weight: 400;
  color: #9ca3af;
  margin: 0 4px;
}

.match-date {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* ── Meta grid (stadium / stage / kickoff) ──────────── */
.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

@media (max-width: 480px) {
  .meta-grid { grid-template-columns: 1fr 1fr; }
}

.meta-tile {
  background: #f9fafb;
  border-radius: 8px;
  padding: 10px 12px;
}

.meta-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
  margin: 0 0 3px;
}

.meta-value {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 2px;
}

.meta-sub {
  font-size: 12px;
  color: #9ca3af;
  margin: 0;
}

/* ── Section title ──────────────────────────────────── */
.section-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 15px;
  font-weight: 500;
  margin: 0 0 1rem;
  color: #374151;
}

.section-title i { color: #6b7280; font-size: 17px; }

/* ── Weather grid ───────────────────────────────────── */
.weather-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

@media (max-width: 480px) {
  .weather-grid { grid-template-columns: repeat(2, 1fr); }
}

.metric-tile {
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.metric-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
  margin: 0 0 6px;
}

.metric-value {
  font-size: 24px;
  font-weight: 500;
  margin: 0;
  line-height: 1;
}

.metric-value sup { font-size: 13px; font-weight: 400; }

.metric-value--heat   { color: #d85a30; }
.metric-value--purple { color: #534ab7; }
.metric-value--amber  { color: #ba7517; }
.metric-value--red    { color: #e24b4a; }

/* ── Risk block ─────────────────────────────────────── */
.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.progress-track {
  background: rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  height: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 6px;
  border-radius: 20px;
  transition: width 0.4s ease;
}

.fill--low      { background: #639922; }
.fill--moderate { background: #ef9f27; }
.fill--high     { background: #d85a30; }
.fill--critical { background: #e24b4a; }
.fill--neutral  { background: #9ca3af; }

.progress-label {
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
  margin: 4px 0 12px;
}

/* ── Stat rows ──────────────────────────────────────── */
.stat-rows { margin-bottom: 12px; }

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  font-size: 13px;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.07);
  color: #4b5563;
}

.stat-row:last-child { border-bottom: none; }
.stat-row strong { color: #1a1a1a; }

/* ── Alerts ─────────────────────────────────────────── */
.alert {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  border: 0.5px solid;
}

.alert--warning {
  background: #faeeda;
  color: #633806;
  border-color: #ef9f27;
}

.alert--error {
  background: #fcebeb;
  color: #501313;
  border-color: #e24b4a;
}

/* ── Badges ─────────────────────────────────────────── */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
  white-space: nowrap;
  text-transform: capitalize;
}

.badge--sm { font-size: 11px; padding: 2px 8px; }

.badge--low      { background: #eaf3de; color: #27500a; }
.badge--moderate { background: #faeeda; color: #633806; }
.badge--high     { background: #faece7; color: #4a1b0c; }
.badge--critical { background: #fcebeb; color: #501313; }
.badge--neutral  { background: #f3f4f6; color: #374151; }

.badge--overall  { font-size: 13px; }

/* ── Recommendation cards ───────────────────────────── */
.rec-list { display: flex; flex-direction: column; gap: 8px; }

.rec-card {
  border-radius: 8px;
  padding: 12px 14px;
  border: 0.5px solid;
}

.rec-card--blue { background: #e6f1fb; border-color: #85b7eb; }
.rec-card--teal { background: #e1f5ee; border-color: #5dcaa5; }

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 4px;
}

.rec-title {
  font-size: 14px;
  font-weight: 500;
  color: #0c447c;
}

.rec-card--teal .rec-title { color: #085041; }

.rec-desc {
  font-size: 13px;
  color: #185fa5;
  margin: 0;
  line-height: 1.5;
}

.rec-card--teal .rec-desc { color: #0f6e56; }

.rec-timing {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #378add;
  margin: 6px 0 0;
}

.rec-card--teal .rec-timing { color: #1d9e75; }

/* ── CTA button ─────────────────────────────────────── */
.card--cta p { color: #6b7280; font-size: 14px; margin: 0 0 1rem; }

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 10px 22px;
  background: #1a1a1a;
  color: #fff;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: opacity 0.15s;
}

.btn-primary:hover { opacity: 0.82; }

/* ── Utility ─────────────────────────────────────────── */
.body-muted { font-size: 13px; color: #6b7280; }
</style>