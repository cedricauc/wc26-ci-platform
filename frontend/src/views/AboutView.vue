<template>
  <div class="about-view">
    <div class="card max-w-4xl mx-auto">
      <h1 class="text-4xl font-bold mb-6">About HeatAware Hub</h1>
      
      <div class="prose max-w-none">
        <p class="text-lg text-gray-700 mb-6">
          HeatAware Hub is a comprehensive Climate Intelligence system designed for the 
          FIFA World Cup 2026, providing real-time heat risk analysis and safety 
          recommendations for players and fans.
        </p>

        <h2 class="text-2xl font-bold mt-8 mb-4">Features</h2>
        <ul class="space-y-2 text-gray-700">
          <li>✅ Real-time weather data integration from OpenWeather API</li>
          <li>✅ Advanced heat index and risk calculations</li>
          <li>✅ Player fatigue and stress modeling</li>
          <li>✅ Fan heat exposure assessment</li>
          <li>✅ Interactive 2D stadium maps with PixiJS</li>
          <li>✅ Zone-specific risk analysis for pitch and seating areas</li>
          <li>✅ Personalized recommendations for players and fans</li>
          <li>✅ Match preview with weather forecasts</li>
        </ul>

        <h2 class="text-2xl font-bold mt-8 mb-4">How It Works</h2>
        <div class="space-y-4 text-gray-700">
          <div class="bg-blue-50 p-4 rounded-lg">
            <h3 class="font-bold text-blue-900 mb-2">1. Weather Data Collection</h3>
            <p>We integrate with OpenWeather API to fetch real-time and forecasted weather 
            conditions for each match location, including temperature, humidity, UV index, 
            and wind speed.</p>
          </div>

          <div class="bg-green-50 p-4 rounded-lg">
            <h3 class="font-bold text-green-900 mb-2">2. Risk Analysis</h3>
            <p>Our sophisticated algorithms calculate heat stress risk using multiple factors:
            heat index, humidity, UV exposure, and physical exertion levels. Separate models
            assess risks for players and fans.</p>
          </div>

          <div class="bg-purple-50 p-4 rounded-lg">
            <h3 class="font-bold text-purple-900 mb-2">3. Zone Mapping</h3>
            <p>Stadium architectural data is analyzed to identify high-risk zones based on
            sun exposure, airflow quality, and roof coverage. Interactive maps visualize
            these risks in real-time.</p>
          </div>

          <div class="bg-orange-50 p-4 rounded-lg">
            <h3 class="font-bold text-orange-900 mb-2">4. Smart Recommendations</h3>
            <p>Based on the risk analysis, we generate tailored recommendations including
            hydration schedules, cooling breaks, tactical adjustments, and safety guidance.</p>
          </div>
        </div>

        <h2 class="text-2xl font-bold mt-8 mb-4">Risk Levels</h2>
        <div class="grid md:grid-cols-2 gap-4">
          <div class="p-4 bg-green-50 border-2 border-green-200 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-4 h-4 rounded bg-heat-low"></div>
              <h3 class="font-bold text-green-900">Low Risk (0-40)</h3>
            </div>
            <p class="text-sm text-green-800">
              Minimal heat stress. Standard precautions apply.
            </p>
          </div>

          <div class="p-4 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-4 h-4 rounded bg-heat-moderate"></div>
              <h3 class="font-bold text-yellow-900">Moderate Risk (40-65)</h3>
            </div>
            <p class="text-sm text-yellow-800">
              Moderate heat stress. Enhanced hydration and monitoring recommended.
            </p>
          </div>

          <div class="p-4 bg-orange-50 border-2 border-orange-200 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-4 h-4 rounded bg-heat-high"></div>
              <h3 class="font-bold text-orange-900">High Risk (65-85)</h3>
            </div>
            <p class="text-sm text-orange-800">
              High heat stress. Cooling breaks and significant precautions required.
            </p>
          </div>

          <div class="p-4 bg-red-50 border-2 border-red-200 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-4 h-4 rounded bg-heat-critical"></div>
              <h3 class="font-bold text-red-900">Critical Risk (85-100)</h3>
            </div>
            <p class="text-sm text-red-800">
              Extreme heat stress. Maximum precautions essential. Consider match timing.
            </p>
          </div>
        </div>

        <h2 class="text-2xl font-bold mt-8 mb-4">Technology Stack</h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div>
            <h3 class="font-bold text-lg mb-2">Frontend</h3>
            <ul class="space-y-1 text-gray-700">
              <li>• Vue.js 3 - UI Framework</li>
              <li>• PixiJS - Interactive Graphics</li>
              <li>• Tailwind CSS - Styling</li>
              <li>• Axios - API Communication</li>
            </ul>
          </div>
          <div>
            <h3 class="font-bold text-lg mb-2">Backend</h3>
            <ul class="space-y-1 text-gray-700">
              <li>• Python FastAPI - REST API</li>
              <li>• OpenWeather API - Weather Data</li>
              <li>• SQLAlchemy - Database ORM</li>
              <li>• Redis - Caching</li>
            </ul>
          </div>
        </div>

        <h2 class="text-2xl font-bold mt-8 mb-4">FIFA World Cup 2026</h2>
        <p class="text-gray-700 mb-4">
          The 2026 FIFA World Cup will be hosted across the United States, Canada, and Mexico,
          featuring matches in diverse climates from the heat of Miami to the moderate conditions
          of Toronto. HeatAware Hub ensures player safety and fan comfort across all venues.
        </p>

        <div class="bg-blue-50 p-6 rounded-lg mt-6">
          <h3 class="font-bold text-xl mb-3">Get Started</h3>
          <p class="text-gray-700 mb-4">
            Try our risk calculator on the home page or explore match previews to see
            HeatAware Hub in action.
          </p>
          <router-link to="/" class="btn-primary inline-block">
            Go to Home
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// About page component
</script>

<style scoped>
.prose ul {
  list-style-type: none;
  padding-left: 0;
}
</style>