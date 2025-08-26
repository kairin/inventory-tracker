# 📦 Inventory Tracker with OCR Image Verification

A Terminal User Interface (TUI) inventory management system that combines barcode scanning with Docling-powered OCR image verification for accurate inventory tracking.

## 🚀 Features

- **Barcode Scanning**: Add/remove items by scanning or typing barcodes
- **OCR Image Processing**: Use Docling to extract text and barcodes from product images  
- **Image Verification**: Verify scanned barcodes against product images
- **Auto-Detection**: Automatically detect product information (brand, color, type) from images
- **Smart Image Tracking**: Prevents reprocessing unchanged images using SHA-256 file hashing
- **Batch Processing**: Auto-process entire `/images` directory with cache optimization
- **Processing Cache**: Persistent cache system to avoid redundant OCR operations
- **Real-time Stats**: Track total items, unique products, verification status, and processing stats
- **Data Persistence**: Automatic saving to JSON file
- **Terminal UI**: Modern TUI interface with keyboard shortcuts

## 📋 Pre-loaded Inventory

The system comes pre-loaded with your scanned Epson 03C ink cartridges:

| Barcode | Item | Quantity | Status |
|---------|------|----------|---------|
| 8885007027531 | Epson 03C Black Ink | 5 | ❌ Not verified |
| 8885007027555 | Epson 03C Cyan Ink | 1 | ❌ Not verified |
| 8885007027579 | Epson 03C Magenta Ink | 1 | ❌ Not verified |
| 8885007027593 | Epson 03C Yellow Ink | 1 | ❌ Not verified |

**Total: 8 items across 4 unique products**

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Quick Start

1. **Clone/Download the repository**
   ```bash
   git clone git@github.com:kairin/inventory-tracker.git
   cd inventory-tracker
   ```

