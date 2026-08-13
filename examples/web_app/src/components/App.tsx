import React from 'react';
import Button from './Button';

export default function App() {
  return (
    <div style={{ padding: 24 }}>
      <h1>Welcome to .veda Example App</h1>
      <Button onClick={() => alert('VEDA is awesome!')}>Click Me</Button>
    </div>
  );
}
