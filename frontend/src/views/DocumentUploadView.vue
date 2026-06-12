<template>
  <div class="document-upload-view" style="font-family: var(--font-sans, sans-serif); max-width: 900px; margin: 0 auto;">
    
    <!-- Header -->
    <div style="padding: 2rem 0 1.5rem;">
      <h1 style="font-size: 24px; font-weight: 500; margin-bottom: .5rem;">
        📄 Document Ingestion
      </h1>
      <p style="font-size: 14px; color: #666;">
        Upload FIFA World Cup PDF documents to extract and store team, stadium, and match data
      </p>
    </div>

    <!-- Upload Cards -->
    <div style="display: grid; gap: 16px; margin-bottom: 2rem;">

      <!-- Stadium PDF Upload -->
      <div style="background: #fff; border: 0.5px solid #e5e5e5; border-radius: 12px; padding: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
          <div style="width: 40px; height: 40px; border-radius: 8px; background: #faeeda; display: flex; align-items: center; justify-content: center; font-size: 20px;">
            🏟️
          </div>
          <div>
            <h3 style="font-size: 16px; font-weight: 500; margin-bottom: 2px;">Stadium Information</h3>
            <p style="font-size: 12px; color: #888;">Upload PDFs with stadium details, locations, and capacities</p>
          </div>
        </div>
        
        <div style="margin-bottom: 12px;">
          <input
            ref="stadiumFileInput"
            type="file"
            accept=".pdf"
            @change="handleFileSelect($event, 'stadium')"
            style="display: none;"
          />
          <button
            @click="$refs.stadiumFileInput.click()"
            :disabled="uploading.stadium"
            style="width: 100%; padding: 10px; border-radius: 8px; background: #185fa5; color: #fff; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background .15s;"
            @mouseenter="e => !uploading.stadium && (e.target.style.background = '#378add')"
            @mouseleave="e => e.target.style.background = '#185fa5'"
          >
            {{ uploading.stadium ? 'Uploading...' : selectedFiles.stadium ? selectedFiles.stadium.name : 'Select Stadium PDF' }}
          </button>
        </div>

        <button
          v-if="selectedFiles.stadium"
          @click="uploadFile('stadium')"
          :disabled="uploading.stadium"
          style="width: 100%; padding: 10px; border-radius: 8px; background: #27500a; color: #fff; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background .15s;"
          @mouseenter="e => !uploading.stadium && (e.target.style.background = '#3b6d11')"
          @mouseleave="e => e.target.style.background = '#27500a'"
        >
          Upload & Process
        </button>

        <div v-if="uploadResults.stadium" style="margin-top: 12px; padding: 12px; border-radius: 8px;" :style="resultStyle(uploadResults.stadium.status)">
          <p style="font-size: 13px; font-weight: 500; margin-bottom: 4px;">{{ uploadResults.stadium.message }}</p>
          <p v-if="uploadResults.stadium.filename" style="font-size: 12px; opacity: 0.8;">File: {{ uploadResults.stadium.filename }}</p>
        </div>
      </div>

      <!-- Game Schedule PDF Upload -->
      <div style="background: #fff; border: 0.5px solid #e5e5e5; border-radius: 12px; padding: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
          <div style="width: 40px; height: 40px; border-radius: 8px; background: #eaf3de; display: flex; align-items: center; justify-content: center; font-size: 20px;">
            ⚽
          </div>
          <div>
            <h3 style="font-size: 16px; font-weight: 500; margin-bottom: 2px;">Match Schedule</h3>
            <p style="font-size: 12px; color: #888;">Upload PDFs containing match schedules and fixtures</p>
          </div>
        </div>
        
        <div style="margin-bottom: 12px;">
          <input
            ref="gameFileInput"
            type="file"
            accept=".pdf"
            @change="handleFileSelect($event, 'game')"
            style="display: none;"
          />
          <button
            @click="$refs.gameFileInput.click()"
            :disabled="uploading.game"
            style="width: 100%; padding: 10px; border-radius: 8px; background: #185fa5; color: #fff; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background .15s;"
            @mouseenter="e => !uploading.game && (e.target.style.background = '#378add')"
            @mouseleave="e => e.target.style.background = '#185fa5'"
          >
            {{ uploading.game ? 'Uploading...' : selectedFiles.game ? selectedFiles.game.name : 'Select Game Schedule PDF' }}
          </button>
        </div>

        <button
          v-if="selectedFiles.game"
          @click="uploadFile('game')"
          :disabled="uploading.game"
          style="width: 100%; padding: 10px; border-radius: 8px; background: #27500a; color: #fff; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background .15s;"
          @mouseenter="e => !uploading.game && (e.target.style.background = '#3b6d11')"
          @mouseleave="e => e.target.style.background = '#27500a'"
        >
          Upload & Process
        </button>

        <div v-if="uploadResults.game" style="margin-top: 12px; padding: 12px; border-radius: 8px;" :style="resultStyle(uploadResults.game.status)">
          <p style="font-size: 13px; font-weight: 500; margin-bottom: 4px;">{{ uploadResults.game.message }}</p>
          <p v-if="uploadResults.game.filename" style="font-size: 12px; opacity: 0.8;">File: {{ uploadResults.game.filename }}</p>
        </div>
      </div>
    </div>

    <!-- Info Section -->
    <div style="background: #f9f9f7; border: 0.5px solid #e5e5e5; border-radius: 12px; padding: 1.5rem;">
      <h3 style="font-size: 15px; font-weight: 500; margin-bottom: 1rem;">How it works</h3>
      <div style="display: grid; gap: 12px;">
        <div style="display: flex; gap: 12px;">
          <span style="font-size: 20px;">1️⃣</span>
          <div>
            <p style="font-size: 13px; font-weight: 500; margin-bottom: 2px;">Upload PDF</p>
            <p style="font-size: 12px; color: #666;">Select and upload your FIFA World Cup document</p>
          </div>
        </div>
        <div style="display: flex; gap: 12px;">
          <span style="font-size: 20px;">2️⃣</span>
          <div>
            <p style="font-size: 13px; font-weight: 500; margin-bottom: 2px;">Docling Extraction</p>
            <p style="font-size: 12px; color: #666;">AI-powered extraction of tables, text, and structured data</p>
          </div>
        </div>
        <div style="display: flex; gap: 12px;">
          <span style="font-size: 20px;">3️⃣</span>
          <div>
            <p style="font-size: 13px; font-weight: 500; margin-bottom: 2px;">Data Normalization</p>
            <p style="font-size: 12px; color: #666;">Intelligent parsing and validation of extracted information</p>
          </div>
        </div>
        <div style="display: flex; gap: 12px;">
          <span style="font-size: 20px;">4️⃣</span>
          <div>
            <p style="font-size: 13px; font-weight: 500; margin-bottom: 2px;">Database Storage</p>
            <p style="font-size: 12px; color: #666;">Automatic insertion into the database with relationship mapping</p>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const selectedFiles = ref({
  team: null,
  stadium: null,
  game: null
})

