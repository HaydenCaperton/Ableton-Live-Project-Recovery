import os
import datetime

def scan_for_als_files(directory):
    """Scan a directory for .als files."""
    recovered_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.als') or is_als_file(os.path.join(root, file)):
                file_path = os.path.join(root, file)
                recovered_files.append(file_path)
                print(f"Found .als file: {file_path}")
    return recovered_files

def is_als_file(file_path):
    """Check if a file is an Ableton Live Set (.als) by its header."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)
            return header == b'PK\x03\x04\x14\x00\x00\x00'
    except:
        return False

def scan_for_files_by_keywords(directory, keywords):
    """
    Scan a directory for files containing specific keywords in their names.
    Args:
        directory (str): The directory to scan.
        keywords (list): A list of keywords to search for in file names.
    Returns:
        list: A list of file paths that match the keywords.
    """
    matching_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if any keyword is in the file name (case-insensitive)
            if any(keyword.lower() in file.lower() for keyword in keywords):
                file_path = os.path.join(root, file)
                matching_files.append(file_path)
                print(f"Found matching file: {file_path}")
    return matching_files

def save_recovered_files(recovered_files, output_dir):
    """Save recovered files to a specified output directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_path in recovered_files:
        file_name = os.path.basename(file_path)
        output_path = os.path.join(output_dir, file_name)
        with open(file_path, 'rb') as src_file, open(output_path, 'wb') as dest_file:
            dest_file.write(src_file.read())
        print(f"Saved: {output_path}")

def main():
    # Specify the directory to scan
    scan_directory = 'C:\\'  # Adjust this for your system
    # Specify the directory to save recovered files
    output_directory = 'C:\\Recovered_Ableton_Files_Advanced_Custom'
    # Specify the keywords to search for
    keywords = ["Somni", "Luminara", "Moonflower", "Afterlude", ""]

    # Scan for .als files
    als_files = scan_for_als_files(scan_directory)
    # Scan for files matching the keywords
    keyword_files = scan_for_files_by_keywords(scan_directory, keywords)

    # Combine the results (avoid duplicates)
    all_recovered_files = list(set(als_files + keyword_files))

    # Save recovered files
    if all_recovered_files:
        save_recovered_files(all_recovered_files, output_directory)
        print(f"Recovery complete. Files saved to: {output_directory}")
    else:
        print("No files were found.")

if __name__ == "__main__":
    main()