<template>
  <div class="stadium-map-wrap">
    <!-- SVG canvas -->
    <div class="map-canvas">
      <svg :viewBox="`0 0 ${W} ${H}`" width="100%" style="display: block;">

        <!-- ── SEATING MODE ── -->
        <template v-if="mode === 'seating'">
          <!-- Arc segments -->
          <g
            v-for="seg in seatingSegments"
            :key="seg.zone.id"
            class="zone-seg"
            @click="$emit('select-zone', seg.zone)"
          >
            <path
              :d="seg.d"
              :fill="riskRgba(seg.zone.level, 0.78)"
              :stroke="selectedId === seg.zone.id ? '#378ADD' : '#fff'"
              :stroke-width="selectedId === seg.zone.id ? 2.5 : 1.5"
              :opacity="selectedId === seg.zone.id ? 1 : 0.85"
            />
            <text
              :x="seg.lx" :y="seg.ly"
              text-anchor="middle" dominant-baseline="middle"
              font-size="11" font-weight="500" fill="#333"
              style="pointer-events: none; user-select: none;"
            >{{ seg.label }}</text>
          </g>

          <!-- Pitch rectangle in center -->
          <rect
            :x="pitchRect.x" :y="pitchRect.y"
            :width="pitchRect.w" :height="pitchRect.h"
            rx="6"
            fill="rgba(99,153,34,0.15)"
            stroke="rgba(99,153,34,0.35)"
            stroke-width="1.5"
          />
          <text
            :x="cx" :y="cy"
            text-anchor="middle" dominant-baseline="middle"
            font-size="12" font-weight="500" fill="rgba(59,109,17,0.7)"
            style="pointer-events: none;"
          >Pitch</text>
        </template>

        <!-- ── PITCH MODE ── -->
        <template v-else>
          <!-- Pitch background -->
          <rect
            :x="pitchBg.x" :y="pitchBg.y"
            :width="pitchBg.w" :height="pitchBg.h"
            rx="6"
            fill="rgba(99,153,34,0.1)"
            stroke="rgba(99,153,34,0.3)"
            stroke-width="1.5"
          />
          <!-- Center line -->
          <line
            :x1="pitchBg.x" :y1="pitchBg.y + pitchBg.h / 2"
            :x2="pitchBg.x + pitchBg.w" :y2="pitchBg.y + pitchBg.h / 2"
            stroke="rgba(99,153,34,0.25)" stroke-width="1" stroke-dasharray="6 4"
          />
          <!-- Center circle -->
          <circle
            :cx="pitchBg.x + pitchBg.w / 2" :cy="pitchBg.y + pitchBg.h / 2"
            :r="pitchCircleR"
            fill="none" stroke="rgba(99,153,34,0.25)" stroke-width="1"
          />
          <!-- Zone cells -->
          <g
            v-for="cell in pitchCells"
            :key="cell.zone.id"
            class="zone-seg"
            @click="$emit('select-zone', cell.zone)"
          >
            <rect
              :x="cell.x + 3" :y="cell.y + 3"
              :width="cell.w - 6" :height="cell.h - 6"
              rx="5"
              :fill="riskRgba(cell.zone.level, 0.78)"
              :stroke="selectedId === cell.zone.id ? '#378ADD' : 'rgba(255,255,255,0.6)'"
              :stroke-width="selectedId === cell.zone.id ? 2.5 : 1.5"
            />
            <text
              :x="cell.x + cell.w / 2" :y="cell.y + cell.h / 2"
              text-anchor="middle" dominant-baseline="middle"
              font-size="11" font-weight="500" fill="#fff"
              style="pointer-events: none; user-select: none;"
            >{{ truncate(cell.zone.name, 16) }}</text>
          </g>
        </template>
      </svg>

      <!-- Zone detail tooltip -->
      <transition name="fade">
        <div v-if="selectedZone" class="zone-tooltip">
          <div class="tooltip-header">
            <p class="tooltip-name">{{ selectedZone.name }}</p>
            <button class="tooltip-close" @click="$emit('select-zone', null)">×</button>
          </div>
          <table class="tooltip-table">
            <tbody>
              <tr>
                <td>Risk score</td>
                <td class="val">{{ selectedZone.score }}/100</td>
              </tr>
              <tr>
                <td>Sun exposure</td>
                <td class="val">{{ pct(selectedZone.sun) }}</td>
              </tr>
              <tr>
                <td>Airflow</td>
                <td class="val">{{ pct(selectedZone.airflow) }}</td>
              </tr>
              <tr v-if="mode === 'seating' && selectedZone.has_roof !== undefined">
                <td>Roof coverage</td>
                <td class="val">{{ selectedZone.has_roof ? 'Yes' : 'No' }}</td>
              </tr>
            </tbody>
          </table>
          <span :class="['risk-badge', `risk-${selectedZone.level}`]">
            {{ capitalize(selectedZone.level) }} risk
          </span>
        </div>
      </transition>
    </div>

    <!-- Legend -->
    <div class="legend">
      <span v-for="level in RISK_LEVELS" :key="level" class="legend-item">
        <span class="legend-swatch" :style="{ background: RISK_COLORS[level] }" />
        {{ capitalize(level) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  zones: {
    type: Array,
    required: true
  },
  mode: {
    type: String,
    default: 'seating' // 'seating' | 'pitch'
  },
  selectedId: {
    type: String,
    default: null
  },
  selectedZone: {
    type: Object,
    default: null
  }
})

