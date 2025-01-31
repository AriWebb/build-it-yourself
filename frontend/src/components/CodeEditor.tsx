'use client';

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
}

export default function CodeEditor({ code, onChange }: CodeEditorProps) {
  const lines = code.split('\n').length;
  const lineNumbers = Array.from({ length: Math.max(lines, 10) }, (_, i) => i + 1);

  const handleSubmit = async () => {
    try {
      const response = await fetch('http://localhost:8000/submit-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: code }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit code');
      }

      const data = await response.json();
      console.log('Code submission result:', data.result);
      // You can add additional handling of the result here
    } catch (error) {
      console.error('Error submitting code:', error);
      // You can add error handling UI here
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
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={handleSubmit}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Submit Code
        </button>
      </div>
    </div>
  );
}
