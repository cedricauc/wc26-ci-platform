<template>
  <div class="home-view" style="font-family: var(--font-sans, sans-serif);">

    <!-- Hero -->
    <div style="padding: 2.5rem 0 2rem; text-align: center;">
      <h1 style="font-size: 28px; font-weight: 500; line-height: 1.3; margin-bottom: .75rem;">
        Climate intelligence for every match
      </h1>
      <p style="font-size: 15px; color: #666; max-width: 480px; margin: 0 auto;">
        Real-time heat risk analysis and safety recommendations for FIFA World Cup 2026
      </p>
    </div>

    <!-- Upcoming Matches -->
    <div style="margin-bottom: 2rem;">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
        <div style="font-size: 16px; font-weight: 500; display: flex; align-items: center; gap: 8px;">
          ⚽ Upcoming matches
          <span v-if="loadingMatches" style="font-size: 12px; color: #999;">(Loading...)</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
          <span v-if="!loadingMatches && totalMatches > 0" style="font-size: 12px; color: #999;">
            {{ (currentPage - 1) * pageSize + 1 }}–{{ Math.min(currentPage * pageSize, totalMatches) }} of {{ totalMatches }}
          </span>
          <select
            v-model="pageSize"
            @change="onPageSizeChange"
            style="font-size: 12px; padding: 4px 8px; border: 0.5px solid #ccc; border-radius: 6px; background: transparent; color: inherit; cursor: pointer;"
          >
            <option :value="10">10 per page</option>
            <option :value="20">20 per page</option>
            <option :value="50">50 per page</option>
            <option :value="100">100 per page</option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loadingMatches" style="text-align: center; padding: 2rem; color: #999; font-size: 14px;">
        Loading matches...
      </div>

      <!-- Error -->
      <div v-else-if="matchesError" style="padding: 1rem; background: #fcebeb; border: 0.5px solid #f09595; border-radius: 8px; font-size: 13px; color: #a32d2d;">
        {{ matchesError }}
      </div>

      <!-- Match Cards -->
      <div v-else-if="upcomingMatches.length > 0" style="display: grid; gap: 10px;">
        <div
          v-for="match in upcomingMatches"
          :key="match.id"
          @click="navigateToMatch(match)"
          @mouseenter="hoveredMatch = match.id"
          @mouseleave="hoveredMatch = null"
          :style="matchCardStyle(match.id)"
        >
          <!-- Teams -->
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="display: flex; flex-direction: column; gap: 2px;">
              <span style="font-size: 15px; font-weight: 500;">{{ match.home }}</span>
              <span style="font-size: 11px; color: #aaa;">Home</span>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center; gap: 1px; padding: 0 4px; flex-shrink: 0;">
              <div style="width: 3px; height: 3px; border-radius: 50%; background: #ccc;"></div>
              <span style="font-size: 10px; font-weight: 500; color: #bbb; letter-spacing: .05em;">VS</span>
              <div style="width: 3px; height: 3px; border-radius: 50%; background: #ccc;"></div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 2px;">
              <span style="font-size: 15px; font-weight: 500;">{{ match.away }}</span>
              <span style="font-size: 11px; color: #aaa;">Away</span>
            </div>
          </div>

          <!-- Meta + CTA -->
          <div style="display: flex; align-items: center; gap: 16px;">
            <div style="display: flex; flex-direction: column; gap: 4px; align-items: flex-end;">
              <span style="font-size: 11px; font-weight: 500; padding: 2px 8px; border-radius: 20px; background: #e6f1fb; color: #0c447c;">
                {{ match.group }}
              </span>
              <span style="font-size: 13px; font-weight: 500; text-align: right;">{{ match.venue }}</span>
              <span style="font-size: 12px; color: #888; text-align: right;">{{ match.city }}</span>
              <span style="font-size: 12px; color: #185fa5; font-weight: 500;">🕐 {{ match.time }}</span>
            </div>
            <div :style="{
              display: 'flex', alignItems: 'center', gap: '4px',
              fontSize: '12px',
              color: hoveredMatch === match.id ? '#185fa5' : '#aaa',
              whiteSpace: 'nowrap', flexShrink: '0',
              transition: 'color .15s'
            }">
              View →
            </div>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else style="text-align: center; padding: 2rem; color: #999; background: #f9f9f7; border-radius: 8px; font-size: 13px;">
        No upcoming matches found. Upload a match schedule PDF to populate.
      </div>

      <!-- Pagination -->
      <div v-if="!loadingMatches && totalPages > 1"
           style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 1rem;">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          :style="paginationBtnStyle(false, currentPage === 1)"
        >
          ←
        </button>

        <template v-for="item in visiblePages" :key="item">
          <span v-if="item === '...'"
                style="padding: 0 4px; font-size: 13px; color: #aaa;">…</span>
          <button
            v-else
            @click="goToPage(item)"
            :style="paginationBtnStyle(item === currentPage, false)"
          >
            {{ item }}
          </button>
        </template>

        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          :style="paginationBtnStyle(false, currentPage === totalPages)"
        >
          →
        </button>
      </div>
    </div>

    <!-- Divider -->
    <div style="height: 0.5px; background: #e5e5e5; margin: 1.5rem 0;"></div>

    <!-- Features -->
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 2rem;">
      <div v-for="feat in features" :key="feat.title"
           style="background: #fff; border: 0.5px solid #e5e5e5; border-radius: 12px; padding: 1.25rem; text-align: center;">
        <div style="width: 40px; height: 40px; border-radius: 8px; background: #f5f5f3; display: flex; align-items: center; justify-content: center; margin: 0 auto .75rem; font-size: 20px;">
          {{ feat.icon }}
        </div>
        <div style="font-size: 14px; font-weight: 500; margin-bottom: 4px;">{{ feat.title }}</div>
        <div style="font-size: 12px; color: #888; line-height: 1.5;">{{ feat.desc }}</div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { matchAPI } from '@/services/api'

