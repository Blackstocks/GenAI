"use client";

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [jobId, setJobId] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState("");

  const handleAsk = async () => {
    if (!query) return;

    setLoading(true);
    setResponse("");
    setJobId("");
    setUploadStatus("");

    try {
      const res = await fetch(
        `http://localhost:8000/chat?query=${encodeURIComponent(query)}`,
        {
          method: "POST",
        }
      );

      const data = await res.json();
      setJobId(data.job_id);

      const poll = async () => {
        const resultRes = await fetch(
          `http://localhost:8000/result/${data.job_id}`
        );
        const resultData = await resultRes.json();

        if (resultData.status === "finished") {
          setResponse(resultData.result);
          setLoading(false);
        } else if (resultData.status === "failed") {
          setResponse("❌ Job failed.");
          setLoading(false);
        } else {
          setTimeout(poll, 1000);
        }
      };

      poll();
    } catch (err) {
      console.error("Error sending query:", err);
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!file) {
      alert("Please select a PDF file first.");
      return;
    }

    setUploadStatus("Uploading...");
    setResponse("");
    setQuery("");

    try {
      const formData = new FormData();
      formData.append("pdf", file);

      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        setUploadStatus("✅ File uploaded successfully.");
      } else {
        setUploadStatus("❌ Upload failed.");
      }
    } catch (error) {
      console.error("Upload error:", error);
      setUploadStatus("❌ Upload failed due to network error.");
    }
  };

  return (
    <div className="flex min-h-screen bg-white text-gray-800">
      {/* Left: Upload */}
      <div className="w-1/3 border-r border-gray-200 p-6 bg-gray-50">
        <h2 className="text-2xl font-semibold mb-4">📄 Upload PDF</h2>
        <form onSubmit={handleFileUpload} className="space-y-4">
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full border border-gray-300 rounded p-2"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Upload
          </button>
        </form>
        {uploadStatus && <p className="mt-4 text-sm">{uploadStatus}</p>}
      </div>

      {/* Right: Chat */}
      <div className="flex-1 p-6">
        <h2 className="text-2xl font-semibold mb-4">💬 Ask the Assistant</h2>

        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something about the uploaded PDF..."
          className="w-full border border-gray-300 rounded p-3 h-24 resize-none"
        />

        <button
          onClick={handleAsk}
          disabled={loading}
          className="mt-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? "Processing..." : "Ask"}
        </button>

        {jobId && <p className="mt-2 text-sm text-gray-500">Job ID: {jobId}</p>}

        {response && (
          <div className="mt-6 bg-gray-100 border border-gray-200 p-4 rounded shadow-sm whitespace-pre-wrap">
            <strong>Response:</strong>
            <p className="mt-2">{response}</p>
          </div>
        )}
      </div>
    </div>
  );
}
