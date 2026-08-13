import React from 'react';

interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
}

export default function Button({ onClick, children }: ButtonProps) {
  return (
    <button onClick={onClick} style={{ padding: '8px 16px', borderRadius: 4, background: '#0070f3', color: '#fff', border: 'none' }}>
      {children}
    </button>
  );
}
