import React from 'react';

export const Dashboard: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-100">Virtual Cricket Coach Dashboard</h1>
        <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-xs font-semibold">
          Academic AI Prototype
        </span>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-5 bg-slate-800 rounded-xl border border-slate-700">
          <p className="text-xs text-slate-400">Target Shots Supported</p>
          <p class="text-3xl font-extrabold text-white mt-1">5 Shots</p>
          <p class="text-xs text-slate-500 mt-1">Defence, Drives, Pull, Cut</p>
        </div>
        <div className="p-5 bg-slate-800 rounded-xl border border-slate-700">
          <p className="text-xs text-slate-400">Pose Model</p>
          <p className="text-3xl font-extrabold text-emerald-400 mt-1">MediaPipe 3D</p>
          <p className="text-xs text-slate-500 mt-1">33 Anatomical Joints</p>
        </div>
        <div className="p-5 bg-slate-800 rounded-xl border border-slate-700">
          <p className="text-xs text-slate-400">Angle Formula</p>
          <p className="text-3xl font-extrabold text-sky-400 mt-1">Vector Dot Product</p>
          <p className="text-xs text-slate-500 mt-1">Numerical Clamping</p>
        </div>
      </div>
    </div>
  );
};
