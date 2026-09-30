import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from backend.app.core.config import settings
from backend.app.core.database import Base, engine
from backend.app.api.router import api_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Academic AI-Powered Virtual Cricket Coach API for Batting Technique Analysis",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve uploaded and processed video files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")

@app.get("/", response_class=HTMLResponse)
def get_web_dashboard():
    """
    Renders an inline modern sports technology dashboard for browser testing.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Virtual Cricket Coach | Batting Technique Analyzer</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
            .card { background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(8px); }
        </style>
    </head>
    <body class="min-h-screen pb-12">
        <!-- Top Navbar -->
        <nav class="border-b border-slate-800 bg-slate-900/80 sticky top-0 z-50 backdrop-blur-md">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center text-slate-950 font-bold text-xl shadow-lg shadow-emerald-500/20">
                        <i class="fa-solid font-bold fa-baseball-bat-ball"></i>
                    </div>
                    <div>
                        <h1 class="text-lg font-bold tracking-tight text-white">Virtual Cricket Coach</h1>
                        <p class="text-xs text-emerald-400 font-medium">Academic Technique Analysis Prototype</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4 text-sm font-medium">
                    <button onclick="switchTab('dashboard')" class="hover:text-emerald-400 transition-colors px-3 py-2 rounded-lg bg-slate-800 text-white">Dashboard</button>
                    <button onclick="switchTab('history')" class="hover:text-emerald-400 transition-colors px-3 py-2 rounded-lg text-slate-400">History</button>
                    <span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">API v1.0 Active</span>
                </div>
            </div>
        </nav>

        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-8">
            <!-- Disclaimers Banner -->
            <div class="p-4 rounded-xl card border-amber-500/30 bg-amber-500/5 flex items-start space-x-3">
                <i class="fa-solid fa-triangle-exclamation text-amber-400 text-lg mt-0.5"></i>
                <div class="text-xs text-amber-200/90 leading-relaxed">
                    <strong class="font-semibold text-amber-400">Academic AI Prototype Notice:</strong> This application calculates biomechanical joint angles and shot movement characteristics for educational and technique guidance. It is not intended for medical or physiological diagnostics.
                </div>
            </div>

            <!-- Dashboard Main View -->
            <div id="view-dashboard" class="space-y-8">
                <!-- Metrics Summary Grid -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="card p-5 rounded-2xl">
                        <p class="text-xs font-medium text-slate-400">Supported Batting Shots</p>
                        <p class="text-2xl font-bold text-white mt-2">5 Categories</p>
                        <p class="text-xs text-slate-500 mt-1">Defence, Drives, Pull & Cut</p>
                    </div>
                    <div class="card p-5 rounded-2xl">
                        <p class="text-xs font-medium text-slate-400">Pose Landmarker</p>
                        <p class="text-2xl font-bold text-emerald-400 mt-2">33 Joints (3D)</p>
                        <p class="text-xs text-slate-500 mt-1">MediaPipe Pose Pipeline</p>
                    </div>
                    <div class="card p-5 rounded-2xl">
                        <p class="text-xs font-medium text-slate-400">Biomechanics Engine</p>
                        <p class="text-2xl font-bold text-sky-400 mt-2">Vector Dot Math</p>
                        <p class="text-xs text-slate-500 mt-1">Exact Angle & Stability Index</p>
                    </div>
                    <div class="card p-5 rounded-2xl">
                        <p class="text-xs font-medium text-slate-400">Classification Model</p>
                        <p class="text-2xl font-bold text-purple-400 mt-2">Modular Heuristic / ML</p>
                        <p class="text-xs text-slate-500 mt-1">Confidence Thresholded</p>
                    </div>
                </div>

                <!-- Upload Section -->
                <div class="card p-6 rounded-2xl">
                    <h2 class="text-lg font-semibold text-white mb-1"><i class="fa-solid fa-cloud-arrow-up text-emerald-400 mr-2"></i>Upload Cricket Batting Video</h2>
                    <p class="text-sm text-slate-400 mb-6">Select an MP4 or MOV clip of a single batsman performing a shot.</p>

                    <form id="uploadForm" onsubmit="handleVideoUpload(event)" class="space-y-4">
                        <div class="border-2 border-dashed border-slate-700 hover:border-emerald-500/50 transition-colors rounded-xl p-8 text-center cursor-pointer relative" id="dropZone">
                            <input type="file" id="videoFile" accept="video/mp4,video/quicktime,video/x-msvideo" class="absolute inset-0 opacity-0 cursor-pointer" onchange="fileSelected(this)">
                            <div class="space-y-2">
                                <i class="fa-solid fa-file-video text-4xl text-slate-500" id="uploadIcon"></i>
                                <p class="text-sm font-medium text-slate-300" id="uploadLabel">Click or drop cricket video here (.mp4, .mov)</p>
                                <p class="text-xs text-slate-500">Maximum file size: 100MB | Duration: 1s to 60s</p>
                            </div>
                        </div>

                        <div class="flex items-center space-x-4">
                            <div class="w-1/2">
                                <label class="block text-xs font-medium text-slate-400 mb-1">Optional Shot Hint Override</label>
                                <select id="shotHint" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500">
                                    <option value="">Auto-Detect Shot Classification</option>
                                    <option value="Forward Defence">Forward Defence</option>
                                    <option value="Straight Drive">Straight Drive</option>
                                    <option value="Cover Drive">Cover Drive</option>
                                    <option value="Pull Shot">Pull Shot</option>
                                    <option value="Cut Shot">Cut Shot</option>
                                </select>
                            </div>
                            <div class="w-1/2 flex items-end">
                                <button type="submit" id="submitBtn" class="w-full bg-emerald-500 hover:bg-emerald-600 font-semibold text-slate-950 px-5 py-2.5 rounded-lg text-sm transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50">
                                    Start Technique Analysis
                                </button>
                            </div>
                        </div>
                    </form>

                    <!-- Status & Progress -->
                    <div id="statusBox" class="hidden mt-4 p-4 rounded-lg bg-slate-800 text-sm font-medium text-emerald-400">
                        <i class="fa-solid fa-spinner fa-spin mr-2"></i><span id="statusText">Uploading video...</span>
                    </div>
                </div>

                <!-- Analysis Results Dashboard (Hidden until populated) -->
                <div id="resultsSection" class="hidden space-y-8">
                    <!-- Shot Detection & Confidence Header -->
                    <div class="card p-6 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4">
                        <div>
                            <span class="text-xs uppercase tracking-wider text-slate-400 font-semibold">Detected Shot Category</span>
                            <h2 class="text-3xl font-extrabold text-white mt-1" id="resShotName">Cover Drive</h2>
                        </div>
                        <div class="flex items-center space-x-6">
                            <div class="text-right">
                                <span class="text-xs text-slate-400">Model Confidence</span>
                                <div class="text-xl font-bold text-emerald-400" id="resConfidence">92.0%</div>
                            </div>
                            <div class="text-right border-l border-slate-700 pl-6">
                                <span class="text-xs text-slate-400">Processing Latency</span>
                                <div class="text-xl font-bold text-sky-400" id="resProcTime">1.8s</div>
                            </div>
                        </div>
                    </div>

                    <!-- Video & Overlay Player -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div class="card p-4 rounded-2xl space-y-2">
                            <h3 class="text-sm font-semibold text-slate-300"><i class="fa-solid fa-skeleton text-emerald-400 mr-2"></i>Pose Overlay Video Output</h3>
                            <video id="resOverlayVideo" controls class="w-full rounded-xl border border-slate-800 bg-black aspect-video"></video>
                        </div>
                        <div class="card p-4 rounded-2xl space-y-2">
                            <h3 class="text-sm font-semibold text-slate-300"><i class="fa-chart-pie fa-solid text-sky-400 mr-2"></i>Biomechanical Radar Breakdown</h3>
                            <div class="aspect-video w-full flex items-center justify-center p-2">
                                <canvas id="biomechChart"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Biomechanical Measurement Grid & Feedback Cards -->
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <!-- Key Metrics Table -->
                        <div class="card p-6 rounded-2xl space-y-4">
                            <h3 class="text-base font-bold text-white border-b border-slate-800 pb-3"><i class="fa-solid fa-ruler-combined text-emerald-400 mr-2"></i>Calculated Features</h3>
                            <div id="resFeaturesList" class="space-y-3 text-sm">
                                <!-- Features populated dynamically -->
                            </div>
                        </div>

                        <!-- Feedback Observations (Span 2) -->
                        <div class="card p-6 rounded-2xl lg:col-span-2 space-y-4">
                            <h3 class="text-base font-bold text-white border-b border-slate-800 pb-3"><i class="fa-solid fa-list-check text-purple-400 mr-2"></i>Technique Analysis & Coaching Feedback</h3>
                            <div id="resFeedbackList" class="space-y-3">
                                <!-- Feedbacks populated dynamically -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- History View (Hidden by default) -->
            <div id="view-history" class="hidden space-y-6">
                <div class="card p-6 rounded-2xl">
                    <h2 class="text-xl font-bold text-white mb-4"><i class="fa-solid fa-clock-rotate-left text-emerald-400 mr-2"></i>Athlete Performance History</h2>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm text-slate-300">
                            <thead class="text-xs uppercase text-slate-400 bg-slate-800/60">
                                <tr>
                                    <th class="p-3 rounded-l-lg">Date</th>
                                    <th class="p-3">Video File</th>
                                    <th class="p-3">Shot Detected</th>
                                    <th class="p-3">Confidence</th>
                                    <th class="p-3 rounded-r-lg">Key Technique Observations</th>
                                </tr>
                            </thead>
                            <tbody id="historyTableBody">
                                <tr><td colspan="5" class="p-4 text-center text-slate-500">No session history yet. Upload a video to run analysis.</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>

        <script>
            let currentChart = null;

            function switchTab(tab) {
                if (tab === 'dashboard') {
                    document.getElementById('view-dashboard').classList.remove('hidden');
                    document.getElementById('view-history').classList.add('hidden');
                } else {
                    document.getElementById('view-dashboard').classList.add('hidden');
                    document.getElementById('view-history').classList.remove('hidden');
                    loadHistory();
                }
            }

            function fileSelected(input) {
                if (input.files && input.files[0]) {
                    document.getElementById('uploadLabel').innerText = input.files[0].name;
                    document.getElementById('uploadIcon').className = "fa-solid fa-file-circle-check text-4xl text-emerald-400";
                }
            }

            async function handleVideoUpload(event) {
                event.preventDefault();
                const fileInput = document.getElementById('videoFile');
                if (!fileInput.files || !fileInput.files[0]) {
                    alert("Please select a video file first.");
                    return;
                }

                const statusBox = document.getElementById('statusBox');
                const statusText = document.getElementById('statusText');
                const submitBtn = document.getElementById('submitBtn');

                statusBox.classList.remove('hidden');
                submitBtn.disabled = true;
                statusText.innerText = "Uploading & validating video stream...";

                try {
                    // 1. Upload Video
                    const formData = new FormData();
                    formData.append('file', fileInput.files[0]);

                    const uploadRes = await fetch('/api/videos/upload', { method: 'POST', body: formData });
                    const uploadData = await uploadRes.json();

                    if (!uploadRes.ok) throw new Error(uploadData.detail || 'Upload failed');

                    statusText.innerText = "Running MediaPipe Pose Landmarker & Biomechanical Extraction...";

                    // 2. Start Analysis
                    const shotHint = document.getElementById('shotHint').value;
                    const startRes = await fetch('/api/analysis/start', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ video_id: uploadData.video_id, shot_type_hint: shotHint || null })
                    });

                    const analysisData = await startRes.json();
                    if (!startRes.ok) throw new Error(analysisData.detail || 'Analysis failed');

                    statusText.innerText = "Rendering Pose Overlay & Generating Coaching Feedback...";

                    renderAnalysisResults(analysisData);
                    statusBox.classList.add('hidden');
                    submitBtn.disabled = false;

                } catch (err) {
                    alert("Error: " + err.message);
                    statusBox.classList.add('hidden');
                    submitBtn.disabled = false;
                }
            }

            function renderAnalysisResults(data) {
                document.getElementById('resultsSection').classList.remove('hidden');

                document.getElementById('resShotName').innerText = data.shot_type;
                document.getElementById('resConfidence').innerText = (data.confidence * 100).toFixed(1) + "%";
                document.getElementById('resProcTime').innerText = (data.processing_time || 1.0).toFixed(2) + "s";

                // Set overlay video player
                const player = document.getElementById('resOverlayVideo');
                player.src = data.overlay_video_url;
                player.load();

                // Render Features
                const featContainer = document.getElementById('resFeaturesList');
                featContainer.innerHTML = '';
                
                const labels = [];
                const values = [];

                data.features.forEach(f => {
                    featContainer.innerHTML += `
                        <div class="flex justify-between items-center border-b border-slate-800/80 pb-2">
                            <span class="text-slate-400 capitalize">${f.feature_name.replace(/_/g, ' ')}</span>
                            <span class="font-mono font-semibold text-emerald-400">${f.value} ${f.unit || ''}</span>
                        </div>
                    `;
                    labels.push(f.feature_name.replace(/_/g, ' '));
                    values.push(f.value);
                });

                // Render Feedbacks
                const fbContainer = document.getElementById('resFeedbackList');
                fbContainer.innerHTML = '';
                data.feedbacks.forEach(fb => {
                    let badgeClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
                    if (fb.severity === 'high') badgeClass = "bg-rose-500/10 text-rose-400 border-rose-500/20";
                    if (fb.severity === 'moderate') badgeClass = "bg-amber-500/10 text-amber-400 border-amber-500/20";

                    fbContainer.innerHTML += `
                        <div class="p-4 rounded-xl border ${badgeClass} space-y-1">
                            <div class="flex justify-between items-center">
                                <span class="font-bold text-xs uppercase tracking-wider">${fb.category}</span>
                                <span class="text-xs px-2 py-0.5 rounded font-semibold uppercase">${fb.severity}</span>
                            </div>
                            <p class="text-sm text-slate-200">${fb.message}</p>
                        </div>
                    `;
                });

                // Render Chart
                renderRadarChart(labels, values);
            }

            function renderRadarChart(labels, values) {
                const ctx = document.getElementById('biomechChart').getContext('2d');
                if (currentChart) currentChart.destroy();

                currentChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Measured Value',
                            data: values,
                            backgroundColor: 'rgba(16, 185, 129, 0.5)',
                            borderColor: 'rgba(16, 185, 129, 1)',
                            borderWidth: 2,
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                            x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } }
                        }
                    }
                });
            }

            async function loadHistory() {
                try {
                    const res = await fetch('/api/athletes');
                    const athletes = await res.json();
                    if (!athletes || athletes.length === 0) return;

                    const hRes = await fetch(`/api/athletes/${athletes[0].id}/history`);
                    const history = await hRes.json();

                    const tbody = document.getElementById('historyTableBody');
                    tbody.innerHTML = '';

                    if (!history || history.length === 0) {
                        tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-500">No session history recorded yet.</td></tr>`;
                        return;
                    }

                    history.forEach(item => {
                        tbody.innerHTML += `
                            <tr class="border-b border-slate-800 hover:bg-slate-800/40">
                                <td class="p-3 text-xs text-slate-400">${new Date(item.created_at).toLocaleString()}</td>
                                <td class="p-3 font-mono text-xs text-slate-200">${item.video_filename}</td>
                                <td class="p-3 font-semibold text-emerald-400">${item.shot_type}</td>
                                <td class="p-3 text-slate-300">${(item.confidence * 100).toFixed(1)}%</td>
                                <td class="p-3 text-xs text-slate-300">${item.feedback_summary.join(' | ')}</td>
                            </tr>
                        `;
                    });
                } catch(e) {
                    console.error("Failed to load history:", e);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content
