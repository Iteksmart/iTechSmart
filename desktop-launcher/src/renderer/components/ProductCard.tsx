import React, { useState } from 'react';
import { Play, Square, ExternalLink, Lock, Loader } from 'lucide-react';

interface ProductCardProps {
  product: any;
  status: string;
  license: any;
  onStatusChange: () => void;
}

function ProductCard({ product, status, license, onStatusChange }: ProductCardProps) {
  const [loading, setLoading] = useState(false);
  const [canAccess, setCanAccess] = useState(true);

  React.useEffect(() => {
    if (license) {
      window.electron.canAccessProduct(product.id).then(setCanAccess);
    }
  }, [license, product.id]);

  const handleStart = async () => {
    setLoading(true);
    try {
      await window.electron.startProduct(product.id);
      onStatusChange();
    } catch (error) {
      console.error('Failed to start product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await window.electron.stopProduct(product.id);
      onStatusChange();
    } catch (error) {
      console.error('Failed to stop product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpen = () => {
    window.electron.openProduct(product.id);
  };

  const isRunning = status === 'running';
  const isLocked = !canAccess;

  return (
    <div className={`bg-slate-800 rounded-lg border ${
      isLocked ? 'border-slate-700 opacity-60' : 'border-slate-700 hover:border-slate-600'
    } transition-all duration-200 overflow-hidden`}>
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <h3 className="font-semibold text-slate-100 mb-1">{product.name}</h3>
            <p className="text-sm text-slate-400 line-clamp-2">{product.description}</p>
          </div>
          {isLocked && (
            <Lock size={20} className="text-slate-500 ml-2" />
          )}
        </div>
        
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs px-2 py-1 bg-slate-700 text-slate-300 rounded">
            {product.category}
          </span>
          
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              isRunning ? 'bg-green-500 animate-pulse' : 'bg-slate-600'
            }`}></div>
            <span className="text-xs text-slate-400">
              {isRunning ? 'Running' : 'Stopped'}
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="p-4 flex gap-2">
        {isLocked ? (
          <button
            disabled
            className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-slate-700 text-slate-500 rounded-lg cursor-not-allowed"
          >
            <Lock size={16} />
            <span>Upgrade License</span>
          </button>
        ) : (
          <>
            {isRunning ? (
              <>
                <button
                  onClick={handleStop}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <Loader size={16} className="animate-spin" />
                  ) : (
                    <Square size={16} />
                  )}
                  <span>Stop</span>
                </button>
                <button
                  onClick={handleOpen}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                  title="Open in browser"
                >
                  <ExternalLink size={16} />
                </button>
              </>
            ) : (
              <button
                onClick={handleStart}
                disabled={loading}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <Loader size={16} className="animate-spin" />
                ) : (
                  <Play size={16} />
                )}
                <span>Start</span>
              </button>
            )}
          </>
        )}
      </div>

      {/* Ports Info */}
      {isRunning && !isLocked && (
        <div className="px-4 pb-4 text-xs text-slate-400">
          <div>Backend: localhost:{product.backendPort}</div>
          <div>Frontend: localhost:{product.frontendPort}</div>
        </div>
      )}
    </div>
  );
}

export default ProductCard;