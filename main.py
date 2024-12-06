import os
import logging
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime

import docx
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.export_pdf_job import ExportPDFJob
from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_params import ExportPDFParams
from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_target_format import ExportPDFTargetFormat
from adobe.pdfservices.operation.pdfjobs.result.export_pdf_result import ExportPDFResult
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

# Flask app setup
app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = "./uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Load environment variables
load_dotenv()

class PDFConverter:
    # Existing implementation
    pass

@app.route("/", methods=["POST"])
def upload_and_convert():
    # Check if a file is provided
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Secure the filename and save the file
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    # Convert the PDF to DOCX
    converter = PDFConverter()
    docx_path = converter.convert_pdf_to_docx(input_path)
    if docx_path:
        download_url = url_for("download_file", filename=os.path.basename(docx_path), _external=True)
        return jsonify({"download_url": download_url})
    else:
        return jsonify({"error": "Failed to convert PDF to DOCX"}), 500

@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)