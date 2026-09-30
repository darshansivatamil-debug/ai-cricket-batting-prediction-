import React, { useState } from 'react';
import Head from 'next/head';
import { Dashboard } from '../components/Dashboard';
import { uploadVideo, startAnalysis, AnalysisResult } from '../services/api';

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [shotHint, setShotHint] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [statusText, setStatusText] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadAndAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      alert("Please select a video file first.");
      return;
    }

    setLoading(true);
    setStatusText("Uploading & validating video stream...");

    try {
      const uploadRes = await uploadVideo(selectedFile);
      setStatusText("Running MediaPipe Pose Landmarker & Biomechanical Extraction...");

      const result = await startAnalysis(uploadRes.video_id, shotHint || undefined);
      setAnalysisResult(result);
      setStatusText("Analysis complete!");
    } catch (err: any) {
      alert("Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>AI Virtual Cricket Coach | Batting Technique Analyzer</title>
        <meta name="description" content="AI-Powered Virtual Cricket Coach for Automated Cricket Technique Analysis" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen pb-12 bg-slate-950 text-slate-100">
        <nav class="border-b border-slate-800 bg-slate-900/80 sticky top-0 z-50 backdrop-blur-md">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center text-slate-950 font-bold text-xl shadow-lg shadow-emerald-500/20">
                🏏
              </div>
              <div>
                <h1 class="text-lg font-bold tracking-tight text-white">Virtual Cricket Coach</h1>
                <p class="text-xs text-emerald-400 font-medium">Academic AI Prototype</p>
              </div>
            </div>
            <div class="flex items-center space-x-4 text-sm font-medium">
              <span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Vercel Ready
              </span>
            </div>
          </div>
        </nav>

        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-8">
          <Dashboard />

          <div class="p-6 bg-slate-900 rounded-2xl border border-slate-800 space-y-4">
            <h2 class="text-lg font-semibold text-white">Upload Cricket Batting Video</h2>
            <form onSubmit={handleUploadAndAnalyze} class="space-y-4">
              <div class="border-2 border-dashed border-slate-700 hover:border-emerald-500/50 transition-colors rounded-xl p-8 text-center relative">
                <input 
                  type="file" 
                  accept="video/mp4,video/quicktime" 
                  onChange={handleFileChange}
                  class="absolute inset-0 opacity-0 cursor-pointer w-full h-full" 
                />
                <p class="text-sm font-medium text-slate-300">
                  {selectedFile ? selectedFile.name : "Click or drop cricket video here (.mp4, .mov)"}
                </p>
              </div>

              <div class="flex space-x-4">
                <select 
                  value={shotHint} 
                  onChange={(e) => setShotHint(e.target.value)}
                  class="w-1/2 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
                >
                  <option value="">Auto-Detect Shot Classification</option>
                  <option value="Forward Defence">Forward Defence</option>
                  <option value="Straight Drive">Straight Drive</option>
                  <option value="Cover Drive">Cover Drive</option>
                  <option value="Pull Shot">Pull Shot</option>
                  <option value="Cut Shot">Cut Shot</option>
                </select>

                <button 
                  type="submit" 
                  disabled={loading}
                  class="w-1/2 bg-emerald-500 hover:bg-emerald-600 font-semibold text-slate-950 px-5 py-2.5 rounded-lg text-sm transition-all disabled:opacity-50"
                >
                  {loading ? statusText : "Start AI Technique Analysis"}
                </button>
              </div>
            </form>
          </div>

          {analysisResult && (
            <div class="p-6 bg-slate-900 rounded-2xl border border-slate-800 space-y-4">
              <div class="flex justify-between items-center">
                <div>
                  <span class="text-xs text-slate-400 uppercase">Detected Shot</span>
                  <h3 class="text-3xl font-extrabold text-white">{analysisResult.shot_type}</h3>
                </div>
                <div class="text-right">
                  <span class="text-xs text-slate-400">Model Confidence</span>
                  <div class="text-2xl font-bold text-emerald-400">
                    {(analysisResult.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}
