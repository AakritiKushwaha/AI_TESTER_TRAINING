import React from 'react';
import ThemeToggle from './ThemeToggle';
import './Header.css';

export default function Header({ onOpenSettings }) {
  return (
    <header className="app-header">
      <h1>TEST STRATEGY BUILDER</h1>
      <div className="header-actions">
        <ThemeToggle />
        <button className="settings-btn" onClick={onOpenSettings}>Settings</button>
      </div>
    </header>
  );
}
