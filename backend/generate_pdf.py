import os
from pathlib import Path
from fpdf import FPDF
from datetime import datetime

class CodePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "SFPMS Backend Code Documentation", 0, 1, "C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_file_section(self, filepath, filename):
        # Add file heading
        self.set_font("Arial", "B", 12)
        self.set_text_color(0, 0, 128)  # Dark blue
        self.cell(0, 10, f"File: {filename}", 0, 1)
        self.set_text_color(0, 0, 0)  # Reset to black
        
        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {str(e)}"
        
        # Add content
        self.set_font("Courier", "", 9)
        
        if content.strip():
            # Split content into lines and add with proper spacing
            lines = content.split('\n')
            for line in lines:
                # Handle long lines by wrapping
                if len(line) > 100:
                    self.multi_cell(0, 5, line)
                else:
                    self.cell(0, 5, line, 0, 1)
        else:
            self.set_font("Courier", "I", 9)
            self.cell(0, 5, "(Empty file)", 0, 1)
        
        # Add spacing between files
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

def main():
    # Initialize PDF
    pdf = CodePDF()
    pdf.add_page()
    
    # Get the backend directory
    backend_dir = Path(__file__).parent
    
    # Files to include (in order)
    files_to_include = [
        "app.py",
        "config.py",
        "database.py",
    ]
    
    # Add main files
    for filename in files_to_include:
        filepath = backend_dir / filename
        if filepath.exists():
            pdf.add_file_section(filepath, filename)
    
    # Add models section header
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(128, 0, 0)  # Dark red
    pdf.cell(0, 10, "Models", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    # Add model files
    models_dir = backend_dir / "models"
    model_files = sorted([
        "__init__.py",
        "daily_log.py",
        "log_reviews.py",
        "notifications.py",
        "organization.py",
        "placements.py",
        "reports.py",
        "student.py",
        "supervisor_assignment.py",
        "user.py",
    ])
    
    for filename in model_files:
        filepath = models_dir / filename
        if filepath.exists():
            pdf.add_file_section(filepath, f"models/{filename}")
    
    # Save PDF
    output_path = backend_dir / "SFPMS_Backend_Code.pdf"
    pdf.output(str(output_path))
    print(f"PDF generated successfully: {output_path}")

if __name__ == "__main__":
    main()
