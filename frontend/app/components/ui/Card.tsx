import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'bordered';
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  variant = 'default'
}) => {
  const baseClasses = 'rounded-lg p-6 transition-all duration-200';
  
  const variants = {
    default: 'bg-slate-800/50 backdrop-blur-sm border border-slate-700/50',
    elevated: 'bg-slate-800/60 backdrop-blur-sm border border-slate-600/50 shadow-xl hover:shadow-2xl',
    bordered: 'bg-slate-800/30 backdrop-blur-sm border-2 border-amber-500/30 hover:border-amber-500/50'
  };
  
  const classes = `${baseClasses} ${variants[variant]} ${className}`;
  
  return (
    <div className={classes}>
      {children}
    </div>
  );
}; 