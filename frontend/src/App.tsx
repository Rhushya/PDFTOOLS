import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import axios from 'axios';
import {
  FileText,
  Upload,
  Merge,
  Scissors,
  RotateCw,
  Minimize2,
  Droplets,
  Hash,
  FileOutput,
  Image,
  Lock,
  Unlock,
  Trash2,
  Download,
  X,
  Check,
  Loader2,
  ChevronRight,
  Sparkles,
  Shield,
  Zap,
  FileImage,
  FileType,
  RefreshCw
} from 'lucide-react';
import './App.css';

const API_URL = '/api';

interface UploadedFile {
  file: File;
  id: string;
  preview?: string;
}

interface Operation {
  id: string;
  name: string;
  icon: React.ReactNode;
  endpoint: string;
  description: string;
  category: string;
  color: string;
}

const operations: Operation[] = [
  { id: 'merge', name: 'Merge PDFs', icon: <Merge size={24} />, endpoint: '/pdf/merge', description: 'Combine multiple PDFs into one', category: 'organize', color: '#3B82F6' },
  { id: 'split', name: 'Split PDF', icon: <Scissors size={24} />, endpoint: '/pdf/split', description: 'Extract pages from PDF', category: 'organize', color: '#8B5CF6' },
  { id: 'rotate', name: 'Rotate Pages', icon: <RotateCw size={24} />, endpoint: '/pdf/rotate', description: 'Rotate PDF pages', category: 'organize', color: '#EC4899' },
  { id: 'compress', name: 'Compress PDF', icon: <Minimize2 size={24} />, endpoint: '/pdf/compress', description: 'Reduce file size', category: 'optimize', color: '#10B981' },
  { id: 'watermark', name: 'Add Watermark', icon: <Droplets size={24} />, endpoint: '/pdf/watermark', description: 'Add text watermark', category: 'enhance', color: '#F59E0B' },
  { id: 'page-numbers', name: 'Page Numbers', icon: <Hash size={24} />, endpoint: '/pdf/page-numbers', description: 'Add page numbers', category: 'enhance', color: '#6366F1' },
  { id: 'extract-text', name: 'Extract Text', icon: <FileOutput size={24} />, endpoint: '/pdf/extract-text', description: 'Extract text content', category: 'extract', color: '#14B8A6' },
  { id: 'extract-images', name: 'Extract Images', icon: <Image size={24} />, endpoint: '/pdf/extract-images', description: 'Extract all images', category: 'extract', color: '#F97316' },
  { id: 'image-to-pdf', name: 'Image to PDF', icon: <FileImage size={24} />, endpoint: '/convert/image-to-pdf', description: 'Convert images to PDF', category: 'convert', color: '#06B6D4' },
  { id: 'pdf-to-jpg', name: 'PDF to JPG', icon: <FileType size={24} />, endpoint: '/convert/pdf-to-jpg', description: 'Convert PDF to images', category: 'convert', color: '#84CC16' },
  { id: 'protect', name: 'Protect PDF', icon: <Lock size={24} />, endpoint: '/security/protect', description: 'Add password protection', category: 'security', color: '#EF4444' },
  { id: 'unlock', name: 'Unlock PDF', icon: <Unlock size={24} />, endpoint: '/security/unlock', description: 'Remove password', category: 'security', color: '#22C55E' },
];

const categories = [
  { id: 'all', name: 'All Tools', icon: <Sparkles size={18} /> },
  { id: 'organize', name: 'Organize', icon: <FileText size={18} /> },
  { id: 'optimize', name: 'Optimize', icon: <Zap size={18} /> },
  { id: 'convert', name: 'Convert', icon: <RefreshCw size={18} /> },
  { id: 'enhance', name: 'Enhance', icon: <Droplets size={18} /> },
  { id: 'extract', name: 'Extract', icon: <FileOutput size={18} /> },
  { id: 'security', name: 'Security', icon: <Shield size={18} /> },
];

