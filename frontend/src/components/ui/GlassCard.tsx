import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

interface GlassCardProps extends HTMLMotionProps<'div'> {
  children: React.ReactNode;
  className?: string;
  gradientBorder?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', gradientBorder = false, ...props }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      whileHover={{ scale: 1.01 }}
      className={`relative overflow-hidden rounded-2xl glass-panel ${className}`}
      {...props}
    >
      {gradientBorder && (
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 pointer-events-none rounded-2xl" style={{ padding: '1px', mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)', maskComposite: 'exclude' }} />
      )}
      <div className="relative z-10 p-6 h-full">
        {children}
      </div>
    </motion.div>
  );
};
