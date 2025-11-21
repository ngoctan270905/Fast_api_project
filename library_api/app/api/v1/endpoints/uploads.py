from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session  # CORRECTED IMPORT
from app.services.book_service import BookService

router = APIRouter()

MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)

@router.post("/uploads/book-cover/{book_id}")
async def upload_book_cover(
    book_id: int, 
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session)  # Inject db session
):
    # Instantiate service inside the endpoint
    book_service = BookService(db)

    if not file.content_type in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Only JPEG, PNG, GIF, WEBP are allowed.",
        )

    # Sanitize filename to prevent directory traversal attacks
    file_extension = file.filename.split(".")[-1]
    safe_filename = f"book_{book_id}_cover.{file_extension}"
    file_path = MEDIA_DIR / safe_filename

    try:
        # Save file to disk
        with open(file_path, "wb") as f:
            while contents := await file.read(1024 * 1024):  # Read in 1MB chunks
                f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not upload file: {e}")
    finally:
        await file.close()

    # Update book record in the database
    try:
        updated_book = await book_service.update_book_cover_image_url(book_id, str(file_path))
    except HTTPException as e:
        # If book not found or other service-level error, re-raise
        raise e
    except Exception as e:
        # Catch any other unexpected errors during DB update
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not update book cover in database: {e}")

    return {
        "filename": safe_filename, 
        "path": str(file_path), 
        "book_id": updated_book.id,
        "message": "File uploaded and book cover URL updated successfully."
    }

@router.post("/uploads/multiple-book-covers/{book_id}")
async def upload_multiple_book_covers(book_id: int, files: List[UploadFile] = File(...)):
    uploaded_files_info = []
    for file in files:
        if not file.content_type in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image format for {file.filename}. Only JPEG, PNG, GIF, WEBP are allowed.",
            )
        
        file_extension = file.filename.split(".")[-1]
        safe_filename = f"book_{book_id}_additional_cover_{len(uploaded_files_info)}.{file_extension}"
        file_path = MEDIA_DIR / safe_filename

        try:
            with open(file_path, "wb") as f:
                while contents := await file.read(1024 * 1024):
                    f.write(contents)
            uploaded_files_info.append({"filename": safe_filename, "path": str(file_path)})
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not upload file {file.filename}")
        finally:
            await file.close()
    
    return {"uploaded_files": uploaded_files_info, "message": "Multiple files uploaded successfully. Database update pending."}
