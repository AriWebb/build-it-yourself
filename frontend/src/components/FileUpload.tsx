'use client';

import { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { v4 as uuidv4 } from 'uuid';

interface FileUploadProps {
  onUpload: (content: string) => void;
}

interface ProgressMessage {
  type: string;
  message: string;
}

export default function FileUpload({ onUpload }: FileUploadProps) {
  const [clientId] = useState(uuidv4());
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [progress, setProgress] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setWs(websocket);
    };

    websocket.onmessage = (event) => {
      const data: ProgressMessage = JSON.parse(event.data);
      if (data.type === 'progress') {
        setProgress(data.message);
      }
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setWs(null);
    };

    return () => {
      websocket.close();
    };
  }, [clientId]);
  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach(async (file) => {
      if (file.name.endsWith('.py')) {
        setIsProcessing(true);
        setProgress('Uploading file...');

        const formData = new FormData();
        formData.append('file', file);

        try {
          const response = await fetch(`http://localhost:8000/analyze/${clientId}`, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error('Analysis failed');
          }

          const result = await response.json();
          onUpload(result.result);
        } catch (error) {
          console.error('Error:', error);
          setProgress('Error processing file');
        } finally {
          setIsProcessing(false);
        }
      }
    });
  }, [clientId, onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/x-python': ['.py'],
    },
    multiple: false,
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`p-8 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${isProcessing ? 'pointer-events-none opacity-50' : ''}`}
      >
        <input {...getInputProps()} />
        <p className="text-gray-600">
          {isDragActive
            ? 'Drop your Python file here...'
            : 'Drag and drop a Python file here, or click to select'}
        </p>
        <p className="text-sm text-gray-500 mt-2">Only .py files are accepted</p>
      </div>
      
      {progress && (
        <div className="p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">{progress}</p>
          {isProcessing && (
            <div className="mt-2 w-full h-1 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 animate-pulse" style={{ width: '100%' }}></div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
