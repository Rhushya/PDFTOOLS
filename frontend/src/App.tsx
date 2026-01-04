import { useState, useCallback, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
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
  Download,
  X,
  Loader2,
  Sparkles,
  Shield,
  Zap,
  FileImage,
  FileType,
  RefreshCw,
  ArrowRight,
  ChevronDown,
  CheckCircle2,
  Github,
  Twitter,
  Linkedin,
  Mail
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
  { id: 'merge', name: 'Merge PDFs', icon: <Merge size={28} />, endpoint: '/pdf/merge', description: 'Combine multiple PDF files into a single document', category: 'organize', color: '#FF6B4A' },
  { id: 'split', name: 'Split PDF', icon: <Scissors size={28} />, endpoint: '/pdf/split', description: 'Extract specific pages or split into multiple files', category: 'organize', color: '#FF6B4A' },
  { id: 'rotate', name: 'Rotate Pages', icon: <RotateCw size={28} />, endpoint: '/pdf/rotate', description: 'Rotate PDF pages to any angle you need', category: 'organize', color: '#FF6B4A' },
  { id: 'compress', name: 'Compress PDF', icon: <Minimize2 size={28} />, endpoint: '/pdf/compress', description: 'Reduce file size while maintaining quality', category: 'optimize', color: '#4ECDC4' },
  { id: 'watermark', name: 'Add Watermark', icon: <Droplets size={28} />, endpoint: '/pdf/watermark', description: 'Add custom text watermarks to your PDFs', category: 'enhance', color: '#FFE66D' },
  { id: 'page-numbers', name: 'Page Numbers', icon: <Hash size={28} />, endpoint: '/pdf/page-numbers', description: 'Automatically add page numbers to documents', category: 'enhance', color: '#FFE66D' },
  { id: 'extract-text', name: 'Extract Text', icon: <FileOutput size={28} />, endpoint: '/pdf/extract-text', description: 'Pull all text content from PDF files', category: 'extract', color: '#95E1D3' },
  { id: 'extract-images', name: 'Extract Images', icon: <Image size={28} />, endpoint: '/pdf/extract-images', description: 'Extract all embedded images from PDFs', category: 'extract', color: '#95E1D3' },
  { id: 'image-to-pdf', name: 'Image to PDF', icon: <FileImage size={28} />, endpoint: '/convert/image-to-pdf', description: 'Convert images into PDF documents', category: 'convert', color: '#DDA0DD' },
  { id: 'pdf-to-jpg', name: 'PDF to JPG', icon: <FileType size={28} />, endpoint: '/convert/pdf-to-jpg', description: 'Convert PDF pages to high-quality images', category: 'convert', color: '#DDA0DD' },
  { id: 'protect', name: 'Protect PDF', icon: <Lock size={28} />, endpoint: '/security/protect', description: 'Secure your PDFs with password protection', category: 'security', color: '#F38181' },
  { id: 'unlock', name: 'Unlock PDF', icon: <Unlock size={28} />, endpoint: '/security/unlock', description: 'Remove password protection from PDFs', category: 'security', color: '#F38181' },
];

const categories = [
  { id: 'all', name: 'ALL TOOLS', icon: <Sparkles size={16} /> },
  { id: 'organize', name: 'ORGANIZE', icon: <FileText size={16} /> },
  { id: 'optimize', name: 'OPTIMIZE', icon: <Zap size={16} /> },
  { id: 'convert', name: 'CONVERT', icon: <RefreshCw size={16} /> },
  { id: 'enhance', name: 'ENHANCE', icon: <Droplets size={16} /> },
  { id: 'extract', name: 'EXTRACT', icon: <FileOutput size={16} /> },
  { id: 'security', name: 'SECURITY', icon: <Shield size={16} /> },
];

const features = [
  { icon: <Zap size={24} />, title: 'LIGHTNING FAST', desc: 'Process PDFs in seconds with optimized algorithms' },
  { icon: <Shield size={24} />, title: 'FULLY SECURE', desc: 'All processing happens locally on your machine' },
  { icon: <Sparkles size={24} />, title: 'NO LIMITS', desc: 'No file size restrictions or daily limits' },
  { icon: <RefreshCw size={24} />, title: 'ALWAYS FREE', desc: 'All tools are completely free to use' },
];

