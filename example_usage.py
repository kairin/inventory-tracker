#!/usr/bin/env python3

"""
Example usage scripts for the Inventory Tracker with OCR
This demonstrates how to use the ImageProcessor independently
"""

from image_processor import ImageProcessor
import json
import os
from pathlib import Path

def example_single_image_processing():
    """Example: Process a single image and extract information."""
    print("=== Single Image Processing Example ===")
    
    processor = ImageProcessor()
    
    # Example image path - replace with your actual image
    image_path = "images/ink_cartridge.jpg"
    
    if not os.path.exists(image_path):
        print(f"⚠️  Example image not found: {image_path}")
        print("📁 Place your product images in the 'images/' directory")
        return
    
    print(f"🔍 Processing image: {image_path}")
    result = processor.process_image(image_path)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print("✅ Processing completed!")
    print(f"📄 Extracted text preview: {result['text'][:200]}...")
    print(f"🏷️  Detected barcodes: {result['barcodes']}")
    print(f"📦 Product info: {result['product_info']}")
    
    return result

def example_barcode_verification():
    """Example: Verify a scanned barcode against an image."""
    print("\n=== Barcode Verification Example ===")
    
    processor = ImageProcessor()
    
    # Example data - replace with your actual values
    scanned_barcode = "8885007027531"  # Your scanned barcode
    image_path = "images/black_ink.jpg"  # Image of the product
    
    if not os.path.exists(image_path):
        print(f"⚠️  Example image not found: {image_path}")
        return
    
    print(f"🔍 Verifying barcode {scanned_barcode} against {image_path}")
    verification = processor.verify_barcode_match(scanned_barcode, image_path)
    
    if "error" in verification:
        print(f"❌ Error: {verification['error']}")
        return
    
    if verification["matches"]:
        print("✅ Barcode matches the image!")
        print(f"🎯 Confidence: {verification['confidence']}")
    else:
        print("❌ Barcode does not match the image")
        print(f"🔍 Found barcodes: {verification['detected_barcodes']}")
    
    print(f"📦 Product details: {verification['product_info']}")
    
    return verification

def example_batch_processing():
    """Example: Process all images in a directory."""
    print("\n=== Batch Processing Example ===")
    
    processor = ImageProcessor()
    images_dir = "images"
    
    if not os.path.exists(images_dir):
        print(f"📁 Creating images directory: {images_dir}")
        os.makedirs(images_dir)
        print("📷 Add your product images to this directory and run again")
        return
    
    print(f"📁 Processing all images in: {images_dir}")
    results = processor.batch_process_images(images_dir)
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    if not results:
        print("📷 No images found in directory")
        print("💡 Add .jpg, .png, .bmp, .tiff, or .gif files to process")
        return
    
    print(f"✅ Processed {len(results)} images")
    
    # Summary of results
    total_barcodes = 0
    verified_items = 0
    
    for filename, result in results.items():
        if "error" not in result:
            barcodes = len(result.get("barcodes", []))
            total_barcodes += barcodes
            if barcodes > 0:
                verified_items += 1
            print(f"📷 {filename}: {barcodes} barcode(s) found")
    
    print(f"📊 Summary: {total_barcodes} barcodes found across {verified_items} images")
    
    # Save results
    output_file = "batch_processing_results.json"
    if processor.save_processing_results(results, output_file):
        print(f"💾 Results saved to: {output_file}")
    
    return results

def example_create_sample_inventory():
    """Example: Create a sample inventory from your pre-scanned items."""
    print("\n=== Sample Inventory Creation ===")
    
    sample_inventory = {
        "8885007027531": {
            "name": "Epson 03C Black Ink",
            "quantity": 5,
            "description": "Black ink cartridge",
            "verified": False,
            "ocr_data": None,
            "last_updated": "2024-01-15 10:00:00"
        },
        "8885007027555": {
            "name": "Epson 03C Cyan Ink", 
            "quantity": 1,
            "description": "Cyan ink cartridge",
            "verified": False,
            "ocr_data": None,
            "last_updated": "2024-01-15 10:00:00"
        },
        "8885007027579": {
            "name": "Epson 03C Magenta Ink",
            "quantity": 1, 
            "description": "Magenta ink cartridge",
            "verified": False,
            "ocr_data": None,
            "last_updated": "2024-01-15 10:00:00"
        },
        "8885007027593": {
            "name": "Epson 03C Yellow Ink",
            "quantity": 1,
            "description": "Yellow ink cartridge", 
            "verified": False,
            "ocr_data": None,
            "last_updated": "2024-01-15 10:00:00"
        }
    }
    
    # Save to inventory.json
    with open("inventory.json", "w") as f:
        json.dump(sample_inventory, f, indent=2)
    
    print("✅ Sample inventory created!")
    print("📄 File: inventory.json")
    print(f"📦 Items: 4 unique products, 8 total items")
    print("🚀 Run 'python3 inventory_tracker.py' to start the TUI")

def main():
    """Run all examples."""
    print("🎯 Inventory Tracker - OCR Examples\n")
    
    # Create images directory if it doesn't exist
    os.makedirs("images", exist_ok=True)
    
    # Run examples
    example_create_sample_inventory()
    
    # Check if we have images to work with
    images_dir = Path("images")
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
    
    if image_files:
        print(f"\n📷 Found {len(image_files)} image(s) in images/ directory")
        example_single_image_processing()
        example_barcode_verification() 
        example_batch_processing()
    else:
        print("\n💡 To test OCR features:")
        print("   1. Add product images to the 'images/' directory")
        print("   2. Run this script again")
        print("   3. Or start the TUI: python3 inventory_tracker.py")
    
    print("\n🎉 Examples completed!")
    print("📖 See README.md for more detailed usage instructions")

if __name__ == "__main__":
    main()