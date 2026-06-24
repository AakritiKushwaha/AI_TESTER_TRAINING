import React from 'react';
import './DocxPreview.css';

export default function DocxPreview({ docx }) {
  if (!docx?.content) return null;
  const dataUrl = `data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,${docx.content}`;
  return (
    <div className="docx-preview">
      <h3>DOCX Preview</h3>
      {/* Embed the DOCX file; most browsers will prompt download or show preview if supported */}
      <embed src={dataUrl} type="application/vnd.openxmlformats-officedocument.wordprocessingml.document" width="100%" height="500px" />
    </div>
  );
}
