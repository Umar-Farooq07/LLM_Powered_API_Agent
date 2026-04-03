import React, { useState } from "react";
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/atom-one-dark.css';

function RagInterface() {
  // --- STATE ---
  const [apiKey, setApiKey] = useState("");           // Stores User's API Key
  const [file, setFile] = useState(null);
  const [docDetails, setDocDetails] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputtext, setinputtext] = useState("");
  const [code, setCode] = useState("");               // Code Editor Content
  const [output, setOutput] = useState("");           // Terminal Output
  const [isThinking, setIsThinking] = useState(false);

  // --- 1. UPLOAD HANDLER ---
  const handleUpload = async () => {
    if (!file) return;
    
    setDocDetails({ name: file.name, status: "Uploading...", size: (file.size / 1024).toFixed(2) + " KB" });
    
    const formData = new FormData();
    formData.append("pdf", file);

    try {
      const res = await fetch("https://llm-powered-api-agent-n7g7.onrender.com/upload", { method: "POST", body: formData });
      if (res.ok) {
        setDocDetails(prev => ({ ...prev, status: "✅ Indexed & Ready" }));
      } else {
        setDocDetails(prev => ({ ...prev, status: "❌ Upload Failed" }));
      }
    } catch (err) {
      setDocDetails(prev => ({ ...prev, status: "❌ Error: " + err.message }));
    }
  };

  // --- 2. CHAT HANDLER (SIMPLE & ROBUST) ---
  const handleSend = async () => {
    if (!inputtext.trim()) return;
    
    // User Message State
    const userMsg = { role: "user", text: inputtext };
    setMessages(prev => [...prev, userMsg]);
    setinputtext("");
    setIsThinking(true);

    try {
      // 1. Send Request
      const res = await fetch("https://llm-powered-api-agent-n7g7.onrender.com/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            text: userMsg.text,
            api_key: apiKey 
        }) 
      });

      const data = await res.json();
      
      // 2. Update Chat UI (The explanation text)
      setMessages(prev => [...prev, { role: "bot", text: data.answer }]);

      // 3. Update Code Editor (Directly from backend!)
      if (data.extracted_code) {
        // 🚀 FIX: Smart Append Logic
        setCode(prevCode => {
          // If the editor is empty, just put the new code in
          if (prevCode.trim() === "") {
            return data.extracted_code;
          }
          // If there is already code, add a divider and append the new code below it
          return prevCode + "\n\n# --- NEW CODE ADDED BY AI ---\n\n" + data.extracted_code;
        });
        
        console.log("✅ Code updated from backend");
      } else {
        console.log("ℹ️ No code returned by backend");
      }

    } catch (err) {
      console.error("Chat Error:", err);
      setMessages(prev => [...prev, { role: "bot", text: "Error connecting to server." }]);
    } finally {
      setIsThinking(false);
    }
  };

  // --- 3. RUN CODE HANDLER ---
  const runCode = async () => {
    setOutput("Running...");
    
    if (!apiKey) {
        console.warn("⚠️ No API Key provided. Code running without credentials.");
    }

    try {
      const res = await fetch("https://llm-powered-api-agent-n7g7.onrender.com/run-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            code: code, 
            api_key: apiKey || "" 
        })
      });

      const data = await res.json();
      setOutput(data.output || "No output returned.");
    } catch (err) {
      setOutput("❌ Execution Error: Is the server running?");
    }
  };

  // --- LAYOUT ---
  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "sans-serif", backgroundColor: "#1e1e1e", color: "white" }}>
      
      {/* --- LEFT COLUMN: SETTINGS & DOCS (20%) --- */}
      <div style={{ width: "20%", minWidth: "250px", borderRight: "1px solid #444", padding: "20px", display: "flex", flexDirection: "column", gap: "20px" }}>
        
        {/* API Key Input Section */}
        <div>
            <h3 style={{ color: "#d63384", marginTop: 0 }}>🔑 Configuration</h3>
            <div style={{ background: "#2d2d2d", padding: "15px", borderRadius: "8px" }}>
                <label style={{fontSize: "12px", color: "#aaa", marginBottom: "5px", display: "block"}}>API Token (HuggingFace/Other)</label>
                <input 
                    type="password" 
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="hf_..."
                    style={{ 
                        width: "100%", padding: "8px", background: "#1e1e1e", border: "1px solid #444", 
                        color: "white", borderRadius: "4px", boxSizing: "border-box" 
                    }} 
                />
            </div>
        </div>

        <h3 style={{ color: "#00bfa5", marginTop: "10px" }}>📄 Document</h3>
        
        {/* File Input */}
        <div style={{ background: "#2d2d2d", padding: "15px", borderRadius: "8px" }}>
          <input 
            type="file" 
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
            style={{ color: "#ccc", width: "100%", marginBottom: "10px" }} 
          />
          <button 
            onClick={handleUpload}
            style={{ width: "100%", padding: "8px", background: "#007bff", border: "none", color: "white", borderRadius: "4px", cursor: "pointer" }}
          >
            Upload PDF
          </button>
        </div>

        {/* Details Display */}
        {docDetails && (
          <div style={{ background: "#2d2d2d", padding: "15px", borderRadius: "8px", fontSize: "14px" }}>
            <p><strong>Name:</strong> {docDetails.name}</p>
            <p><strong>Size:</strong> {docDetails.size}</p>
            <p style={{ color: docDetails.status.includes("✅") ? "#4caf50" : "#ff5252" }}>
              {docDetails.status}
            </p>
          </div>
        )}
      </div>


      {/* --- MIDDLE COLUMN: CHAT (40%) --- */}
      <div style={{ width: "40%", borderRight: "1px solid #444", display: "flex", flexDirection: "column" }}>
        <div style={{ padding: "15px", borderBottom: "1px solid #444", background: "#252526" }}>
          <h3>💬 Chat Assistant</h3>
        </div>

        {/* Messages Area */}
        <div style={{ flex: 1, overflowY: "auto", padding: "20px", display: "flex", flexDirection: "column", gap: "15px", background: "#1e1e1e" }}>
          {messages.map((msg, idx) => (
            <div key={idx} style={{
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "85%",
              background: msg.role === "user" ? "#0e639c" : "#2d2d2d",
              padding: "12px",
              borderRadius: "8px",
              lineHeight: "1.5"
            }}>
              <strong>{msg.role === "user" ? "You" : "AI"}:</strong>
              <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                {msg.text}
              </ReactMarkdown>
            </div>
          ))}
          {isThinking && <p style={{ color: "#888", fontStyle: "italic", paddingLeft: "10px" }}>Generating response...</p>}
        </div>

        {/* Input Area */}
        <div style={{ padding: "15px", borderTop: "1px solid #444", display: "flex", gap: "10px", background: "#252526" }}>
          <input
            value={inputtext}
            onChange={(e) => setinputtext(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask..."
            style={{ flex: 1, padding: "12px", borderRadius: "4px", border: "none", background: "#3c3c3c", color: "white" }}
          />
          <button onClick={handleSend} style={{ padding: "0 20px", background: "#28a745", border: "none", color: "white", borderRadius: "4px", cursor: "pointer" }}>➤</button>
        </div>
      </div>


      {/* --- RIGHT COLUMN: CODE EDITOR (40%) --- */}
      <div style={{ width: "40%", display: "flex", flexDirection: "column", background: "#1e1e1e" }}>
        <div style={{ padding: "15px", borderBottom: "1px solid #444", background: "#252526", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3>🛠️ Code Editor</h3>
          <button onClick={runCode} style={{ padding: "5px 15px", background: "#d63384", border: "none", color: "white", borderRadius: "4px", cursor: "pointer" }}>
            ▶ Run Code
          </button>
        </div>

        {/* Code Input */}
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Code extraction will appear here..."
          style={{ flex: 2, background: "#1e1e1e", color: "#d4d4d4", padding: "15px", border: "none", fontFamily: "monospace", fontSize: "14px", resize: "none", outline: "none" }}
          spellCheck="false"
        />

        {/* Console Output */}
        <div style={{ flex: 1, borderTop: "1px solid #444", background: "black", padding: "15px", fontFamily: "monospace", color: "#0f0", overflowY: "auto" }}>
          <strong style={{ display: "block", marginBottom: "5px", color: "white" }}>Terminal Output:</strong>
          <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{output}</pre>
        </div>
      </div>

    </div>
  );
}

export default RagInterface;