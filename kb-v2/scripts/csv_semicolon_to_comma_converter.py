import csv
import re

def convert_semicolons_to_commas_with_quotes(input_file, output_file):
    """
    Convert semicolons back to commas within field values and wrap those fields in double quotes
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
                
                rows_processed = 0
                fields_converted = 0
                
                for row in reader:
                    converted_row = []
                    
                    for field in row:
                        # Check if field contains semicolons
                        if ';' in field:
                            # Replace semicolons with commas
                            converted_field = field.replace(';', ',')
                            converted_row.append(converted_field)
                            fields_converted += 1
                            print(f"Converted: '{field}' -> '{converted_field}'")
                        else:
                            converted_row.append(field)
                    
                    writer.writerow(converted_row)
                    rows_processed += 1
                
                print(f"\n{'='*50}")
                print(f"CONVERSION SUMMARY")
                print(f"{'='*50}")
                print(f"Total rows processed: {rows_processed}")
                print(f"Total fields converted: {fields_converted}")
                print(f"Output saved to: {output_file}")
                
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found!")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

def preview_conversion(input_file, num_rows=5):
    """
    Preview what the conversion will look like without actually converting
    """
    try:
        print(f"PREVIEW - First {num_rows} rows of conversion:")
        print("="*80)
        
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            
            for i, row in enumerate(reader):
                if i >= num_rows:
                    break
                    
                print(f"\nRow {i + 1}:")
                print("-" * 40)
                
                for j, field in enumerate(row):
                    if ';' in field:
                        converted = field.replace(';', ',')
                        print(f"  Field {j + 1}: '{field}' -> '{converted}' (WILL BE CONVERTED)")
                    else:
                        print(f"  Field {j + 1}: '{field}' (NO CHANGE)")
                        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found!")
    except Exception as e:
        print(f"Error during preview: {str(e)}")

def main():
    # Configuration
    input_file = "categories_with_semicolons.csv"  # Change this to your input file name
    output_file = "categories_fixed.csv"          # Change this to your desired output file name
    
    print("CSV Semicolon to Comma Converter")
    print("="*50)
    
    # Check if input file exists
    import os
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' not found!")
        print("Please update the 'input_file' variable with the correct path to your CSV file.")
        return
    
    # Show preview first
    print("STEP 1: Preview of changes")
    preview_conversion(input_file)
    
    # Ask for confirmation
    print("\n" + "="*50)
    response = input("Do you want to proceed with the conversion? (y/N): ").strip().lower()
    
    if response == 'y' or response == 'yes':
        print("\nSTEP 2: Converting file...")
        convert_semicolons_to_commas_with_quotes(input_file, output_file)
        
        # Show sample of output
        print(f"\nSample of converted file ({output_file}):")
        print("-" * 50)
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 3:  # Show first 3 lines
                        break
                    print(f"Line {i + 1}: {line.strip()}")
        except:
            pass
            
    else:
        print("Conversion cancelled.")

if __name__ == "__main__":
    main()
