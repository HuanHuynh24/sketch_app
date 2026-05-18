import React, { useState } from 'react';
import { UniversityOption } from './data';
import { Bot, SendHorizontal } from 'lucide-react';

export function RagChatPanel({ option }: { option: UniversityOption }) {
  const [messages, setMessages] = useState([{ role: 'ai', text: `Chào bạn, tôi là cố vấn AI của ${option.shortName}. Bạn muốn hỏi thêm về học phí, chương trình học hay cơ hội việc làm của ngành ${option.major}?` }]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if(!input.trim()) return;
    setMessages([...messages, { role: 'user', text: input }]);
    setInput('');
    setTimeout(() => {
      setMessages(prev => [...prev, { role: 'ai', text: `Tôi đang phân tích câu hỏi về ${option.shortName}... Thực tế học phí có thể được giảm nếu bạn đạt học bổng đầu vào.` }]);
    }, 1000);
  };

  return (
    <div className="glass-panel bg-black/60 border border-white/10 rounded-3xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-white/10 bg-white/5 flex items-center gap-3">
        <Bot size={20} className="text-[#c084fc]"/> 
        <span className="font-bold text-white">AI Cố vấn Tư vấn</span>
      </div>
      
      <div className="flex-1 overflow-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
             <div className={`p-4 max-w-[85%] rounded-2xl ${m.role === 'user' ? 'bg-[#7c3aed] text-white rounded-tr-sm' : 'bg-white/10 text-[#f8fafc] border border-white/10 rounded-tl-sm'}`}>
               {m.text}
             </div>
          </div>
        ))}
      </div>
      
      <div className="p-3 border-t border-white/10 bg-black/40 flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="Hỏi AI về trường này..."
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-[#06b6d4]/50 transition-colors"
        />
        <button onClick={handleSend} className="w-12 h-12 bg-[#06b6d4] text-black rounded-xl flex items-center justify-center hover:bg-[#06b6d4]/80 transition-colors">
          <SendHorizontal size={20}/>
        </button>
      </div>
    </div>
  );
}
