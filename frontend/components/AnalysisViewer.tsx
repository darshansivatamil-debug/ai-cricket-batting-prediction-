import React from 'react';
import { AnalysisResult } from '../services/api';

interface AnalysisViewerProps {
  analysis: AnalysisResult;
}

export const AnalysisViewer: React.FC<AnalysisViewerProps> = ({ analysis }) => {
  return (
    <div className="space-y-6">
      <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 flex justify-between items-center">
        <div>
          <span className="text-xs text-slate-400 uppercase">Detected Shot</span>
          <h2 className="text-3xl font-extrabold text-white">{analysis.shot_type}</h2>
        </div>
        <div className="text-right">
          <span className="text-xs text-slate-400">Confidence</span>
          <div className="text-2xl font-bold text-emerald-400">
            {(analysis.confidence * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-4 bg-slate-800 rounded-xl border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-2">Pose Overlay Video Output</h3>
          <video src={analysis.overlay_video_url} controls class="w-full rounded-lg bg-black aspect-video" />
        </div>
        <div className="p-4 bg-slate-800 rounded-xl border border-slate-700 space-y-3">
          <h3 className="text-sm font-semibold text-slate-300">Biomechanical Measurements</h3>
          {analysis.features.map((f, idx) => (
            <div key={idx} className="flex justify-between border-b border-slate-700/60 pb-1 text-sm">
              <span className="text-slate-400 capitalize">{f.feature_name.replace(/_/g, ' ')}</span>
              <span className="font-mono text-emerald-400 font-bold">{f.value} {f.unit}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
