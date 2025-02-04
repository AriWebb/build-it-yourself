'use client';

import { useState } from 'react';

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  websocket: WebSocket | null;
  clientId: string;
}

export default function CodeEditor({ code, onChange, websocket, clientId }: CodeEditorProps) {
  const [progress, setProgress] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);

  const lines = code.split('\n').length;
  const lineNumbers = Array.from({ length: Math.max(lines, 15) }, (_, i) => i + 1);

  // Set up message handler for the websocket
  if (websocket) {
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'progress') {
        setProgress(data.message);
      }
    };
  }

  const handleSubmit = async () => {
    if (!websocket) {
      console.error('WebSocket not connected');
      return;
    }

    try {
      setIsProcessing(true);
      setProgress('Submitting code...');

      const formData = new FormData();
      const blob = new Blob([code], { type: 'text/plain' });
      const file = new File([blob], 'code.py', { type: 'text/plain' });
      formData.append('file', file);

      const response = await fetch(`http://localhost:8000/analyze/${clientId}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to submit code');
      }

      const data = await response.json();
      // console.log('Code submission result:', data.result);
      // Result will be handled by the websocket in OutputEditor
    } catch (error) {
      console.error('Error submitting code:', error);
      setProgress('Error processing code');
    } finally {
      setIsProcessing(false);
    }
  };

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
        <textarea
          value={code}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 p-4 font-mono text-sm outline-none resize-none min-h-[300px]"
          placeholder="Paste your Python code here..."
          spellCheck={false}
        />
      </div>
      <div className="p-4 border-t border-gray-200 space-y-4">
        {progress && (
          <div className="p-3 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">{progress}</p>
            {isProcessing && (
              <div className="mt-2 w-full h-1 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 animate-pulse" style={{ width: '100%' }}></div>
              </div>
            )}
          </div>
        )}
        <div className="flex justify-between items-center">
          <button
            onClick={handleSubmit}
            disabled={isProcessing || !websocket}
            className={`px-4 py-2 bg-blue-500 text-white rounded transition-colors ${
              isProcessing || !websocket ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-600'
            }`}
          >
            {isProcessing ? 'Processing...' : 'Submit Code'}
          </button>
        </div>
      </div>
    </div>
  );
}