const router = useRouter()

const hoveredMatch = ref(null)
const loadingMatches = ref(true)
const matchesError = ref(null)
const upcomingMatches = ref([])
const totalMatches = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// --- Navigation ---
const navigateToMatch = (match) => {
  router.push(`/match/${match.match_number}`)
}

// --- Card style ---
const matchCardStyle = (id) => ({
  background: '#fff',
  border: `0.5px solid ${hoveredMatch.value === id ? '#999' : '#e5e5e5'}`,
  borderRadius: '12px',
  padding: '1rem 1.25rem',
  display: 'grid',
  gridTemplateColumns: '1fr auto',
  gap: '1rem',
  alignItems: 'center',
  cursor: 'pointer',
  transition: 'border-color .15s',
})

// --- Pagination computed ---
const totalPages = computed(() => Math.ceil(totalMatches.value / pageSize.value))

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
    return pages
  }

  pages.push(1)
  if (current > 3) pages.push('...')

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) pages.push(i)

  if (current < total - 2) pages.push('...')
  pages.push(total)

  return pages
})

const paginationBtnStyle = (active, disabled) => ({
  padding: '5px 10px',
  fontSize: '13px',
  border: '0.5px solid #ccc',
  borderRadius: '6px',
  background: active ? '#185fa5' : disabled ? '#f5f5f5' : '#fff',
  color: active ? '#fff' : disabled ? '#bbb' : '#333',
  cursor: disabled ? 'not-allowed' : 'pointer',
  fontWeight: active ? '500' : '400',
  transition: 'all .15s',
  minWidth: '32px',
})

// --- Fetch ---
const fetchMatches = async () => {
  loadingMatches.value = true
  matchesError.value = null

  try {
    const response = await matchAPI.listMatches({
      page: currentPage.value,
      limit: pageSize.value,
    })

    const data = response.data
    // Support both { matches, total } and { items, total } response shapes
    const raw = data.matches ?? data.items ?? []
    totalMatches.value = data.total ?? raw.length

    upcomingMatches.value = raw.map(m => ({
      id: m.id ?? m.match_number,
      match_number: m.match_number, 
      home: m.home_team,
      away: m.away_team,
      group: m.group_name || 'TBD',
      venue: m.stadium,
      city: m.city,
      time: formatMatchTime(m.kickoff_time || m.kickoff_datetime),
      lat: m.latitude ?? 0,
      lng: m.longitude ?? 0,
    }))
  } catch (err) {
    console.error('Error fetching matches:', err)
    matchesError.value = 'Failed to load matches from server.'
    // Fallback sample data
    upcomingMatches.value = [
      { id: 1, home: 'Mexico', away: 'South Africa', group: 'Group A', venue: 'Estadio Azteca', city: 'Mexico City', time: 'Thu Jun 11', lat: 19.3029, lng: -99.1505 },
      { id: 2, home: 'Korea Republic', away: 'Czechia', group: 'Group A', venue: 'Estadio Akron', city: 'Guadalajara', time: 'Thu Jun 11', lat: 20.6878, lng: -103.4669 },
    ]
    totalMatches.value = upcomingMatches.value.length
  } finally {
    loadingMatches.value = false
  }
}

const formatMatchTime = (isoString) => {
  if (!isoString) return 'TBD'
  try {
    return new Date(isoString).toLocaleString('en-US', {
      weekday: 'short', month: 'short', day: 'numeric',
      hour: 'numeric', minute: '2-digit'
    })
  } catch {
    return 'TBD'
  }
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchMatches()
}

const onPageSizeChange = () => {
  currentPage.value = 1
  fetchMatches()
}

onMounted(fetchMatches)

const features = ref([
  { icon: '🌡️', title: 'Real-time weather', desc: 'Live data and forecasts for every match location' },
  { icon: '🗺️', title: 'Stadium maps', desc: 'Heat-risk overlays for pitch and seating zones' },
  { icon: '💡', title: 'Smart recommendations', desc: 'Personalized safety guidance for players and fans' },
])
</script>