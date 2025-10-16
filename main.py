"""
MISMO XML Anonymizer API
FastAPI application with Swagger UI for anonymizing MISMO XML documents
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response, JSONResponse
from typing import Optional, List
from pydantic import BaseModel
import logging
import os
import glob

from anonymizer import MISMOAnonymizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MISMO XML Anonymizer API",
    description="API for anonymizing personally identifiable information (PII) in MISMO XML documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize anonymizer
anonymizer = MISMOAnonymizer()


# Request models
class FolderRequest(BaseModel):
    folder_path: str


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MISMO XML Anonymizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "POST /anonymize": "Upload MISMO XML file for anonymization",
            "POST /anonymize/text": "Submit MISMO XML as text for anonymization",
            "POST /anonymize/folder": "Process all XML files in a folder"
        }
    }


@app.post(
    "/anonymize",
    response_class=Response,
    responses={
        200: {
            "description": "Anonymized XML document",
            "content": {"application/xml": {}}
        }
    },
    summary="Anonymize MISMO XML file",
    description="Upload a MISMO XML file and receive an anonymized version with PII replaced"
)
async def anonymize_xml_file(file: UploadFile = File(..., description="MISMO XML file to anonymize")):
    """
    Anonymize a MISMO XML file

    - **file**: Upload XML file (must be valid XML)

    Returns anonymized XML with PII replaced:
    - Names replaced with Person1, Person2, etc.
    - SSNs replaced with fake SSN format
    - Addresses anonymized
    - Phone numbers and emails replaced
    - Financial data anonymized
    """
    try:
        # Validate file type
        if not file.filename.endswith('.xml'):
            raise HTTPException(
                status_code=400,
                detail="File must be an XML file"
            )

        # Read file content
        content = await file.read()
        xml_content = content.decode('utf-8')

        logger.info(f"Processing file: {file.filename}")

        # Anonymize XML
        anonymized_xml = anonymizer.anonymize_xml(xml_content)

        logger.info(f"Successfully anonymized file: {file.filename}")

        # Return anonymized XML
        return Response(
            content=anonymized_xml,
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename=anonymized_{file.filename}"
            }
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing XML: {str(e)}")


@app.post(
    "/anonymize/text",
    response_class=Response,
    responses={
        200: {
            "description": "Anonymized XML document",
            "content": {"application/xml": {}}
        }
    },
    summary="Anonymize MISMO XML text",
    description="Submit MISMO XML as text and receive an anonymized version"
)
async def anonymize_xml_text(xml_text: str):
    """
    Anonymize MISMO XML provided as text

    - **xml_text**: XML content as string

    Returns anonymized XML with PII replaced
    """
    try:
        logger.info("Processing XML text")

        # Anonymize XML
        anonymized_xml = anonymizer.anonymize_xml(xml_text)

        logger.info("Successfully anonymized XML text")

        # Return anonymized XML
        return Response(
            content=anonymized_xml,
            media_type="application/xml"
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing XML: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing XML: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post(
    "/anonymize/folder",
    response_class=JSONResponse,
    summary="Anonymize all XML files in a folder",
    description="Process all XML files in a specified folder and save anonymized versions in an 'anon' subfolder"
)
async def anonymize_folder(request: FolderRequest):
    """
    Anonymize all XML files in a folder

    - **folder_path**: Absolute path to folder containing XML files

    Processes all .xml files in the folder and creates anonymized versions in a subfolder named 'anon'.
    Returns a summary of processed files.
    """
    try:
        folder_path = request.folder_path

        # Validate folder exists
        if not os.path.exists(folder_path):
            raise HTTPException(
                status_code=400,
                detail=f"Folder does not exist: {folder_path}"
            )

        if not os.path.isdir(folder_path):
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {folder_path}"
            )

        # Find all XML files
        xml_pattern = os.path.join(folder_path, "*.xml")
        xml_files = glob.glob(xml_pattern)

        if not xml_files:
            return {
                "status": "success",
                "message": "No XML files found in folder",
                "processed": 0,
                "files": []
            }

        # Create anon subfolder
        anon_folder = os.path.join(folder_path, "anon")
        os.makedirs(anon_folder, exist_ok=True)

        logger.info(f"Processing {len(xml_files)} XML files from {folder_path}")

        processed_files = []
        failed_files = []

        # Process each XML file
        for xml_file in xml_files:
            try:
                filename = os.path.basename(xml_file)

                # Skip files that are in the anon subfolder
                if os.path.dirname(xml_file) == anon_folder:
                    continue

                logger.info(f"Processing: {filename}")

                # Read XML file
                with open(xml_file, 'r', encoding='utf-8') as f:
                    xml_content = f.read()

                # Anonymize XML
                anonymized_xml = anonymizer.anonymize_xml(xml_content)

                # Save to anon folder
                output_file = os.path.join(anon_folder, filename)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(anonymized_xml)

                processed_files.append({
                    "original": filename,
                    "anonymized": f"anon/{filename}"
                })

                logger.info(f"Successfully anonymized: {filename}")

            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                failed_files.append({
                    "file": filename,
                    "error": str(e)
                })

        return {
            "status": "success",
            "message": f"Processed {len(processed_files)} files successfully",
            "folder": folder_path,
            "output_folder": anon_folder,
            "processed": len(processed_files),
            "failed": len(failed_files),
            "files": processed_files,
            "errors": failed_files if failed_files else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing folder: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
