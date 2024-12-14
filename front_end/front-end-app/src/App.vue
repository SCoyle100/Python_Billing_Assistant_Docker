<template>
  <div style="font-family: Arial, sans-serif; padding: 20px;">
    <h1>PDF to DOCX Converter</h1>
    <form @submit.prevent="handleSubmit" style="margin-bottom: 20px;">
      <input
        type="file"
        accept="application/pdf"
        @change="handleFileChange"
        style="display: block; margin-bottom: 10px;"
      />
      <button type="submit">Convert</button>
    </form>
    <p v-if="message">{{ message }}</p>
    <a v-if="downloadLink" :href="downloadLink" download style="color: blue;">
      Download Converted File
    </a>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      file: null,
      message: "",
      downloadLink: "",
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
    },
    async handleSubmit() {
      if (!this.file) {
        this.message = "Please select a file to upload.";
        return;
      }

      const formData = new FormData();
      formData.append("file", this.file);

      try {
        this.message = "Uploading and converting...";
        this.downloadLink = ""; // Reset the download link

        const response = await axios.post(`${process.env.VUE_APP_API_URL}/`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        console.log("Backend response:", response.data); // Debug response

        // Ensure we set the correct URL
        if (response.data.download_url) {
          this.message = "Conversion successful!";
          this.downloadLink = response.data.download_url;
        } else {
          this.message = "Conversion successful, but no download link returned.";
        }
      } catch (error) {
        console.error("Error during upload or conversion:", error);
        this.message = "An error occurred during the upload or conversion.";
      }
    },
  },
};
</script>

<style>
/* Add your custom styles here if needed */
</style>

