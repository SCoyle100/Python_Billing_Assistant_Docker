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
    def __init__(self):
        self.word = None
        self.doc = None

    def convert_pdf_to_docx(self, input_path):
        try:
            with open(input_path, 'rb') as file:
                input_stream = file.read()

            load_dotenv()

            credentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
            )

            pdf_services = PDFServices(credentials=credentials)
            input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)
            export_pdf_params = ExportPDFParams(target_format=ExportPDFTargetFormat.DOCX)
            export_pdf_job = ExportPDFJob(input_asset=input_asset, export_pdf_params=export_pdf_params)
            location = pdf_services.submit(export_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, ExportPDFResult)
            result_asset = pdf_services_response.get_result().get_asset()
            stream_asset = pdf_services.get_content(result_asset)

            output_file_path = self.create_output_file_path(input_path)
            with open(output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())

            return output_file_path

        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f'Exception encountered while executing operation: {e}')
            return None
        

    def create_output_file_path(self, input_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.basename(input_path)
        file_name, _ = os.path.splitext(base_name)
        output_file_path = os.path.join(output_dir, f"{file_name}.docx")

        return output_file_path        

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