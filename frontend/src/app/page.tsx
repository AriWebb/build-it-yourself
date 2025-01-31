'use client';

import { useState } from 'react';
import CodeEditor from '../components/CodeEditor';
import FileUpload from '../components/FileUpload';

export default function Home() {
  const [code, setCode] = useState('');

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
  };

  const handleFileUpload = (content: string) => {
    setCode(content);
  };

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
          <CodeEditor code={code} onChange={handleCodeChange} />
          <FileUpload onUpload={handleFileUpload} />
        </div>
      </div>
    </main>
  );
}