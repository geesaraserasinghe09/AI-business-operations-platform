import React, { useState, useEffect } from 'react';
import {
  FileText,
  Upload,
  Search,
  Trash2,
  Sparkles,
  Bot,
  RefreshCw,
  FileCheck,
  CheckCircle,
  HelpCircle
} from 'lucide-react';
import { api } from '../services/api';
import { DocumentItem } from '../types';

export const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  // RAG Q&A state
  const [question, setQuestion] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [ragResult, setRagResult] = useState<{
    question: string;
    answer: string;
    relevant_chunks: string[];
    source_documents: string[];
  } | null>(null);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const data = await api.documents.list();
      setDocuments(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await api.documents.upload(file);
      fetchDocuments();
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document and its vector embeddings?')) return;
    try {
      await api.documents.delete(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleRagQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || isQuerying) return;

    setIsQuerying(true);
    try {
      const res = await api.documents.queryRAG(question);
      setRagResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Document Intelligence & RAG
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Upload PDF, DOCX, and TXT operational documents for automated chunking, embedding, and semantic Q&A retrieval.
          </p>
        </div>

        {/* Upload Button */}
        <label className="flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow cursor-pointer transition shrink-0">
          <Upload className="w-4 h-4" />
          <span>{uploading ? 'Processing & Embedding...' : 'Upload Document'}</span>
          <input
            type="file"
            accept=".pdf,.docx,.txt,.md,.csv"
            disabled={uploading}
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
      </div>

      {/* RAG Conversational Q&A Section */}
      <div className="bg-white dark:bg-navy-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center justify-center font-bold">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">Ask Internal Documentation (RAG)</h2>
            <p className="text-xs text-slate-400">Ground answers in uploaded operational policies, SLAs, and manuals.</p>
          </div>
        </div>

        <form onSubmit={handleRagQuery} className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. What are the rules and threshold amounts for authorizing customer refunds?"
            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-white text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
          <button
            type="submit"
            disabled={isQuerying || !question.trim()}
            className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow transition disabled:opacity-50 flex items-center gap-1.5"
          >
            {isQuerying ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Bot className="w-4 h-4" />}
            <span>Query RAG</span>
          </button>
        </form>

        {/* Answer Card */}
        {ragResult && (
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-navy-950 border border-brand-200/60 dark:border-brand-900/60 space-y-3 text-xs animate-fadeIn">
            <div className="flex items-center justify-between text-brand-600 dark:text-brand-400 font-semibold">
              <span className="flex items-center gap-1.5">
                <Bot className="w-4 h-4" />
                <span>Grounded AI Synthesis</span>
              </span>
              <span className="text-[11px] text-slate-400">
                Sources: {ragResult.source_documents.join(', ') || 'Internal Docs'}
              </span>
            </div>
            <p className="text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-line">
              {ragResult.answer}
            </p>

            {ragResult.relevant_chunks.length > 0 && (
              <div className="pt-2 border-t border-slate-200/60 dark:border-slate-800 space-y-1.5">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Matched Vector Chunks:</span>
                {ragResult.relevant_chunks.map((ch, idx) => (
                  <div key={idx} className="p-2 bg-white dark:bg-navy-900 rounded border border-slate-200/60 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-400 italic">
                    "{ch.slice(0, 160)}..."
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Documents Table */}
      <div className="bg-white dark:bg-navy-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900 dark:text-white">Indexed Knowledge Base</h2>
          <span className="text-xs text-slate-400">{documents.length} documents indexed</span>
        </div>

        {loading && documents.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading indexed documents...</div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">
            No documents uploaded yet. Upload your first PDF, DOCX, or TXT file above.
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800/30 transition text-xs">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold uppercase text-[10px]">
                    {doc.file_type}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white">{doc.filename}</h3>
                    <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">{doc.content_summary}</p>
                    <div className="flex items-center gap-3 text-[10px] text-slate-400 mt-1 font-mono">
                      <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                      <span>•</span>
                      <span>{doc.chunks_count || 0} vector chunks</span>
                      <span>•</span>
                      <span>Uploaded: {new Date(doc.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(doc.id)}
                  title="Delete Document"
                  className="p-2 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
