import os
import uuid
from fastapi import UploadFile
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

# Base directories for uploads
PDF_UPLOAD_DIR = "app/static/uploads/pdfs"
PHOTO_UPLOAD_DIR = "app/static/uploads/photos"

def ensure_upload_dirs():
    """Ensure upload directories exist"""
    os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)
    os.makedirs(PHOTO_UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile, directory: str) -> str:
    """Save an uploaded file to the specified directory and return the file path"""
    ensure_upload_dirs()
    
    # Generate a unique filename
    filename = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = os.path.join(directory, filename)
    
    # Write the file
    with open(file_path, "wb") as buffer:
        content = await upload_file.read()
        buffer.write(content)
    
    return file_path

async def save_pdf_file(upload_file: UploadFile) -> str:
    """Save an uploaded PDF file and return the file path"""
    return await save_upload_file(upload_file, PDF_UPLOAD_DIR)

async def save_photo_file(upload_file: UploadFile) -> str:
    """Save an uploaded photo file and return the file path"""
    return await save_upload_file(upload_file, PHOTO_UPLOAD_DIR)

def generate_inspection_pdf(inspection_data, photos_data):
    """Generate a PDF with inspection data and photos"""
    # Create a unique filename for the PDF
    filename = f"inspection_{uuid.uuid4()}.pdf"
    file_path = os.path.join(PDF_UPLOAD_DIR, filename)
    
    # Ensure directory exists
    ensure_upload_dirs()
    
    # Create the PDF document
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add inspection details
    elements.append(Paragraph(f"工程抽查表", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"分項工程名稱: {inspection_data.subproject_name}", styles['Normal']))
    elements.append(Paragraph(f"抽查表名稱: {inspection_data.inspection_form_name}", styles['Normal']))
    elements.append(Paragraph(f"檢查日期: {inspection_data.inspection_date}", styles['Normal']))
    elements.append(Paragraph(f"檢查位置: {inspection_data.location}", styles['Normal']))
    elements.append(Paragraph(f"抽查時機: {inspection_data.timing}", styles['Normal']))
    elements.append(Paragraph(f"抽查結果: {inspection_data.result}", styles['Normal']))
    
    if inspection_data.remark:
        elements.append(Paragraph(f"備註: {inspection_data.remark}", styles['Normal']))
    
    elements.append(Spacer(1, 24))
    
    # Add photos if available
    if photos_data:
        elements.append(Paragraph("現場照片", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        for photo in photos_data:
            if os.path.exists(photo.photo_path):
                img = RLImage(photo.photo_path, width=400, height=300)
                elements.append(img)
                elements.append(Paragraph(f"說明: {photo.caption if photo.caption else '無'}", styles['Normal']))
                elements.append(Paragraph(f"拍攝日期: {photo.capture_date}", styles['Normal']))
                elements.append(Spacer(1, 12))
    
    # Build the PDF
    doc.build(elements)
    
    return file_path
