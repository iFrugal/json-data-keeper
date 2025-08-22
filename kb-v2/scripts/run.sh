#!/bin/bash

# Image Downloader Runner Script
# This script sets up the environment and runs the image downloader

set -e  # Exit on any error

echo "============================================"
echo "      CSV Image Downloader Runner"
echo "============================================"

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed or not in PATH!"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

print_success "Python found: $($PYTHON_CMD --version)"

# Check if pip is available
print_status "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        print_error "pip is not installed or not in PATH!"
        exit 1
    else
        PIP_CMD="pip"
    fi
else
    PIP_CMD="pip3"
fi

print_success "pip found: $($PIP_CMD --version)"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_warning "requirements.txt not found. Creating one..."
    cat > requirements.txt << EOF
requests>=2.25.1
EOF
    print_success "requirements.txt created with necessary dependencies"
fi

# Check if image_downloader.py exists
if [ ! -f "image_downloader.py" ]; then
    print_error "image_downloader.py not found in current directory!"
    print_error "Please make sure the Python script is in the same directory as this shell script."
    exit 1
fi

# Check if CSV file exists
CSV_FILE="categories.csv"
if [ ! -f "$CSV_FILE" ]; then
    print_warning "CSV file '$CSV_FILE' not found!"
    print_warning "Please make sure your CSV file is named 'categories.csv' and is in the current directory."
    read -p "Do you want to continue anyway? The script will show an error but won't crash. (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Exiting. Please add your CSV file and try again."
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in virtual environment
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
print_success "Dependencies installed successfully"

# Create images directory if it doesn't exist
if [ ! -d "images" ]; then
    print_status "Creating images directory..."
    mkdir -p images
    print_success "Images directory created"
fi

# Display current directory contents
print_status "Current directory contents:"
ls -la

echo
print_status "Starting image downloader..."
echo "============================================"

# Run the Python script
python image_downloader.py

echo
echo "============================================"
print_success "Script execution completed!"

# Show final directory structure
if [ -d "images" ]; then
    echo
    print_status "Final directory structure:"
    tree images/ 2>/dev/null || find images/ -type d -exec echo "📁 {}" \; -o -type f -exec echo "📄 {}" \;
fi

# Deactivate virtual environment
deactivate

print_success "Done! Check the 'images' folder for downloaded files."