const uploading = ref({
  team: false,
  stadium: false,
  game: false
})

const uploadResults = ref({
  team: null,
  stadium: null,
  game: null
})

const handleFileSelect = (event, type) => {
  const file = event.target.files[0]
  if (file) {
    selectedFiles.value[type] = file
    uploadResults.value[type] = null
  }
}

const uploadFile = async (type) => {
  const file = selectedFiles.value[type]
  if (!file) return

  uploading.value[type] = true
  uploadResults.value[type] = null

  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('uploaded_by', 'admin')

    const endpoint = `${API_BASE_URL}/api/v1/ingest/${type}-pdf`
    const response = await axios.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    uploadResults.value[type] = {
      status: 'success',
      message: response.data.message || 'Upload successful!',
      filename: response.data.filename
    }

    // Clear selected file after successful upload
    selectedFiles.value[type] = null

  } catch (error) {
    console.error(`Error uploading ${type} PDF:`, error)
    uploadResults.value[type] = {
      status: 'error',
      message: error.response?.data?.detail || 'Upload failed. Please try again.',
      filename: file.name
    }
  } finally {
    uploading.value[type] = false
  }
}

const resultStyle = (status) => {
  if (status === 'success') {
    return {
      background: '#eaf3de',
      border: '0.5px solid #a8d47f',
      color: '#27500a'
    }
  } else if (status === 'error') {
    return {
      background: '#fcebeb',
      border: '0.5px solid #f09595',
      color: '#a32d2d'
    }
  }
  return {}
}
</script>