function App() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [selectedOperation, setSelectedOperation] = useState<Operation | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [showOperationModal, setShowOperationModal] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [extraParams, setExtraParams] = useState<Record<string, string>>({});
  const [scrolled, setScrolled] = useState(false);
  
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.3], [1, 0.95]);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Smooth scroll
  useEffect(() => {
    document.documentElement.style.scrollBehavior = 'smooth';
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));
    setFiles(prev => [...prev, ...newFiles]);
    toast.success(`${acceptedFiles.length} file(s) added`, {
      icon: '📄',
      style: {
        background: '#1a1a2e',
        color: '#fff',
        border: '1px solid rgba(255,107,74,0.3)',
      },
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
    }
  });

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const clearAllFiles = () => {
    setFiles([]);
  };

  const closeOperationModal = () => {
    setShowOperationModal(false);
    setFiles([]);
    setSelectedOperation(null);
    setExtraParams({});
  };

  const handleOperationClick = (op: Operation) => {
    setSelectedOperation(op);
    setShowOperationModal(true);
    setFiles([]);
    setExtraParams({});
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
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (response.data.success) {
        const downloadLink = response.data.data.download_url;
        setDownloadUrl(downloadLink);
        setShowModal(true);
        toast.success('Operation completed!', {
          icon: '✨',
          style: {
            background: '#1a1a2e',
            color: '#fff',
            border: '1px solid rgba(78,205,196,0.3)',
          },
        });
      } else {
        throw new Error(response.data.message);
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      toast.error(err.response?.data?.message || err.message || 'An error occurred');
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

  const scrollToTools = () => {
    document.getElementById('tools')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="app">
      <Toaster position="top-center" />

      {/* Animated Background */}
      <div className="bg-pattern">
        <div className="bg-grid"></div>
        <div className="bg-gradient-orb orb-1"></div>
        <div className="bg-gradient-orb orb-2"></div>
        <div className="bg-gradient-orb orb-3"></div>
      </div>

      {/* Header */}
      <motion.header 
        className={`header ${scrolled ? 'header-scrolled' : ''}`}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="header-inner">
          <motion.div 
            className="logo"
            whileHover={{ scale: 1.02 }}
          >
            <span className="logo-text">pdfmaster</span>
          </motion.div>
          
          <nav className="nav">
            <a href="#tools" className="nav-link">TOOLS</a>
            <a href="#features" className="nav-link">FEATURES</a>
          </nav>

          <motion.button 
            className="btn-primary"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={scrollToTools}
          >
            GET STARTED
          </motion.button>
        </div>
      </motion.header>

      {/* Hero Section */}
      <motion.section 
        ref={heroRef}
        className="hero"
        style={{ opacity: heroOpacity, scale: heroScale }}
      >
        <div className="hero-content">
          <motion.div 
            className="hero-badge"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <span className="badge-dot"></span>
            FREE & OPEN SOURCE
          </motion.div>

          <motion.h1 
            className="hero-title"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          >
            TRANSFORM.<br />
            <span className="title-accent">ORGANIZE.</span><br />
            ACCELERATE.
          </motion.h1>

          <motion.p 
            className="hero-subtitle"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            PDF TOOLS BUILT FOR SPEED. WIRED FOR SIMPLICITY.
          </motion.p>

          <motion.p 
            className="hero-desc"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.6 }}
          >
            PDFMaster puts powerful PDF tools at your fingertips. Forget clunky software and 
            online limits - this is PDF processing with a turbo boost. From merge to convert 
            in seconds, PDFMaster is your productivity powerhouse.
          </motion.p>

          <motion.button 
            className="btn-hero"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            whileHover={{ scale: 1.05, x: 5 }}
            whileTap={{ scale: 0.95 }}
            onClick={scrollToTools}
          >
            GO FROM FILES TO DONE <ArrowRight size={20} />
          </motion.button>

          <motion.div 
            className="scroll-indicator"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            onClick={scrollToTools}
          >
            <ChevronDown size={24} className="bounce" />
          </motion.div>
        </div>

        {/* Floating Elements */}
        <div className="hero-visual">
          <motion.div 
            className="floating-card card-1"
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8, duration: 0.8 }}
          >
            <div className="card-icon"><Merge size={32} /></div>
            <span>Merge</span>
          </motion.div>
          <motion.div 
            className="floating-card card-2"
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9, duration: 0.8 }}
          >
            <div className="card-icon"><Scissors size={32} /></div>
            <span>Split</span>
          </motion.div>
          <motion.div 
            className="floating-card card-3"
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.0, duration: 0.8 }}
          >
            <div className="card-icon"><Lock size={32} /></div>
            <span>Protect</span>
          </motion.div>
          
          {/* Connecting Lines Animation */}
          <svg className="connection-lines" viewBox="0 0 300 200">
            <motion.path
              d="M50,100 Q150,50 250,100"
              stroke="#FF6B4A"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 1.2, duration: 1.5 }}
            />
            <motion.path
              d="M50,100 Q150,150 250,100"
              stroke="#FF6B4A"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 1.4, duration: 1.5 }}
            />
            <motion.circle cx="50" cy="100" r="12" fill="#FF6B4A" 
              initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 1.1 }} />
            <motion.circle cx="250" cy="100" r="12" fill="#FF6B4A"
              initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 1.6 }} />
          </svg>
        </div>
      </motion.section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="features-grid">
          {features.map((feature, index) => (
            <motion.div 
              key={index}
              className="feature-card"
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ delay: index * 0.1, duration: 0.6 }}
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-desc">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Tools Section */}
      <section id="tools" className="tools-section">
        <motion.div 
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="section-title">POWERFUL TOOLS</h2>
          <p className="section-subtitle">Everything you need to work with PDFs</p>
        </motion.div>

        {/* Category Filter */}
        <motion.div 
          className="category-filter"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
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
        </motion.div>

        {/* Operations Grid */}
        <motion.div 
          className="tools-grid"
          layout
        >
          <AnimatePresence mode="popLayout">
            {filteredOperations.map((op, index) => (
              <motion.div
                key={op.id}
                className={`tool-card ${selectedOperation?.id === op.id ? 'selected' : ''}`}
                layout
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ delay: index * 0.05, duration: 0.3 }}
                whileHover={{ 
                  y: -12, 
                  scale: 1.02,
                  transition: { duration: 0.2 } 
                }}
                onClick={() => handleOperationClick(op)}
                style={{ '--card-color': op.color } as React.CSSProperties}
              >
                <div className="tool-icon" style={{ backgroundColor: `${op.color}20`, color: op.color }}>
                  {op.icon}
                </div>
                <h3 className="tool-name">{op.name}</h3>
                <p className="tool-desc">{op.description}</p>
                <div className="tool-arrow">
                  <ArrowRight size={18} />
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      </section>

      {/* Success Modal */}
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
              className="modal"
              initial={{ opacity: 0, scale: 0.8, y: 50 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 50 }}
              transition={{ type: "spring", damping: 25 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-icon">
                <CheckCircle2 size={64} />
              </div>
              <h3>Success!</h3>
              <p>Your file has been processed successfully</p>
              {downloadUrl && (
                <motion.a
                  href={downloadUrl}
                  className="btn-download"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Download size={20} />
                  DOWNLOAD FILE
                </motion.a>
              )}
              <button className="modal-close" onClick={() => setShowModal(false)}>
                Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Operation Modal - Popup when clicking on any operation */}
      <AnimatePresence>
        {showOperationModal && selectedOperation && (
          <motion.div 
            className="modal-overlay operation-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeOperationModal}
          >
            <motion.div 
              className="operation-modal"
              initial={{ opacity: 0, scale: 0.9, y: 30 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 30 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="operation-modal-header" style={{ borderColor: selectedOperation.color }}>
                <div className="operation-modal-title">
                  <div className="operation-modal-icon" style={{ backgroundColor: `${selectedOperation.color}20`, color: selectedOperation.color }}>
                    {selectedOperation.icon}
                  </div>
                  <div>
                    <h2>{selectedOperation.name}</h2>
                    <p>{selectedOperation.description}</p>
                  </div>
                </div>
                <button className="modal-close-btn" onClick={closeOperationModal}>
                  <X size={24} />
                </button>
              </div>

              {/* Modal Body */}
              <div className="operation-modal-body">
                {/* Dropzone */}
                <div {...getRootProps()}>
                  <input {...getInputProps()} />
                  <motion.div 
                    className={`dropzone modal-dropzone ${isDragActive ? 'drag-active' : ''}`}
                    whileHover={{ scale: 1.01 }}
                    animate={isDragActive ? { scale: 1.02, borderColor: selectedOperation.color } : {}}
                  >
                    <motion.div 
                      className="dropzone-icon"
                      animate={isDragActive ? { y: -10, scale: 1.1 } : { y: 0, scale: 1 }}
                      style={{ color: selectedOperation.color }}
                    >
                      <Upload size={40} />
                    </motion.div>
                    <p className="dropzone-title">
                      {isDragActive ? 'Drop files here...' : 'Drag & drop files here'}
                    </p>
                    <p className="dropzone-subtitle">or click to browse</p>
                    <span className="dropzone-hint">
                      {selectedOperation.id === 'image-to-pdf' ? 'JPG, PNG, GIF supported' : 'PDF files supported'}
                    </span>
                  </motion.div>
                </div>

                {/* File List */}
                <AnimatePresence>
                  {files.length > 0 && (
                    <motion.div 
                      className="file-list modal-file-list"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                    >
                      <div className="file-list-header">
                        <span>{files.length} file(s) selected</span>
                        <button onClick={clearAllFiles} className="clear-all">
                          Clear all
                        </button>
                      </div>
                      {files.map((file, index) => (
                        <motion.div 
                          key={file.id}
                          className="file-item"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: 20 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <FileText size={20} className="file-icon" />
                          <div className="file-info">
                            <span className="file-name">{file.file.name}</span>
                            <span className="file-size">{formatFileSize(file.file.size)}</span>
                          </div>
                          <button onClick={() => removeFile(file.id)} className="remove-file">
                            <X size={16} />
                          </button>
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Extra Parameters */}
                <AnimatePresence>
                  {(selectedOperation.id === 'rotate' || selectedOperation.id === 'split' || 
                    selectedOperation.id === 'watermark' || selectedOperation.id === 'protect' ||
                    selectedOperation.id === 'unlock') && (
                    <motion.div 
                      className="params-section modal-params"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                    >
                      {selectedOperation.id === 'rotate' && (
                        <div className="param-group">
                          <label>Rotation Angle</label>
                          <select 
                            value={extraParams.angle || '90'}
                            onChange={(e) => setExtraParams({...extraParams, angle: e.target.value})}
                            className="param-select"
                          >
                            <option value="90">90° Clockwise</option>
                            <option value="180">180°</option>
                            <option value="270">270° (90° Counter-clockwise)</option>
                          </select>
                        </div>
                      )}
                      {selectedOperation.id === 'split' && (
                        <div className="param-group">
                          <label>Page Range (e.g., 1-3)</label>
                          <input 
                            type="text"
                            value={extraParams.pages || ''}
                            onChange={(e) => setExtraParams({...extraParams, pages: e.target.value})}
                            placeholder="1-3 or 1,3,5"
                            className="param-input"
                          />
                        </div>
                      )}
                      {selectedOperation.id === 'watermark' && (
                        <div className="param-group">
                          <label>Watermark Text</label>
                          <input 
                            type="text"
                            value={extraParams.text || ''}
                            onChange={(e) => setExtraParams({...extraParams, text: e.target.value})}
                            placeholder="CONFIDENTIAL"
                            className="param-input"
                          />
                        </div>
                      )}
                      {(selectedOperation.id === 'protect' || selectedOperation.id === 'unlock') && (
                        <div className="param-group">
                          <label>Password</label>
                          <input 
                            type="password"
                            value={extraParams.password || ''}
                            onChange={(e) => setExtraParams({...extraParams, password: e.target.value})}
                            placeholder="Enter password"
                            className="param-input"
                          />
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Modal Footer */}
              <div className="operation-modal-footer">
                <motion.button
                  className={`btn-process modal-process-btn ${isProcessing ? 'processing' : ''}`}
                  onClick={processFiles}
                  disabled={isProcessing || files.length === 0}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  style={{ 
                    background: isProcessing ? '#333' : selectedOperation.color,
                  }}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 size={20} className="spin" />
                      Processing... {progress}%
                    </>
                  ) : (
                    <>
                      <Zap size={20} />
                      PROCESS {files.length > 0 ? `${files.length} FILE${files.length > 1 ? 'S' : ''}` : 'FILES'}
                    </>
                  )}
                </motion.button>

                {/* Progress Bar */}
                <AnimatePresence>
                  {isProcessing && (
                    <motion.div 
                      className="progress-bar modal-progress"
                      initial={{ opacity: 0, scaleX: 0 }}
                      animate={{ opacity: 1, scaleX: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <motion.div 
                        className="progress-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        style={{ background: selectedOperation.color }}
                      />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-brand">
            <span className="logo-text">pdfmaster</span>
            <p>Professional PDF tools for everyone</p>
          </div>
          <div className="footer-links">
            <a href="#tools">Tools</a>
            <a href="#features">Features</a>
            <a href="https://github.com/Rhushya/PDFTOOLS" target="_blank" rel="noopener noreferrer">GitHub</a>
          </div>
          <div className="footer-social">
            <a href="https://github.com/Rhushya/PDFTOOLS" target="_blank" rel="noopener noreferrer">
              <Github size={20} />
            </a>
            <a href="#"><Twitter size={20} /></a>
            <a href="#"><Linkedin size={20} /></a>
            <a href="#"><Mail size={20} /></a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2026 PDFMaster. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