defineEmits(['select-zone'])

// ─── Constants ────────────────────────────────────────────────────────────────

const W = 680
const H = 380

const RISK_LEVELS = ['low', 'moderate', 'high', 'critical']

const RISK_COLORS = {
  low:      '#639922',
  moderate: '#EF9F27',
  high:     '#D85A30',
  critical: '#E24B4A',
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function riskRgba(level, alpha) {
  const hex = RISK_COLORS[level] ?? '#888'
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

function truncate(str, max) {
  return str.length > max ? str.slice(0, max - 1) + '…' : str
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

function pct(val) {
  return `${Math.round(val * 100)}%`
}

// ─── Seating geometry ─────────────────────────────────────────────────────────

const cx = W / 2
const cy = H / 2
const outer = Math.min(W, H) * 0.38
const inner = outer * 0.52
const GAP = 0.04

const seatingSegments = computed(() => {
  const n = props.zones.length
  if (!n) return []
  const step = (2 * Math.PI) / n

  return props.zones.map((zone, i) => {
    const a0 = i * step - Math.PI / 2 + GAP / 2
    const a1 = (i + 1) * step - Math.PI / 2 - GAP / 2

    const pts = []
    for (let a = a0; a <= a1; a += 0.05)
      pts.push([cx + Math.cos(a) * outer, cy + Math.sin(a) * outer])
    pts.push([cx + Math.cos(a1) * outer, cy + Math.sin(a1) * outer])
    for (let a = a1; a >= a0; a -= 0.05)
      pts.push([cx + Math.cos(a) * inner, cy + Math.sin(a) * inner])
    pts.push([cx + Math.cos(a0) * inner, cy + Math.sin(a0) * inner])

    const d = 'M ' + pts.map(p => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' L ') + ' Z'

    const midA = (a0 + a1) / 2
    const labelR = (outer + inner) / 2
    const lx = (cx + Math.cos(midA) * labelR).toFixed(1)
    const ly = (cy + Math.sin(midA) * labelR).toFixed(1)

    const short = zone.name
      .replace(/section \d+\s*[—\-]\s*/i, '')
      .replace(/section /i, '')
    const label = truncate(short, 14)

    return { zone, d, lx, ly, label }
  })
})

const pitchRect = computed(() => {
  const pw = inner * 1.3
  const ph = inner * 0.8
  return { x: (cx - pw / 2).toFixed(1), y: (cy - ph / 2).toFixed(1), w: pw.toFixed(1), h: ph.toFixed(1) }
})

// ─── Pitch geometry ───────────────────────────────────────────────────────────

const pitchBg = computed(() => {
  const pw = W * 0.62
  const ph = H * 0.72
  return { x: (W - pw) / 2, y: (H - ph) / 2, w: pw, h: ph }
})

const pitchCells = computed(() => {
  const n = props.zones.length
  if (!n) return []
  const cols = Math.ceil(Math.sqrt(n))
  const { x: px, y: py, w: pw, h: ph } = pitchBg.value
  const zw = pw / cols
  const zh = ph / Math.ceil(n / cols)

  return props.zones.map((zone, i) => ({
    zone,
    x: px + (i % cols) * zw,
    y: py + Math.floor(i / cols) * zh,
    w: zw,
    h: zh,
  }))
})

const pitchCircleR = computed(() => {
  const n = props.zones.length || 1
  const cols = Math.ceil(Math.sqrt(n))
  const rows = Math.ceil(n / cols)
  const { w: pw, h: ph } = pitchBg.value
  return Math.min(pw / cols, ph / rows) * 0.22
})
</script>

<style scoped>
.stadium-map-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.map-canvas {
  position: relative;
  background: #f5f5f3;
  border-radius: 12px;
  border: 0.5px solid #e0e0dc;
  overflow: hidden;
}

.zone-seg {
  cursor: pointer;
  transition: opacity 0.15s;
}
.zone-seg:hover { opacity: 0.75; }

/* ── Tooltip ── */
.zone-tooltip {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #fff;
  border: 0.5px solid #ddd;
  border-radius: 12px;
  padding: 14px 16px;
  max-width: 210px;
  font-size: 13px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  pointer-events: none;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 10px;
}

.tooltip-name {
  margin: 0;
  font-weight: 500;
  line-height: 1.3;
  font-size: 13px;
}

.tooltip-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  font-size: 16px;
  line-height: 1;
  padding: 0;
  flex-shrink: 0;
  pointer-events: all;
}

.tooltip-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.tooltip-table td { padding: 2px 0; }
.tooltip-table td:first-child { color: #888; }
.tooltip-table .val { text-align: right; font-weight: 500; }

/* ── Legend ── */
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #555;
}

.legend-swatch {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  display: inline-block;
  flex-shrink: 0;
}

/* ── Risk badges ── */
.risk-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 500;
  padding: 2px 9px;
  border-radius: 99px;
  white-space: nowrap;
  margin-top: 10px;
}
.risk-low      { background: #EAF3DE; color: #3B6D11; }
.risk-moderate { background: #FAEEDA; color: #854F0B; }
.risk-high     { background: #FAECE7; color: #993C1D; }
.risk-critical { background: #FCEBEB; color: #A32D2D; }

/* ── Transitions ── */
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
