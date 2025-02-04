'use client';

import { useState, useEffect } from 'react';

interface OutputEditorProps {
  websocket: WebSocket | null;
}

export default function OutputEditor({ websocket }: OutputEditorProps) {
  const [outputCode, setOutputCode] = useState('');
  const [displayedCode, setDisplayedCode] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const lines = displayedCode.split('\n').length;
  const lineNumbers = Array.from({ length: Math.max(lines, 15) }, (_, i) => i + 1);

  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      if (data.type === 'complete' && data.code) {
        setOutputCode(data.code);
        setIsTyping(true);
      }
    };

    websocket.addEventListener('message', handleMessage);

    return () => {
      websocket.removeEventListener('message', handleMessage);
    };
  }, [websocket]);

  useEffect(() => {
    if (!isTyping || !outputCode) return;

    let currentIndex = 0;
    const typingInterval = setInterval(() => {
      if (currentIndex <= outputCode.length) {
        setDisplayedCode(outputCode.slice(0, currentIndex));
        currentIndex++;
      } else {
        setIsTyping(false);
        clearInterval(typingInterval);
      }
    }, 8); // Adjust typing speed here

    return () => clearInterval(typingInterval);
  }, [outputCode, isTyping]);

  return (
    <div className="relative bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="flex">
        <div className="p-4 bg-gray-50 text-gray-400 text-sm font-mono border-r border-gray-200 select-none">
          {lineNumbers.map((num) => (
            <div key={num} className="text-right pr-2">
              {num}
            </div>
          ))}
        </div>
        <pre className="flex-1 p-4 font-mono text-sm min-h-[300px] whitespace-pre-wrap overflow-auto">
          {displayedCode}
        </pre>
      </div>
    </div>
  );
}