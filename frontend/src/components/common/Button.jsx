export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  ...props 
}) {
  const baseStyles = 'font-medium rounded transition-all duration-200 focus-ring disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-black dark:bg-white text-white dark:text-black hover:opacity-80',
    secondary: 'border border-current hover:bg-light-hover dark:hover:bg-dark-hover',
    ghost: 'hover:bg-light-hover dark:hover:bg-dark-hover',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className} ${
        loading ? 'cursor-wait' : ''
      }`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4"
              fill="none"
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Loading...
        </span>
      ) : (
        children
      )}
    </button>
  );
}