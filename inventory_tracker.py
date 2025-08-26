#!/usr/bin/env python3

import json
import os
from datetime import datetime
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Button, DataTable, Static, Label
from textual.binding import Binding
from rich.text import Text
from image_processor import ImageProcessor

class InventoryTracker(App):
    """A TUI app for tracking inventory items using barcode scanning."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    .header {
        dock: top;
        height: 3;
        background: $primary;
        color: $text;
        content-align: center middle;
    }
    
    .scanner {
        height: 5;
        margin: 1;
        border: solid $primary;
    }
    
    .inventory {
        margin: 1;
        border: solid $accent;
    }
    
    .stats {
        height: 3;
        margin: 1;
        border: solid $success;
        background: $surface-lighten-1;
    }
    
    Input {
        margin: 1;
    }
    
    Button {
        margin: 1;
        min-width: 10;
    }
    
    DataTable {
        height: 1fr;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "save", "Save"),
        Binding("r", "reset", "Reset"),
        Binding("i", "process_image", "Process Image"),
        Binding("v", "verify_image", "Verify Image"),
        Binding("a", "auto_process_images", "Auto-Process Images"),
        Binding("c", "clear_cache", "Clear Cache"),
    ]
    
    def __init__(self):
        super().__init__()
        self.inventory_file = "inventory.json"
        self.inventory = {}
        self.image_processor = ImageProcessor()
        self.images_directory = "images"
        self.load_inventory()
        
        # Create images directory if it doesn't exist
        os.makedirs(self.images_directory, exist_ok=True)
        
        # Pre-populate with scanned items (from React code data)
        self.inventory = {
            "8885007027531": {
                "name": "Epson 03C Black Ink", 
                "quantity": 5, 
                "description": "Black ink cartridge",
                "verified": False,
                "ocr_data": None
            },
            "8885007027555": {
                "name": "Epson 03C Cyan Ink", 
                "quantity": 1, 
                "description": "Cyan ink cartridge",
                "verified": False,
                "ocr_data": None
            },
            "8885007027579": {
                "name": "Epson 03C Magenta Ink", 
                "quantity": 1, 
                "description": "Magenta ink cartridge",
                "verified": False,
                "ocr_data": None
            },
            "8885007027593": {
                "name": "Epson 03C Yellow Ink", 
                "quantity": 1, 
                "description": "Yellow ink cartridge",
                "verified": False,
                "ocr_data": None
            },
        }
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        
        with Container(classes="header"):
            yield Static("📦 Inventory Tracker - Barcode Scanner", id="title")
        
        with Container(classes="scanner"):
            yield Label("Scan Barcode or Process Image:")
            with Horizontal():
                yield Input(placeholder="Enter barcode or scan...", id="barcode_input")
                yield Button("Add Item", id="add_btn", variant="primary")
                yield Button("Remove Item", id="remove_btn", variant="error")
            with Horizontal():
                yield Input(placeholder="Enter image path...", id="image_input")
                yield Button("Process Image", id="process_img_btn", variant="success")
                yield Button("Verify Image", id="verify_img_btn", variant="warning")
            with Horizontal():
                yield Button("Auto-Process Images Folder", id="auto_process_btn", variant="primary")
                yield Button("Clear Processing Cache", id="clear_cache_btn", variant="error")
                yield Button("Show Processing Stats", id="show_stats_btn", variant="default")
        
        with Container(classes="stats"):
            yield Static("", id="stats")
        
        with Container(classes="inventory"):
            yield DataTable(id="inventory_table")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Set up the data table and initial display."""
        table = self.query_one("#inventory_table", DataTable)
        table.add_columns("Barcode", "Item Name", "Description", "Quantity", "Verified", "Last Updated")
        self.refresh_table()
        self.update_stats()
    
    def refresh_table(self) -> None:
        """Refresh the inventory table."""
        table = self.query_one("#inventory_table", DataTable)
        table.clear()
        
        for barcode, item in self.inventory.items():
            verified_status = "✅" if item.get("verified", False) else "❌"
            table.add_row(
                barcode,
                item["name"],
                item.get("description", ""),
                str(item["quantity"]),
                verified_status,
                item.get("last_updated", "")
            )
    
    def update_stats(self) -> None:
        """Update the statistics display."""
        total_items = sum(item["quantity"] for item in self.inventory.values())
        unique_items = len(self.inventory)
        
        stats_text = f"📊 Total Items: {total_items} | Unique Products: {unique_items} | Last Scan: {datetime.now().strftime('%H:%M:%S')}"
        self.query_one("#stats", Static).update(stats_text)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id in ["add_btn", "remove_btn"]:
            barcode_input = self.query_one("#barcode_input", Input)
            barcode = barcode_input.value.strip()
            
            if not barcode:
                self.notify("Please enter a barcode", severity="warning")
                return
            
            if event.button.id == "add_btn":
                self.add_item(barcode)
            elif event.button.id == "remove_btn":
                self.remove_item(barcode)
            
            barcode_input.value = ""
            barcode_input.focus()
            
        elif event.button.id == "process_img_btn":
            self.process_image_from_input()
            
        elif event.button.id == "verify_img_btn":
            self.verify_image_from_input()
            
        elif event.button.id == "auto_process_btn":
            self.auto_process_images_folder()
            
        elif event.button.id == "clear_cache_btn":
            self.clear_processing_cache()
            
        elif event.button.id == "show_stats_btn":
            self.show_processing_stats()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field."""
        if event.input.id == "barcode_input":
            barcode = event.input.value.strip()
            if barcode:
                self.add_item(barcode)
                event.input.value = ""
    
    def add_item(self, barcode: str) -> None:
        """Add an item to inventory."""
        if barcode in self.inventory:
            self.inventory[barcode]["quantity"] += 1
            self.inventory[barcode]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.notify(f"Updated {self.inventory[barcode]['name']} (Qty: {self.inventory[barcode]['quantity']})", severity="success")
        else:
            # For new items, prompt for name or use default
            item_name = f"Item-{barcode[-4:]}"  # Use last 4 digits as default name
            self.inventory[barcode] = {
                "name": item_name,
                "quantity": 1,
                "description": "New item - update description",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.notify(f"Added new item: {item_name}", severity="success")
        
        self.refresh_table()
        self.update_stats()
    
    def remove_item(self, barcode: str) -> None:
        """Remove an item from inventory."""
        if barcode in self.inventory:
            if self.inventory[barcode]["quantity"] > 1:
                self.inventory[barcode]["quantity"] -= 1
                self.inventory[barcode]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.notify(f"Removed 1 {self.inventory[barcode]['name']} (Qty: {self.inventory[barcode]['quantity']})", severity="warning")
            else:
                item_name = self.inventory[barcode]["name"]
                del self.inventory[barcode]
                self.notify(f"Completely removed {item_name}", severity="error")
            
            self.refresh_table()
            self.update_stats()
        else:
            self.notify("Item not found in inventory", severity="error")
    
    def process_image_from_input(self) -> None:
        """Process image from input field."""
        image_input = self.query_one("#image_input", Input)
        image_path = image_input.value.strip()
        
        if not image_path:
            self.notify("Please enter an image path", severity="warning")
            return
        
        self.notify("Processing image...", severity="information")
        result = self.image_processor.process_image(image_path)
        
        if "error" in result:
            self.notify(f"Error: {result['error']}", severity="error")
            return
        
        # Extract barcodes from the image
        detected_barcodes = result.get("barcodes", [])
        product_info = result.get("product_info", {})
        
        if detected_barcodes:
            # Update inventory with detected items
            for barcode in detected_barcodes:
                if barcode in self.inventory:
                    # Update existing item with OCR data
                    self.inventory[barcode]["ocr_data"] = result
                    self.inventory[barcode]["verified"] = True
                    self.inventory[barcode]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Update description with OCR info if available
                    if product_info:
                        description_parts = []
                        if "brand" in product_info:
                            description_parts.append(product_info["brand"])
                        if "color" in product_info:
                            description_parts.append(product_info["color"])
                        if "type" in product_info:
                            description_parts.append(product_info["type"])
                        
                        if description_parts:
                            self.inventory[barcode]["description"] = " ".join(description_parts)
                else:
                    # Create new item from OCR data
                    item_name = f"{product_info.get('brand', 'Unknown')} {product_info.get('color', '')} {product_info.get('type', 'Item')}"
                    self.inventory[barcode] = {
                        "name": item_name.strip(),
                        "quantity": 1,
                        "description": f"Auto-detected from image: {Path(image_path).name}",
                        "verified": True,
                        "ocr_data": result,
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
            
            self.refresh_table()
            self.update_stats()
            self.notify(f"Found {len(detected_barcodes)} barcode(s): {', '.join(detected_barcodes)}", severity="success")
        else:
            self.notify("No barcodes detected in image", severity="warning")
        
        image_input.value = ""
    
    def verify_image_from_input(self) -> None:
        """Verify barcode against image."""
        barcode_input = self.query_one("#barcode_input", Input)
        image_input = self.query_one("#image_input", Input)
        
        barcode = barcode_input.value.strip()
        image_path = image_input.value.strip()
        
        if not barcode or not image_path:
            self.notify("Please enter both barcode and image path", severity="warning")
            return
        
        self.notify("Verifying barcode against image...", severity="information")
        verification = self.image_processor.verify_barcode_match(barcode, image_path)
        
        if "error" in verification:
            self.notify(f"Verification error: {verification['error']}", severity="error")
            return
        
        if verification["matches"]:
            # Update inventory item as verified
            if barcode in self.inventory:
                self.inventory[barcode]["verified"] = True
                self.inventory[barcode]["ocr_data"] = verification
                self.inventory[barcode]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.refresh_table()
                self.update_stats()
            
            self.notify(f"✅ Barcode {barcode} matches image!", severity="success")
        else:
            detected = verification.get("detected_barcodes", [])
            if detected:
                self.notify(f"❌ Barcode mismatch! Found: {', '.join(detected)}", severity="error")
            else:
                self.notify(f"❌ No matching barcode found in image", severity="error")
        
        barcode_input.value = ""
        image_input.value = ""
    
    def action_process_image(self) -> None:
        """Keyboard shortcut for processing images."""
        self.process_image_from_input()
    
    def action_verify_image(self) -> None:
        """Keyboard shortcut for verifying images."""
        self.verify_image_from_input()
    
    def auto_process_images_folder(self) -> None:
        """Auto-process all images in the images directory."""
        self.notify("Auto-processing images folder...", severity="information")
        
        # Check if images directory exists
        if not os.path.exists(self.images_directory):
            self.notify(f"Images directory not found: {self.images_directory}", severity="error")
            return
        
        # Get list of image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
        image_files = [f for f in os.listdir(self.images_directory) 
                      if Path(f).suffix.lower() in image_extensions]
        
        if not image_files:
            self.notify("No images found in images directory", severity="warning")
            return
        
        # Batch process all images
        results = self.image_processor.batch_process_images(self.images_directory)
        
        if "error" in results:
            self.notify(f"Error: {results['error']}", severity="error")
            return
        
        # Process results and update inventory
        new_items = 0
        updated_items = 0
        total_barcodes = 0
        
        for filename, result in results.items():
            if filename == "_batch_summary":
                continue
                
            if "error" in result:
                continue
                
            barcodes = result.get("barcodes", [])
            product_info = result.get("product_info", {})
            from_cache = result.get("from_cache", False)
            
            total_barcodes += len(barcodes)
            
            for barcode in barcodes:
                if barcode in self.inventory:
                    # Update existing item
                    self.inventory[barcode]["ocr_data"] = result
                    self.inventory[barcode]["verified"] = True
                    self.inventory[barcode]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Update description with OCR info if available
                    if product_info and not from_cache:
                        description_parts = []
                        if "brand" in product_info:
                            description_parts.append(product_info["brand"])
                        if "color" in product_info:
                            description_parts.append(product_info["color"])
                        if "type" in product_info:
                            description_parts.append(product_info["type"])
                        
                        if description_parts:
                            self.inventory[barcode]["description"] = " ".join(description_parts)
                    
                    updated_items += 1
                else:
                    # Create new item
                    item_name = f"{product_info.get('brand', 'Unknown')} {product_info.get('color', '')} {product_info.get('type', 'Item')}"
                    self.inventory[barcode] = {
                        "name": item_name.strip(),
                        "quantity": 1,
                        "description": f"Auto-detected from image: {filename}",
                        "verified": True,
                        "ocr_data": result,
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    new_items += 1
        
        # Get batch summary
        summary = results.get("_batch_summary", {})
        newly_processed = summary.get("newly_processed", 0)
        from_cache = summary.get("from_cache", 0)
        
        self.refresh_table()
        self.update_stats()
        
        self.notify(
            f"✅ Processed {len(image_files)} images: {newly_processed} new, {from_cache} cached. "
            f"Found {total_barcodes} barcodes. {new_items} new items, {updated_items} updated.",
            severity="success"
        )
    
    def clear_processing_cache(self) -> None:
        """Clear the image processing cache."""
        if self.image_processor.clear_processed_cache():
            self.notify("✅ Processing cache cleared", severity="success")
        else:
            self.notify("❌ Failed to clear processing cache", severity="error")
    
    def show_processing_stats(self) -> None:
        """Show processing statistics."""
        stats = self.image_processor.get_processing_stats()
        
        stats_message = (
            f"📊 Processing Stats: "
            f"{stats['total_images_processed']} images processed, "
            f"{stats['successful_processing']} successful, "
            f"{stats['failed_processing']} failed, "
            f"{stats['total_barcodes_found']} barcodes found. "
            f"Last: {stats['last_processing_date'][:19] if stats['last_processing_date'] != 'Never' else 'Never'}"
        )
        
        self.notify(stats_message, severity="information")
    
    def action_auto_process_images(self) -> None:
        """Keyboard shortcut for auto-processing images."""
        self.auto_process_images_folder()
    
    def action_clear_cache(self) -> None:
        """Keyboard shortcut for clearing cache."""
        self.clear_processing_cache()
    
    def action_save(self) -> None:
        """Save inventory to file."""
        self.save_inventory()
        self.notify("Inventory saved!", severity="success")
    
    def action_reset(self) -> None:
        """Reset inventory."""
        self.inventory = {}
        self.refresh_table()
        self.update_stats()
        self.notify("Inventory reset!", severity="warning")
    
    def load_inventory(self) -> None:
        """Load inventory from file."""
        if os.path.exists(self.inventory_file):
            try:
                with open(self.inventory_file, 'r') as f:
                    self.inventory = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.inventory = {}
    
    def save_inventory(self) -> None:
        """Save inventory to file."""
        try:
            with open(self.inventory_file, 'w') as f:
                json.dump(self.inventory, f, indent=2)
        except IOError:
            self.notify("Failed to save inventory", severity="error")

def main():
    """Run the inventory tracker app."""
    app = InventoryTracker()
    app.run()

if __name__ == "__main__":
    main()