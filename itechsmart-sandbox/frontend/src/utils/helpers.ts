import { format, formatDistanceToNow } from 'date-fns';

/**
 * Format bytes to human readable string
 */
export const formatBytes = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Format date to readable string
 */
export const formatDate = (date: string | Date): string => {
  return format(new Date(date), 'MMM dd, yyyy HH:mm:ss');
};

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: string | Date): string => {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
};

/**
 * Format duration in seconds to readable string
 */
export const formatDuration = (seconds: number): string => {
  if (seconds < 60) {
    return `${seconds}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }
};

/**
 * Get status color class
 */
export const getStatusColor = (status: string): string => {
  const statusColors: Record<string, string> = {
    running: 'badge-success',
    completed: 'badge-success',
    passed: 'badge-success',
    stopped: 'badge-warning',
    pending: 'badge-warning',
    creating: 'badge-info',
    error: 'badge-error',
    failed: 'badge-error',
    terminated: 'badge-secondary',
  };

  return statusColors[status.toLowerCase()] || 'badge-secondary';
};

/**
 * Get file extension from path
 */
export const getFileExtension = (path: string): string => {
  const parts = path.split('.');
  return parts.length > 1 ? parts[parts.length - 1] : '';
};

/**
 * Get language from file extension
 */
export const getLanguageFromExtension = (extension: string): string => {
  const languageMap: Record<string, string> = {
    js: 'javascript',
    jsx: 'javascript',
    ts: 'typescript',
    tsx: 'typescript',
    py: 'python',
    java: 'java',
    cpp: 'cpp',
    c: 'c',
    cs: 'csharp',
    go: 'go',
    rs: 'rust',
    rb: 'ruby',
    php: 'php',
    swift: 'swift',
    kt: 'kotlin',
    scala: 'scala',
    html: 'html',
    css: 'css',
    scss: 'scss',
    json: 'json',
    xml: 'xml',
    yaml: 'yaml',
    yml: 'yaml',
    md: 'markdown',
    sh: 'shell',
    bash: 'shell',
    sql: 'sql',
  };

  return languageMap[extension.toLowerCase()] || 'plaintext';
};

/**
 * Truncate string with ellipsis
 */
export const truncate = (str: string, length: number): string => {
  if (str.length <= length) return str;
  return str.substring(0, length) + '...';
};

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
};

/**
 * Download file from blob
 */
export const downloadFile = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};

/**
 * Parse error message from API response
 */
export const parseErrorMessage = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

/**
 * Generate random ID
 */
export const generateId = (): string => {
  return Math.random().toString(36).substring(2, 15);
};

/**
 * Debounce function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Format percentage
 */
export const formatPercent = (value: number, decimals: number = 1): string => {
  return `${value.toFixed(decimals)}%`;
};

/**
 * Calculate time remaining
 */
export const calculateTimeRemaining = (
  createdAt: string,
  ttlSeconds: number
): number => {
  const created = new Date(createdAt).getTime();
  const now = Date.now();
  const elapsed = (now - created) / 1000;
  return Math.max(0, ttlSeconds - elapsed);
};

/**
 * Check if sandbox is expired
 */
export const isSandboxExpired = (
  createdAt: string,
  ttlSeconds: number
): boolean => {
  return calculateTimeRemaining(createdAt, ttlSeconds) === 0;
};