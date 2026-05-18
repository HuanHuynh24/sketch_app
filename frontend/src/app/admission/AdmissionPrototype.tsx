"use client";

import React, { useState } from 'react';
import Navbar from "@/components/Navbar";
import { BridgeScreen } from "./components/BridgeScreen";
import { ProfileHeader } from "./components/ProfileHeader";
import { UniversityCard } from "./components/UniversityCard";
import { DetailPanel } from "./components/DetailPanel";
import { RagChatPanel } from "./components/RagChatPanel";
import { Target } from 'lucide-react';
import { options, UniversityOption } from "./components/data";

export default function AdmissionPrototype() {
  const [started, setStarted] = useState(false);
  const [selectedOpt, setSelectedOpt] = useState<UniversityOption | null>(null);

  if (!started) {
    return (
      <>
        <Navbar />
        <BridgeScreen onStart={() => setStarted(true)} />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-[#030014] text-white overflow-hidden flex flex-col">
      <Navbar />
      
      <main className="flex-1 pt-24 px-6 pb-6 max-w-[1600px] mx-auto w-full flex flex-col h-screen">
        <ProfileHeader />
        
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
          
          {/* Left: List */}
          <div className="lg:col-span-4 glass-panel bg-black/40 backdrop-blur-2xl border border-white/10 rounded-[2rem] p-6 overflow-auto custom-scrollbar flex flex-col gap-4">
             <h3 className="text-xl font-bold text-white mb-4 sticky top-0 bg-[#030014]/80 backdrop-blur-xl py-2 z-10 border-b border-white/10">Đề xuất hàng đầu</h3>
             {options.map((opt: UniversityOption) => (
               <UniversityCard 
                 key={opt.id} 
                 option={opt} 
                 selected={selectedOpt?.id === opt.id} 
                 onClick={() => setSelectedOpt(opt)} 
               />
             ))}
          </div>
          
          {/* Right: Master-Detail Split */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            {selectedOpt ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full min-h-0">
                <DetailPanel option={selectedOpt} />
                <RagChatPanel option={selectedOpt} />
              </div>
            ) : (
              <div className="glass-panel bg-black/40 border border-white/10 rounded-[2rem] flex flex-col items-center justify-center h-full text-center p-10">
                <div className="w-24 h-24 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(255,255,255,0.05)]">
                  <Target size={40} className="text-[#06b6d4] opacity-50" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">Chọn một trường để xem chi tiết</h3>
                <p className="text-[#94a3b8] max-w-sm">Hệ thống sẽ cung cấp thông tin tỷ lệ đỗ và kết nối bạn với AI cố vấn của từng trường cụ thể.</p>
              </div>
            )}
          </div>
          
        </div>
      </main>
    </div>
  );
}
