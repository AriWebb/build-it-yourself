'use client';

import { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import CodeEditor from '../components/CodeEditor';
import OutputEditor from '../components/OutputEditor';
import FileUpload from '../components/FileUpload';

export default function Home() {
  const [code, setCode] = useState('');
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [clientId] = useState(() => uuidv4());

  const handleCodeChange = useCallback((newCode: string) => {
    setCode(newCode);
  }, []);

  const handleFileUpload = useCallback((content: string) => {
    setCode(content);
  }, []);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWebsocket(ws);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWebsocket(null);
    };

    return () => {
      ws.close();
    };
  }, [clientId]);

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Build It Yourself
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Transform your Python code by removing external dependencies. Our AI-powered tool 
            rewrites your code to be self-contained, making it easier to understand and maintain.
          </p>
        </div>

        <div className="space-y-8">
          <div className="space-y-8">
            <div>
              <h2 className="text-lg font-semibold mb-2">Input Code</h2>
              <CodeEditor 
                code={code} 
                onChange={handleCodeChange}
                websocket={websocket}
                clientId={clientId}
              />
            </div>
            <div>
              <h2 className="text-lg font-semibold mb-2">Generated Code</h2>
              <OutputEditor websocket={websocket} />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}