import React, { useState, useEffect } from 'react';
import './ThemeToggle.css';

export default function ThemeToggle() {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const saved = localStorage.getItem('theme') || 'light';
    setTheme(saved);
    document.body.dataset.theme = saved;
    document.documentElement.dataset.theme = saved;
  }, []);

  const toggle = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.body.dataset.theme = newTheme;
    document.documentElement.dataset.theme = newTheme;
  };

  return (
    <button className="theme-toggle-btn" onClick={toggle}>
      {theme === 'light' ? 'Switch to 🌙 Dark Mode' : 'Switch to ☀️ Light Mode'}
    </button>
  );
}
