import os
import multiprocessing
from multiprocessing import Pool, cpu_count

# Define Ableton-specific markers inside .als files
ALS_MARKER = b'<Ableton Live Set'
ALP_MARKER = b'PK\x03\x04\x14\x00\x00\x00'  # .alp files are ZIP-based

def is_als_or_alp_file(file_path):
    """Check if a file is an Ableton Live Set (.als) or Project (.alp) by content."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(100)  # Read first 100 bytes for better accuracy
            return ALS_MARKER in header or header.startswith(ALP_MARKER)
    except Exception:
        return False

def scan_for_files(directory, keywords):
    """Scan a directory for .als, .alp, and keyword-matching files."""
    als_files = []
    alp_files = []
    keyword_files = []

    for root, dirs, files in os.walk(directory):
        # Prioritize scanning folders with Ableton-specific structures
        if any(folder in dirs for folder in ["Samples", "Ableton Project Info"]):
            print(f"Likely Ableton Project found in: {root}")

        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.als') and is_als_or_alp_file(file_path):
                als_files.append(file_path)
                print(f"Found .als file: {file_path}")
            elif file.endswith('.alp') and is_als_or_alp_file(file_path):
                alp_files.append(file_path)
                print(f"Found .alp file: {file_path}")
            elif any(keyword.lower() in file.lower() for keyword in keywords):
                keyword_files.append(file_path)
                print(f"Found keyword-matching file: {file_path}")

    return {
        'als_files': als_files,
        'alp_files': alp_files,
        'keyword_files': keyword_files,
    }

def save_recovered_files(recovered_files, output_dir):
    """Save recovered files to a specified output directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_path in recovered_files:
        try:
            file_name = os.path.basename(file_path)
            output_path = os.path.join(output_dir, file_name)
            with open(file_path, 'rb') as src_file, open(output_path, 'wb') as dest_file:
                dest_file.write(src_file.read())
            print(f"Saved: {output_path}")
        except Exception as e:
            print(f"Failed to save {file_path}: {e}")

def parallel_scan(directory, keywords, num_processes):
    """Perform a parallel scan of the directory using multiple processes."""
    subdirs = [os.path.join(directory, d) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    if not subdirs:
        subdirs = [directory]

    with Pool(processes=num_processes) as pool:
        results = pool.starmap(scan_for_files, [(subdir, keywords) for subdir in subdirs])

    combined_results = {'als_files': [], 'alp_files': [], 'keyword_files': []}
    for result in results:
        combined_results['als_files'].extend(result['als_files'])
        combined_results['alp_files'].extend(result['alp_files'])
        combined_results['keyword_files'].extend(result['keyword_files'])

    return combined_results

def main():
    try:
        scan_directory = 'C:\\'  # Adjust this for your system
        output_directory = 'C:\\Recovered_Ableton_Files'
        keywords = ["homeless transfer"]
        num_processes = cpu_count()

        print(f"Scanning {scan_directory} with {num_processes} processes...")
        results = parallel_scan(scan_directory, keywords, num_processes)

        if results['als_files']:
            save_recovered_files(results['als_files'], os.path.join(output_directory, 'ALS_Files'))
        if results['alp_files']:
            save_recovered_files(results['alp_files'], os.path.join(output_directory, 'ALP_Files'))
        if results['keyword_files']:
            save_recovered_files(results['keyword_files'], os.path.join(output_directory, 'Keyword_Files'))

        if not results['als_files'] and not results['alp_files'] and not results['keyword_files']:
            print("No files were found.")

    except KeyboardInterrupt:
        print("\nScan interrupted by user. Exiting gracefully...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