function App() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [selectedOperation, setSelectedOperation] = useState<Operation | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState<{ title: string; message: string; type: 'success' | 'error' | 'info' }>({ title: '', message: '', type: 'info' });
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [extraParams, setExtraParams] = useState<Record<string, string>>({});

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));
    setFiles(prev => [...prev, ...newFiles]);
    toast.success(`${acceptedFiles.length} file(s) added`);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    }
  });

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
    toast.success('File removed');
  };

  const clearAllFiles = () => {
    setFiles([]);
    toast.success('All files cleared');
  };

  const processFiles = async () => {
    if (!selectedOperation || files.length === 0) {
      toast.error('Please select an operation and upload files');
      return;
    }

    setIsProcessing(true);
    setProgress(0);

    const formData = new FormData();
    
    if (selectedOperation.id === 'merge' || selectedOperation.id === 'image-to-pdf') {
      files.forEach(f => formData.append('files', f.file));
    } else {
      formData.append('file', files[0].file);
    }

    Object.entries(extraParams).forEach(([key, value]) => {
      formData.append(key, value);
    });

    try {
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await axios.post(`${API_URL}${selectedOperation.endpoint}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setProgress(percentCompleted);
          }
        }
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (response.data.success) {
        const downloadLink = response.data.data.download_url;
        setDownloadUrl(downloadLink);
        setModalContent({
          title: 'Success!',
          message: response.data.message || 'Operation completed successfully',
          type: 'success'
        });
        setShowModal(true);
        toast.success('Operation completed!');
      } else {
        throw new Error(response.data.message);
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      setModalContent({
        title: 'Error',
        message: err.response?.data?.message || err.message || 'An error occurred',
        type: 'error'
      });
      setShowModal(true);
      toast.error('Operation failed');
    } finally {
      setIsProcessing(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  const filteredOperations = selectedCategory === 'all' 
    ? operations 
    : operations.filter(op => op.category === selectedCategory);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="app">
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(30, 30, 30, 0.95)',
            color: '#fff',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.1)',
          },
        }}
      />

      <div className="background-gradient"></div>
      <div className="background-blur"></div>

      <motion.header 
        className="header"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="header-content">
          <div className="logo">
            <motion.div 
              className="logo-icon"
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
            >
              <FileText size={32} />
            </motion.div>
            <div className="logo-text">
              <h1>PDFMaster</h1>
              <span>Professional PDF Tools</span>
            </div>
          </div>
          <nav className="nav-links">
            <a href="#tools">Tools</a>
            <a href="#upload">Upload</a>
            <motion.button 
              className="btn-glow"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Started
            </motion.button>
          </nav>
        </div>
      </motion.header>

      <motion.section 
        className="hero"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        <div className="hero-content">
          <motion.h2
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            All-in-One <span className="gradient-text">PDF Solution</span>
          </motion.h2>
          <motion.p
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            Merge, split, compress, convert and edit PDF files with ease.
            Free, secure, and runs entirely on your machine.
          </motion.p>
          <motion.div 
            className="hero-stats"
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <div className="stat">
              <span className="stat-number">12+</span>
              <span className="stat-label">PDF Tools</span>
            </div>
            <div className="stat">
              <span className="stat-number">100%</span>
              <span className="stat-label">Free & Secure</span>
            </div>
            <div className="stat">
              <span className="stat-number">Local</span>
              <span className="stat-label">Processing</span>
            </div>
          </motion.div>
        </div>
      </motion.section>

      <main className="main-content">
        <motion.section 
          id="upload"
          className="upload-section glass-card"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h3><Upload size={24} /> Upload Your Files</h3>
          
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <motion.div 
              className="dropzone-content"
              animate={{ y: isDragActive ? -10 : 0 }}
              whileHover={{ scale: 1.02 }}
            >
              <div className="dropzone-icon">
                <Upload size={48} />
              </div>
              <p className="dropzone-title">
                {isDragActive ? 'Drop files here...' : 'Drag & drop files here'}
              </p>
              <p className="dropzone-subtitle">or click to browse</p>
              <span className="dropzone-formats">PDF, JPG, PNG, DOCX supported</span>
            </motion.div>
          </div>

          <AnimatePresence>
            {files.length > 0 && (
              <motion.div 
                className="file-list"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
              >
                <div className="file-list-header">
                  <h4>{files.length} file(s) selected</h4>
                  <motion.button 
                    className="btn-clear"
                    onClick={clearAllFiles}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Trash2 size={16} /> Clear All
                  </motion.button>
                </div>
                
                {files.map((file, index) => (
                  <motion.div 
                    key={file.id}
                    className="file-item"
                    initial={{ x: -50, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: 50, opacity: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <div className="file-icon">
                      {file.preview ? (
                        <img src={file.preview} alt="" className="file-preview" />
                      ) : (
                        <FileText size={24} />
                      )}
                    </div>
                    <div className="file-info">
                      <span className="file-name">{file.file.name}</span>
                      <span className="file-size">{formatFileSize(file.file.size)}</span>
                    </div>
                    <motion.button 
                      className="btn-remove"
                      onClick={() => removeFile(file.id)}
                      whileHover={{ scale: 1.1, backgroundColor: 'rgba(239, 68, 68, 0.2)' }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <X size={18} />
                    </motion.button>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.section>

        <motion.section 
          id="tools"
          className="operations-section"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <h3><Sparkles size={24} /> Choose Operation</h3>

          <div className="category-filter">
            {categories.map((cat) => (
              <motion.button
                key={cat.id}
                className={`category-btn ${selectedCategory === cat.id ? 'active' : ''}`}
                onClick={() => setSelectedCategory(cat.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {cat.icon}
                {cat.name}
              </motion.button>
            ))}
          </div>

          <motion.div className="operations-grid" layout>
            <AnimatePresence mode="popLayout">
              {filteredOperations.map((op, index) => (
                <motion.button
                  key={op.id}
                  className={`operation-card ${selectedOperation?.id === op.id ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedOperation(op);
                    setExtraParams({});
                  }}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.8, opacity: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ 
                    scale: 1.03, 
                    y: -5,
                    boxShadow: `0 20px 40px ${op.color}30`
                  }}
                  whileTap={{ scale: 0.97 }}
                  style={{ '--accent-color': op.color } as React.CSSProperties}
                >
                  <div className="operation-icon" style={{ background: `${op.color}20`, color: op.color }}>
                    {op.icon}
                  </div>
                  <div className="operation-info">
                    <span className="operation-name">{op.name}</span>
                    <span className="operation-desc">{op.description}</span>
                  </div>
                  <ChevronRight size={20} className="operation-arrow" />
                </motion.button>
              ))}
            </AnimatePresence>
          </motion.div>
        </motion.section>

        <AnimatePresence>
          {selectedOperation && (
            <motion.section 
              className="params-section glass-card"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
            >
              <h4>Options for {selectedOperation.name}</h4>
              <div className="params-grid">
                {selectedOperation.id === 'watermark' && (
                  <>
                    <div className="param-group">
                      <label>Watermark Text</label>
                      <input 
                        type="text" 
                        placeholder="Enter watermark text"
                        value={extraParams.text || ''}
                        onChange={(e) => setExtraParams(prev => ({ ...prev, text: e.target.value }))}
                      />
                    </div>
                    <div className="param-group">
                      <label>Opacity (0-1)</label>
                      <input 
                        type="number" 
                        min="0" 
                        max="1" 
                        step="0.1"
                        placeholder="0.3"
                        value={extraParams.opacity || ''}
                        onChange={(e) => setExtraParams(prev => ({ ...prev, opacity: e.target.value }))}
                      />
                    </div>
                  </>
                )}
                {selectedOperation.id === 'rotate' && (
                  <div className="param-group">
                    <label>Rotation Angle</label>
                    <select 
                      value={extraParams.angle || '90'}
                      onChange={(e) => setExtraParams(prev => ({ ...prev, angle: e.target.value }))}
                    >
                      <option value="90">90°</option>
                      <option value="180">180°</option>
                      <option value="270">270°</option>
                    </select>
                  </div>
                )}
                {selectedOperation.id === 'compress' && (
                  <div className="param-group">
                    <label>Quality</label>
                    <select 
                      value={extraParams.quality || 'medium'}
                      onChange={(e) => setExtraParams(prev => ({ ...prev, quality: e.target.value }))}
                    >
                      <option value="low">Low (Smallest Size)</option>
                      <option value="medium">Medium (Balanced)</option>
                      <option value="high">High (Best Quality)</option>
                    </select>
                  </div>
                )}
                {(selectedOperation.id === 'protect' || selectedOperation.id === 'unlock') && (
                  <div className="param-group">
                    <label>Password</label>
                    <input 
                      type="password" 
                      placeholder="Enter password"
                      value={extraParams.password || ''}
                      onChange={(e) => setExtraParams(prev => ({ ...prev, password: e.target.value }))}
                    />
                  </div>
                )}
                {selectedOperation.id === 'split' && (
                  <div className="param-group">
                    <label>Pages (e.g., 1,3,5-7)</label>
                    <input 
                      type="text" 
                      placeholder="Leave empty for all pages"
                      value={extraParams.pages || ''}
                      onChange={(e) => setExtraParams(prev => ({ ...prev, pages: e.target.value }))}
                    />
                  </div>
                )}
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        <motion.section 
          className="action-section"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <AnimatePresence>
            {isProcessing && (
              <motion.div 
                className="progress-container"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
              >
                <div className="progress-bar">
                  <motion.div 
                    className="progress-fill"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
                <span className="progress-text">{progress}% Complete</span>
              </motion.div>
            )}
          </AnimatePresence>

          <motion.button
            className="btn-process"
            onClick={processFiles}
            disabled={isProcessing || files.length === 0 || !selectedOperation}
            whileHover={{ scale: 1.02, boxShadow: '0 20px 40px rgba(99, 102, 241, 0.4)' }}
            whileTap={{ scale: 0.98 }}
          >
            {isProcessing ? (
              <>
                <Loader2 className="spin" size={24} />
                Processing...
              </>
            ) : (
              <>
                <Zap size={24} />
                Process Files
              </>
            )}
          </motion.button>

          {selectedOperation && (
            <p className="selected-operation-info">
              Selected: <strong>{selectedOperation.name}</strong> • {files.length} file(s)
            </p>
          )}
        </motion.section>
      </main>

      <AnimatePresence>
        {showModal && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowModal(false)}
          >
            <motion.div 
              className={`modal glass-card ${modalContent.type}`}
              initial={{ scale: 0.8, y: 50, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.8, y: 50, opacity: 0 }}
              transition={{ type: "spring", damping: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className={`modal-icon ${modalContent.type}`}>
                {modalContent.type === 'success' ? <Check size={48} /> : <X size={48} />}
              </div>
              <h3>{modalContent.title}</h3>
              <p>{modalContent.message}</p>
              
              <div className="modal-actions">
                {downloadUrl && modalContent.type === 'success' && (
                  <motion.a
                    href={downloadUrl}
                    className="btn-download"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    download
                  >
                    <Download size={20} />
                    Download Result
                  </motion.a>
                )}
                <motion.button
                  className="btn-close"
                  onClick={() => setShowModal(false)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Close
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <footer className="footer">
        <p>© 2026 PDFMaster • All your PDF needs in one place</p>
        <p className="footer-sub">Powered by Python & React • 100% Open Source</p>
      </footer>
    </div>
  );
}

export default App;