2. **Run the installation script**
   ```bash
   python3 run.py
   ```
   This will automatically install dependencies and start the app.

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 inventory_tracker.py
```

## 💻 Usage

### Basic Operations

#### Barcode Scanning
1. Enter barcode in the "Enter barcode or scan..." field
2. Press **Enter** or click **Add Item** to add/increment quantity
3. Click **Remove Item** to decrement quantity

#### Image Processing  
1. Place your product images in the `images/` directory
2. Enter image path in the "Enter image path..." field
3. Click **Process Image** to extract barcodes and product info
4. The system will auto-detect and add items to inventory

#### Image Verification
1. Enter barcode in first field
2. Enter image path in second field  
3. Click **Verify Image** to check if barcode matches image
4. ✅/❌ status will update in the inventory table

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `s` | Save inventory |
| `r` | Reset inventory |
| `i` | Process image |
| `v` | Verify image |
| `a` | Auto-process images folder |
| `c` | Clear processing cache |

### File Structure

```
inventory-tracker/
├── inventory_tracker.py    # Main TUI application
├── image_processor.py      # Docling OCR processing
├── requirements.txt        # Python dependencies
├── run.py                 # Installation & startup script
├── example_usage.py        # Usage examples and demos
├── inventory.json         # Persistent inventory data
├── processed_images.json  # Image processing cache database
├── images/               # Directory for product images (your images go here)
└── README.md             # This documentation
```

## 🔧 Configuration

### Image Directory
By default, images are stored in the `images/` directory. You can:
- Drop images directly into this folder
- Reference images with relative paths: `images/product1.jpg`
- Use absolute paths: `/full/path/to/image.jpg`

### Supported Image Formats
- JPG/JPEG
- PNG  
- BMP
- TIFF
- GIF

### Data Storage
Inventory data is automatically saved to `inventory.json` with the following structure:

```json
{
  "8885007027531": {
    "name": "Epson 03C Black Ink",
    "quantity": 5,
    "description": "Black ink cartridge", 
    "verified": true,
    "ocr_data": { /* OCR results */ },
    "last_updated": "2024-01-15 14:30:22"
  }
}
```

## 🤖 OCR Features with Docling

### What Docling Extracts
- **Barcodes**: EAN-13, UPC-A, EAN-8 formats
- **Product Information**: Brand, model, color, type
- **Part Numbers**: Manufacturer part numbers
- **Text Content**: All readable text from images

### OCR Processing Flow
1. **Image Input**: Load image file
2. **Hash Check**: Calculate SHA-256 hash to check if already processed
3. **Cache Lookup**: Return cached results if image unchanged
4. **Docling Processing**: Extract text and structure (if not cached)
5. **Pattern Matching**: Find barcodes and product details
6. **OpenCV Enhancement**: Additional barcode detection
7. **Cache Storage**: Save results to prevent reprocessing
8. **Data Fusion**: Combine OCR results with inventory

### Verification Process
1. **Barcode Matching**: Check if scanned barcode appears in image
2. **Confidence Scoring**: Rate match accuracy
3. **Product Validation**: Cross-reference product details
4. **Status Update**: Mark items as verified ✅ or unverified ❌

## 🗄️ Image Tracking & Caching System

### Smart Processing Prevention
- **File Hashing**: SHA-256 hash calculated for each image
- **Change Detection**: Only processes images that have changed
- **Persistent Cache**: `processed_images.json` stores processing history
- **Automatic Skipping**: Cached results returned instantly for unchanged images

### Processing Database Structure
```json
{
  "/absolute/path/to/image.jpg": {
    "file_hash": "sha256_hash_here",
    "processed_at": "2024-01-15T14:30:22.123456",
    "file_size": 2048576,
    "filename": "image.jpg",
    "barcodes_found": ["8885007027531"],
    "product_info": {"brand": "Epson", "color": "black"},
    "success": true
  }
}
```

### Cache Management Features
- **Auto-Process Folder**: Process entire `/images` directory efficiently
- **Batch Optimization**: Skip already processed images automatically  
- **Cache Statistics**: Track processing counts, success rates, barcodes found
- **Manual Cache Control**: Clear cache for specific images or all images
- **Force Reprocessing**: Override cache when needed

### Performance Benefits
- **Instant Results**: Cached images return results in milliseconds
- **Reduced API Calls**: Avoid redundant Docling processing
- **Battery Saving**: Skip heavy OCR operations on unchanged files
- **Scalability**: Handle large image directories efficiently

## 🎯 Use Cases

### Warehouse Management
- Verify received shipments against photos
- Audit inventory with image documentation
- Track verification status of all items

### Retail Operations  
- Confirm product authenticity
- Update inventory from supplier photos
- Maintain visual records of products

### Personal Inventory
- Organize home/office supplies
- Photo-document valuable items
- Track quantities with visual verification

## 📊 Data Export & Backup

### Manual Backup
```bash
# Copy inventory file
cp inventory.json inventory_backup_$(date +%Y%m%d).json

# Save OCR results
python3 -c "
from image_processor import ImageProcessor
processor = ImageProcessor()
results = processor.batch_process_images('images/')
processor.save_processing_results(results, 'ocr_results.json')
"
```

### Automation
Add to your cron job for regular backups:
```bash
0 2 * * * cd /path/to/inventory && cp inventory.json backups/inventory_$(date +\%Y\%m\%d).json
```

## 🐛 Troubleshooting

### Common Issues

**"Failed to process image"**
- Check image file exists and is readable
- Ensure image is in supported format
- Verify Docling installation: `pip show docling`

**"No barcodes detected"**  
- Image quality might be poor
- Try different angles/lighting
- Check if barcode is clearly visible and not obstructed

**"Import error: image_processor"**
- Run from correct directory
- Ensure all dependencies installed: `pip install -r requirements.txt`

**"Permission denied"**
- Make scripts executable: `chmod +x *.py`
- Check file/directory permissions

### Debug Mode
Enable verbose logging by modifying `image_processor.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Updates & Migration

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Data Migration
The system automatically handles data migration. Existing `inventory.json` files will be updated with new fields like `verified` and `ocr_data`.

## 📝 Development

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

### Testing
```bash
# Test image processing
python3 -c "
from image_processor import ImageProcessor
processor = ImageProcessor()
result = processor.process_image('path/to/test/image.jpg')
print(result)
"
```

### API Documentation
See `image_processor.py` for detailed API documentation and method signatures.

## 📄 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review the code documentation
3. Create an issue in the repository

---

**Happy inventory tracking! 📦✨**