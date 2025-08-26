#!/usr/bin/env python3

import os
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
import tempfile
import json
from datetime import datetime

class ImageProcessor:
    """Handles OCR and image processing for inventory items using Docling."""
    
    def __init__(self):
        self.converter = DocumentConverter()
        self.barcode_patterns = [
            r'\b\d{13}\b',  # EAN-13 barcodes
            r'\b\d{12}\b',  # UPC-A barcodes
            r'\b\d{8}\b',   # EAN-8 barcodes
        ]
        self.processed_images_file = "processed_images.json"
        self.processed_images = self._load_processed_images()
        
    def _load_processed_images(self) -> Dict[str, Dict]:
        """Load the processed images database."""
        if os.path.exists(self.processed_images_file):
            try:
                with open(self.processed_images_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_processed_images(self) -> None:
        """Save the processed images database."""
        try:
            with open(self.processed_images_file, 'w') as f:
                json.dump(self.processed_images, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save processed images database: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception as e:
            return f"error_{str(e)}"
    
    def _is_image_processed(self, image_path: str) -> bool:
        """Check if image has already been processed."""
        abs_path = os.path.abspath(image_path)
        file_hash = self._calculate_file_hash(image_path)
        
        # Check if we have this image in our database
        if abs_path in self.processed_images:
            stored_info = self.processed_images[abs_path]
            stored_hash = stored_info.get("file_hash", "")
            
            # If hash matches, image hasn't changed
            if stored_hash == file_hash:
                return True
        
        return False
    
    def _mark_image_processed(self, image_path: str, processing_result: Dict) -> None:
        """Mark image as processed and store results."""
        abs_path = os.path.abspath(image_path)
        file_hash = self._calculate_file_hash(image_path)
        
        self.processed_images[abs_path] = {
            "file_hash": file_hash,
            "processed_at": datetime.now().isoformat(),
            "file_size": os.path.getsize(image_path),
            "filename": os.path.basename(image_path),
            "barcodes_found": processing_result.get("barcodes", []),
            "product_info": processing_result.get("product_info", {}),
            "success": processing_result.get("success", False)
        }
        
        self._save_processed_images()
    
    def get_cached_result(self, image_path: str) -> Optional[Dict]:
        """Get cached processing result for an image."""
        abs_path = os.path.abspath(image_path)
        if abs_path in self.processed_images:
            cached_info = self.processed_images[abs_path]
            return {
                "success": True,
                "text": "Cached result - full text not stored",
                "barcodes": cached_info.get("barcodes_found", []),
                "product_info": cached_info.get("product_info", {}),
                "metadata": {
                    "filename": cached_info.get("filename", ""),
                    "file_size": cached_info.get("file_size", 0),
                    "cached": True
                },
                "processed_at": cached_info.get("processed_at", ""),
                "from_cache": True
            }
        return None

    def process_image(self, image_path: str, force_reprocess: bool = False) -> Dict[str, any]:
        """Process an image and extract text and barcode information."""
        try:
            if not os.path.exists(image_path):
                return {"error": f"Image not found: {image_path}"}
            
            # Check if already processed (unless forced)
            if not force_reprocess and self._is_image_processed(image_path):
                cached_result = self.get_cached_result(image_path)
                if cached_result:
                    return cached_result
            
            # Convert image using Docling
            result = self.converter.convert(image_path)
            
            # Extract text content
            extracted_text = result.document.export_to_markdown()
            
            # Process the image for additional barcode detection
            barcodes = self._detect_barcodes_opencv(image_path)
            
            # Extract product information
            product_info = self._extract_product_info(extracted_text)
            
            # Get image metadata
            image_metadata = self._get_image_metadata(image_path)
            
            processing_result = {
                "success": True,
                "text": extracted_text,
                "barcodes": barcodes,
                "product_info": product_info,
                "metadata": image_metadata,
                "processed_at": datetime.now().isoformat(),
                "from_cache": False
            }
            
            # Mark as processed
            self._mark_image_processed(image_path, processing_result)
            
            return processing_result
            
        except Exception as e:
            return {"error": f"Failed to process image: {str(e)}"}
    
    def _detect_barcodes_opencv(self, image_path: str) -> List[str]:
        """Detect barcodes using OpenCV and pattern matching."""
        barcodes = []
        
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return barcodes
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing for better OCR
            processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Use Docling for text extraction from processed image
            temp_path = tempfile.mktemp(suffix='.png')
            cv2.imwrite(temp_path, processed)
            
            try:
                result = self.converter.convert(temp_path)
                text = result.document.export_to_markdown()
                
                # Extract barcodes using regex patterns
                for pattern in self.barcode_patterns:
                    matches = re.findall(pattern, text)
                    barcodes.extend(matches)
                
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            print(f"Barcode detection error: {e}")
        
        return list(set(barcodes))  # Remove duplicates
    
    def _extract_product_info(self, text: str) -> Dict[str, str]:
        """Extract product information from OCR text."""
        product_info = {}
        
        # Common product information patterns
        patterns = {
            "brand": [
                r"(?i)(epson|hp|canon|brother|lexmark|xerox)\b",
                r"(?i)brand[:\s]+(\w+)",
            ],
            "model": [
                r"(?i)model[:\s]+([A-Z0-9\-]+)",
                r"(?i)(\d{2,3}[A-Z]{1,2})\b",  # Common ink model patterns
            ],
            "color": [
                r"(?i)(black|cyan|magenta|yellow|blue|red|green)\b",
                r"(?i)colou?r[:\s]+(\w+)",
            ],
            "type": [
                r"(?i)(ink|toner|cartridge|ribbon)\b",
                r"(?i)type[:\s]+(\w+)",
            ],
            "part_number": [
                r"(?i)part[:\s#]*([A-Z0-9\-]+)",
                r"(?i)p/?n[:\s#]*([A-Z0-9\-]+)",
            ]
        }
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text)
                if match:
                    product_info[key] = match.group(1).strip()
                    break
        
        return product_info
    
    def _get_image_metadata(self, image_path: str) -> Dict[str, any]:
        """Extract metadata from image file."""
        try:
            with Image.open(image_path) as img:
                metadata = {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode,
                    "file_size": os.path.getsize(image_path),
                    "filename": os.path.basename(image_path)
                }
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    if exif:
                        metadata["exif"] = {str(k): str(v) for k, v in exif.items()}
                
                return metadata
        except Exception as e:
            return {"error": f"Failed to extract metadata: {str(e)}"}
    
    def verify_barcode_match(self, scanned_barcode: str, image_path: str) -> Dict[str, any]:
        """Verify if a scanned barcode matches what's detected in the image."""
        try:
            result = self.process_image(image_path)
            
            if "error" in result:
                return result
            
            detected_barcodes = result.get("barcodes", [])
            
            verification_result = {
                "matches": scanned_barcode in detected_barcodes,
                "scanned_barcode": scanned_barcode,
                "detected_barcodes": detected_barcodes,
                "confidence": 1.0 if scanned_barcode in detected_barcodes else 0.0,
                "product_info": result.get("product_info", {}),
                "verification_time": datetime.now().isoformat()
            }
            
            return verification_result
            
        except Exception as e:
            return {"error": f"Verification failed: {str(e)}"}
    
    def get_processing_stats(self) -> Dict[str, any]:
        """Get statistics about processed images."""
        total_processed = len(self.processed_images)
        successful_processing = sum(1 for info in self.processed_images.values() 
                                  if info.get("success", False))
        total_barcodes_found = sum(len(info.get("barcodes_found", [])) 
                                 for info in self.processed_images.values())
        
        return {
            "total_images_processed": total_processed,
            "successful_processing": successful_processing,
            "failed_processing": total_processed - successful_processing,
            "total_barcodes_found": total_barcodes_found,
            "last_processing_date": max([info.get("processed_at", "") 
                                       for info in self.processed_images.values()], 
                                      default="Never")
        }
    
    def clear_processed_cache(self, image_path: str = None) -> bool:
        """Clear processed image cache. If image_path is provided, clear only that image."""
        try:
            if image_path:
                abs_path = os.path.abspath(image_path)
                if abs_path in self.processed_images:
                    del self.processed_images[abs_path]
                    self._save_processed_images()
                    return True
                return False
            else:
                # Clear all cache
                self.processed_images = {}
                self._save_processed_images()
                return True
        except Exception:
            return False
    
    def list_processed_images(self) -> List[Dict[str, any]]:
        """Get list of all processed images with their info."""
        processed_list = []
        for path, info in self.processed_images.items():
            processed_list.append({
                "path": path,
                "filename": info.get("filename", os.path.basename(path)),
                "processed_at": info.get("processed_at", ""),
                "file_size": info.get("file_size", 0),
                "barcodes_found": info.get("barcodes_found", []),
                "success": info.get("success", False)
            })
        return processed_list

    def batch_process_images(self, image_directory: str, force_reprocess: bool = False) -> Dict[str, Dict[str, any]]:
        """Process all images in a directory."""
        results = {}
        
        if not os.path.exists(image_directory):
            return {"error": f"Directory not found: {image_directory}"}
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
        
        processed_count = 0
        skipped_count = 0
        
        for filename in os.listdir(image_directory):
            if Path(filename).suffix.lower() in image_extensions:
                image_path = os.path.join(image_directory, filename)
                
                # Check if already processed
                if not force_reprocess and self._is_image_processed(image_path):
                    results[filename] = self.get_cached_result(image_path)
                    skipped_count += 1
                else:
                    results[filename] = self.process_image(image_path, force_reprocess)
                    processed_count += 1
        
        # Add summary information
        results["_batch_summary"] = {
            "total_images": len([f for f in os.listdir(image_directory) 
                               if Path(f).suffix.lower() in image_extensions]),
            "newly_processed": processed_count,
            "from_cache": skipped_count,
            "force_reprocess": force_reprocess,
            "processed_at": datetime.now().isoformat()
        }
        
        return results
    
    def save_processing_results(self, results: Dict[str, any], output_file: str):
        """Save processing results to JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Failed to save results: {e}")
            return False

def main():
    """Example usage of ImageProcessor."""
    processor = ImageProcessor()
    
    # Example: Process a single image
    # result = processor.process_image("path/to/your/image.jpg")
    # print(json.dumps(result, indent=2))
    
    # Example: Verify barcode
    # verification = processor.verify_barcode_match("8885007027531", "path/to/image.jpg")
    # print(json.dumps(verification, indent=2))
    
    print("ImageProcessor initialized. Use the methods to process your images.")

if __name__ == "__main__":
    main()