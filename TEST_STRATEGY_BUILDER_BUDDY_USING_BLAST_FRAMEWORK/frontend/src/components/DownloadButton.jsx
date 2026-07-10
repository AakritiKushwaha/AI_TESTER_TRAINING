import React from 'react';
import './DownloadButton.css';

export default function DownloadButton({ docx, disabled }) {
  const handleDownload = () => {
    if (!docx?.docxBase64) return;
    const byteCharacters = atob(docx.docxBase64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = docx.docxFileName || 'strategy.docx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <button className="download-btn" onClick={handleDownload} disabled={disabled || !docx}>
      Download DOCX
    </button>
  );
}
