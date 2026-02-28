import React, { useState } from "react";

export default function PdfUploader() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
    } else {
      alert("Please select a valid PDF file");
    }
  };

  const handleUpload = async () => {
    if (!file) return alert("No file selected");

    const formData = new FormData();
    formData.append("pdf", file); 

    try {
      setUploading(true);

      const res = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      console.log("Server response:", data);
      alert("Upload successful!");
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <h2>Upload PDF</h2>

      <input
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
      />

      {file && <p>Selected: {file.name}</p>}

      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? "Uploading..." : "Upload PDF"}
      </button>
    </div>
  );
}
