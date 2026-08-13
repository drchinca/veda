import { useState, useEffect } from 'react';

export function useAuth() {
  const [user, setUser] = useState<string | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) setUser(savedUser);
  }, []);

  return { user, isLoggedIn: !!user };
}
