# 📦 Inventory Tracker

> **Simple inventory management with barcode scanning and image verification**

A user-friendly Terminal User Interface (TUI) that helps you track inventory using barcode scanning and image processing. Perfect for small businesses, warehouses, or personal inventory management.

## ✨ What This Does

🔍 **Scan or type barcodes** to add items to your inventory  
📸 **Take photos** of products and automatically extract barcodes and product info  
✅ **Verify items** by checking if barcodes match product images  
📊 **Track quantities** and see real-time statistics  
💾 **Auto-save** everything to keep your data safe

## 🎯 Perfect For

- **New employees/interns** - Easy to learn and use
- **Small warehouses** - Track incoming/outgoing inventory  
- **Retail shops** - Verify products match their barcodes
- **Home/office** - Organize supplies and equipment

## 📋 Pre-loaded Inventory

The system comes pre-loaded with your scanned Epson 03C ink cartridges:

| Barcode | Item | Quantity | Status |
|---------|------|----------|---------|
| 8885007027531 | Epson 03C Black Ink | 5 | ❌ Not verified |
| 8885007027555 | Epson 03C Cyan Ink | 1 | ❌ Not verified |
| 8885007027579 | Epson 03C Magenta Ink | 1 | ❌ Not verified |
| 8885007027593 | Epson 03C Yellow Ink | 1 | ❌ Not verified |

**Total: 8 items across 4 unique products**

## 🚀 Quick Start Guide

### Step 1: Get the Code
```bash
git clone https://github.com/kairin/inventory-tracker.git
cd inventory-tracker
```

### Step 2: Run the App
```bash
python3 run.py
```
**That's it!** The script will install everything you need and start the app.

> 💡 **For your intern**: Just run `python3 run.py` - it handles all the setup automatically!

### Alternative: Manual Setup
If the automatic setup doesn't work:
```bash
pip install -r requirements.txt
python3 inventory_tracker.py
```

### What You Need
- Python 3.8 or newer
- Internet connection (for installing dependencies)

## 📱 How to Use (Step-by-Step)

### For Your First Time

1. **Start the app**: Run `python3 run.py`
2. **You'll see a screen with**:
   - Input field for barcodes
   - Buttons for Add/Remove items
   - Table showing your current inventory
   - Stats at the bottom

### Adding Items (3 Ways)

#### Method 1: Type/Scan Barcodes 📝
1. Type a barcode in the top input field
2. Press **Enter** or click **"Add Item"**
3. Watch your inventory table update automatically!

#### Method 2: Process Product Photos 📸
1. Put your product photos in the `images/` folder
2. Type the image filename (like `product1.jpg`) in the second input field
3. Click **"Process Image"**
4. The app finds barcodes in the photo and adds them automatically!

#### Method 3: Verify Items ✅
1. Type a barcode in the first field
2. Type an image filename in the second field
3. Click **"Verify Image"** 
4. The app checks if the barcode matches what's in the photo

### Quick Keys (Shortcuts)

Press these keys anywhere in the app:
- **`q`** = Quit and save
- **`s`** = Save your work
- **`a`** = Process ALL photos in images/ folder
- **`r`** = Reset inventory (careful!)

> 💡 **Tip for your intern**: Start with Method 1 (typing barcodes) to get comfortable, then try the photo features!

## 📁 Understanding the Files

**Main files to know:**
- **`run.py`** - Start here! Runs everything
- **`inventory_tracker.py`** - The main app with the interface
- **`images/`** folder - Put your product photos here
- **`inventory.json`** - Your inventory data (auto-created)

**Other files (you usually don't need to touch):**
- `image_processor.py` - Handles photo processing
- `requirements.txt` - List of needed software
- `example_usage.py` - Code examples
- `processed_images.json` - Keeps track of processed photos

## ⚙️ Simple Settings

### Where to Put Photos
- Drop photos in the **`images/`** folder
- Supported formats: JPG, PNG, BMP, TIFF, GIF
- File names can be anything: `product1.jpg`, `ink_cartridge.png`, etc.

### Your Data is Saved Automatically
- Everything saves to `inventory.json`
- No need to worry about losing your work
- The file updates every time you make changes

## 🔧 What Happens Behind the Scenes

**When you process a photo, the app:**
1. Reads the image file
2. Extracts text and barcodes using AI (Docling)
3. Finds product information (brand, model, color)
4. Adds items to your inventory automatically
5. Saves everything so it doesn't re-process the same photo

**Smart features:**
- ⚡ **Fast processing** - Already processed photos load instantly
- 🧠 **Remembers photos** - Won't waste time re-processing unchanged images
- 📊 **Tracks everything** - Keeps stats on success rates and found items

## 💾 Backing Up Your Data

### Quick Backup
```bash
# Make a backup copy of your inventory
cp inventory.json backup_inventory.json
```

### Daily Backup (Advanced)
Add this to your system's scheduled tasks to backup daily:
```bash
cp inventory.json backups/inventory_$(date +%Y%m%d).json
```

## 🆘 Help! Something's Not Working

### "App won't start"
1. **Check Python version**: Run `python3 --version` (need 3.8+)
2. **Try manual setup**: Run `pip install -r requirements.txt` then `python3 inventory_tracker.py`
3. **Check you're in the right folder**: Make sure you're in the `inventory-tracker` directory

### "Can't process images"
1. **Check the image exists**: Make sure your photo is in the `images/` folder
2. **Try a different photo**: Some images work better than others
3. **Check image format**: Use JPG, PNG, or other common formats

### "No barcodes found in photo"
1. **Make sure barcode is clear**: Not blurry, good lighting
2. **Try a closer photo**: Barcode should be visible and straight
3. **Check if it's a supported barcode type**: Works with most common barcodes

### "Permission errors"
```bash
chmod +x *.py  # Makes files executable
```

### Still stuck?
1. Try restarting the app: `python3 run.py`
2. Check if all files are there (see file list above)
3. Create an issue on GitHub with your error message

## 📚 For Your Intern

### Learning Path
1. **Week 1**: Get comfortable with typing barcodes and watching the inventory update
2. **Week 2**: Try processing some product photos from the `images/` folder  
3. **Week 3**: Learn verification features and keyboard shortcuts
4. **Week 4**: Understand the data files and backup procedures

### Key Points to Remember
- **Always start with** `python3 run.py`
- **Data saves automatically** - no need to worry about losing work
- **Photos go in `images/` folder** - that's where the app looks for them
- **Press `q` to quit safely** - this saves your work properly

### Practice Tasks
1. Add 10 items by typing random barcodes
2. Take a photo of a product with a barcode and process it
3. Try the verification feature with a known barcode and photo
4. Use `s` key to save and `a` key to auto-process all images

---

**Questions? Create an issue on GitHub or ask your supervisor! 📦✨**