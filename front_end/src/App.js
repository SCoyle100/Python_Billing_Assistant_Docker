import React, { useState } from "react";
import axios from "axios";


const App = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [downloadLink, setDownloadLink] = useState("");

  // Handle file input change
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    console.log("Selected file:", selectedFile);
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setMessage("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    console.log("FormData contents:", formData.get("file"));

    try {
      setMessage("Uploading and converting...");
      setDownloadLink("");
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/`, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
      setMessage("Conversion successful!");
      setDownloadLink(response.data); // Assuming the backend sends back the download URL
    } catch (error) {
      console.error(error);
      setMessage("An error occurred during the upload or conversion.");
    }
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif", padding: "20px" }}>
      <h1>PDF to DOCX Converter</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          style={{ display: "block", marginBottom: "10px" }}
        />
        <button type="submit">Convert</button>
      </form>
      {message && <p>{message}</p>}
      {downloadLink && (
        <a href={downloadLink} download style={{ color: "blue" }}>
          Download Converted File
        </a>
      )}
    </div>
  );
};

export default App;

