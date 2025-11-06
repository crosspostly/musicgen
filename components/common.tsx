
import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className }) => (
  <div className={`bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-6 ${className}`}>
    {children}
  </div>
);

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  unit?: string;
  hint: string;
  valueLabel?: string;
}

export const Slider: React.FC<SliderProps> = ({ label, value, min, max, step, onChange, unit, hint, valueLabel }) => (
  <div className="space-y-2">
    <div className="flex justify-between items-center">
      <label className="font-medium text-gray-300">{label}</label>
      <span className="text-indigo-400 font-semibold">{valueLabel || value} {unit}</span>
    </div>
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={onChange}
      className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
    />
    <p className="text-xs text-gray-500">{hint}</p>
  </div>
);

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', className, ...props }) => {
  const baseClasses = 'px-4 py-2 rounded-md font-semibold flex items-center justify-center gap-2 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-500 focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500',
    secondary: 'bg-gray-700 text-gray-200 hover:bg-gray-600 focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-500 focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-red-500',
  };

  return (
    <button className={`${baseClasses} ${variantClasses[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
};

interface TooltipProps {
    children: React.ReactNode;
    text: string;
}

export const Tooltip: React.FC<TooltipProps> = ({ children, text }) => {
    return (
        <div className="relative group flex items-center">
            {children}
            <div className="absolute bottom-full mb-2 w-max max-w-xs p-2 text-sm bg-gray-900 text-white rounded-md scale-0 group-hover:scale-100 transition-transform origin-bottom">
                {text}
            </div>
        </div>
    );
};
