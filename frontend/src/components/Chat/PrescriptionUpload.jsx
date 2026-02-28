import { useState, useRef } from 'react';
import { UploadCloud, FileText, X, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

const PrescriptionUpload = ({ isOpen, onClose, onUploadComplete }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadState, setUploadState] = useState('idle'); // idle, uploading, success, error
  const inputRef = useRef(null);

  if (!isOpen) return null;

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const validateAndSetFile = (selectedFile) => {
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    if (selectedFile && validTypes.includes(selectedFile.type)) {
      setFile(selectedFile);
      setUploadState('idle');
    } else {
      setFile(null);
      setUploadState('error');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const simulateUpload = () => {
    if (!file) return;
    setUploadState('uploading');
    
    // Simulate backend processing time
    setTimeout(() => {
      setUploadState('success');
      setTimeout(() => {
        onUploadComplete(file.name);
        onClose();
        setFile(null);
        setUploadState('idle');
      }, 1500); // Close automatically after showing success
    }, 2000);
  };

  return (
    <div className="fixed inset-0 z-[90] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-md animate-in fade-in duration-300">
      <div className="glass-panel w-full max-w-md p-8 relative shadow-2xl animate-in zoom-in-95 duration-300 bg-white/70">
        
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 p-2 bg-white/50 hover:bg-white rounded-full text-slate-500 transition-colors"
        >
          <X size={20} />
        </button>

        <div className="text-center mb-6 mt-2">
          <h2 className="text-2xl font-extrabold text-slate-800 tracking-tight">Upload Prescription</h2>
          <p className="text-sm text-slate-500 mt-1 font-medium">Valid formats: PDF, JPG, PNG</p>
        </div>

        {uploadState === 'success' ? (
          <div className="flex flex-col items-center justify-center py-10 animate-in zoom-in duration-500">
            <div className="w-20 h-20 bg-emerald-100 text-emerald-500 rounded-full flex items-center justify-center mb-4 shadow-inner">
              <CheckCircle2 size={40} strokeWidth={2.5} />
            </div>
            <h3 className="text-xl font-bold text-slate-800">Upload Complete</h3>
            <p className="text-sm text-slate-500 mt-1">Analyzing Rx data...</p>
          </div>
        ) : (
          <>
            <form 
              onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
              onClick={() => inputRef.current.click()}
              className={`relative flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-3xl cursor-pointer transition-all duration-300 group ${
                dragActive ? 'border-emerald-500 bg-emerald-50/50' : 'border-slate-300 hover:border-emerald-400 bg-white/30 hover:bg-white/50'
              }`}
            >
              <input ref={inputRef} type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={handleChange} className="hidden" />
              
              <div className="p-4 bg-white shadow-sm rounded-full mb-3 group-hover:scale-110 group-hover:shadow-md transition-all">
                <UploadCloud size={32} className={dragActive ? 'text-emerald-500' : 'text-slate-400 group-hover:text-emerald-500'} />
              </div>
              <p className="text-sm font-bold text-slate-700">Drag & drop your file here</p>
              <p className="text-xs text-slate-400 mt-1 font-medium">or click to browse files</p>
            </form>

            {/* Error Message */}
            {uploadState === 'error' && (
              <div className="flex items-center gap-2 mt-4 p-3 bg-rose-50 text-rose-600 rounded-xl text-xs font-bold border border-rose-100">
                <AlertCircle size={16} /> Invalid file format. Please upload a PDF or Image.
              </div>
            )}

            {/* Selected File Preview */}
            {file && uploadState !== 'error' && (
              <div className="flex items-center justify-between mt-4 p-3 bg-white/60 border border-white/80 rounded-2xl shadow-sm">
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
                    <FileText size={18} />
                  </div>
                  <span className="text-sm font-semibold text-slate-700 truncate">{file.name}</span>
                </div>
                <button 
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="p-1.5 text-slate-400 hover:text-rose-500 rounded-md transition-colors"
                >
                  <X size={16} />
                </button>
              </div>
            )}

            <button 
              onClick={simulateUpload}
              disabled={!file || uploadState === 'uploading'}
              className="w-full mt-6 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-300 text-white p-4 rounded-2xl font-bold text-[15px] shadow-lg flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
            >
              {uploadState === 'uploading' ? (
                <><Loader2 size={18} className="animate-spin" /> Processing File...</>
              ) : (
                'Secure Upload'
              )}
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default PrescriptionUpload;