# recover_als_files5.py
import os
import argparse
import logging
import multiprocessing
import shutil
from pathlib import Path
from tqdm import tqdm # External dependency for progress bar: pip install tqdm

# --- Configuration ---

# Ableton-specific markers
ALS_MARKER = b'<Ableton Live Set'
ALP_MARKER = b'PK\x03\x04\x14\x00\x00\x00' # .alp files are ZIP-based

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Core Functions ---

def is_als_or_alp_file(file_path):
    """Check if a file is an Ableton Live Set (.als) or Project (.alp) by content."""
    try:
        with open(file_path, 'rb') as f:
            # Read a slightly larger header for potentially better matching
            header = f.read(256)
            is_als = ALS_MARKER in header
            is_alp = header.startswith(ALP_MARKER)
            # Basic heuristic: .als files are often > 10KB, .alp > 1MB (very rough)
            # Add more checks if needed, e.g., try unzipping a small part for ALP
            return is_als or is_alp
    except PermissionError:
        logging.warning(f"Permission denied accessing: {file_path}")
        return False
    except Exception as e:
        logging.warning(f"Could not read header for {file_path}: {e}")
        return False

def _scan_worker(args):
    """Worker function for parallel scanning a single directory root."""
    root_dir, keywords, base_scan_path, output_base_dir = args
    found_files = {'als': [], 'alp': [], 'keyword': []}
    
    try:
        # Use tqdm for progress within the worker (shows per-process progress)
        # Note: Nested tqdm might look messy in some terminals.
        # For a single overall progress bar, enumeration needs to happen before parallelization.
        for root, dirs, files in os.walk(root_dir, topdown=True):
             # Filter out directories we don't have permission to read, to avoid repeated errors
            accessible_dirs = []
            for d in dirs:
                dir_path = os.path.join(root, d)
                if os.access(dir_path, os.R_OK):
                    accessible_dirs.append(d)
                else:
                    logging.warning(f"Permission denied scanning directory: {dir_path}")
            dirs[:] = accessible_dirs # Modify dirs in place for os.walk

            for file in files:
                file_path = os.path.join(root, file)
                
                # Check permissions before attempting to open
                if not os.access(file_path, os.R_OK):
                    logging.warning(f"Permission denied reading file: {file_path}")
                    continue

                rel_path = os.path.relpath(file_path, base_scan_path)
                output_path = os.path.join(output_base_dir, rel_path)

                try:
                    is_ableton = is_als_or_alp_file(file_path)
                    is_keyword = any(k.lower() in file.lower() for k in keywords if k)

                    if is_ableton:
                        # Rudimentary check if it's more likely ALS or ALP based on extension
                        if file.lower().endswith('.als'):
                            found_files['als'].append((file_path, output_path))
                            logging.debug(f"Found potential .als: {file_path}")
                        elif file.lower().endswith('.alp'):
                            found_files['alp'].append((file_path, output_path))
                            logging.debug(f"Found potential .alp: {file_path}")
                        else: # Header matched, but extension unknown, save as 'als' maybe?
                            found_files['als'].append((file_path, output_path))
                            logging.debug(f"Found potential Ableton file (unknown ext): {file_path}")
                            
                    elif is_keyword:
                        found_files['keyword'].append((file_path, output_path))
                        logging.debug(f"Found keyword match: {file_path}")

                except Exception as e:
                    logging.error(f"Error processing file {file_path}: {e}")

    except PermissionError:
         logging.warning(f"Permission denied scanning directory tree starting at: {root_dir}")
    except Exception as e:
        logging.error(f"Error scanning directory tree {root_dir}: {e}")
        
    return found_files


def save_file(src_dst_tuple):
    """Copies a single file from source to destination, creating dirs."""
    src, dst = src_dst_tuple
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst) # copy2 preserves metadata like modification time
        logging.info(f"Saved: {dst}")
        return True
    except Exception as e:
        logging.error(f"Failed to save {src} to {dst}: {e}")
        return False

# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Recover Ableton Live (.als, .alp) and keyword-matching files.")
    parser.add_argument("scan_directory", type=str, help="The root directory to start scanning from.")
    parser.add_argument("output_directory", type=str, help="The directory where recovered files will be saved (preserving structure).")
    parser.add_argument("-k", "--keywords", type=str, nargs='*', default=[], help="Optional list of keywords to search for in filenames.")
    parser.add_argument("-p", "--processes", type=int, default=os.cpu_count(), help="Number of parallel processes to use for scanning.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging.")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel processing (run sequentially).")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    scan_dir = Path(args.scan_directory).resolve()
    output_dir = Path(args.output_directory).resolve()
    keywords = args.keywords
    num_processes = 1 if args.no_parallel else args.processes

    if not scan_dir.is_dir():
        logging.error(f"Scan directory does not exist or is not a directory: {scan_dir}")
        return
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created output directory: {output_dir}")
        except Exception as e:
            logging.error(f"Could not create output directory {output_dir}: {e}")
            return
    elif not output_dir.is_dir():
        logging.error(f"Output path exists but is not a directory: {output_dir}")
        return


    logging.info(f"Starting scan:")
    logging.info(f"  Source: {scan_dir}")
    logging.info(f"  Destination: {output_dir}")
    logging.info(f"  Keywords: {keywords if keywords else 'None'}")
    logging.info(f"  Parallel Processes: {num_processes}")

    all_found_files = {'als': [], 'alp': [], 'keyword': []}
    
    try:
        # --- Scanning Phase ---
        scan_roots = [d for d in scan_dir.iterdir() if d.is_dir()]
        # Also include files directly in the root scan dir if needed
        # For simplicity, we parallelize based on top-level dirs.
        # Consider adding root files to a separate scan if important.
        if not scan_roots: # Handle case where scan_dir has no subdirectories
            scan_roots = [scan_dir]
            
        worker_args = [(str(root), keywords, str(scan_dir), str(output_dir)) for root in scan_roots]

        logging.info(f"Distributing scan across {len(scan_roots)} root directories using {num_processes} processes...")

        if num_processes > 1:
            try:
                # Create a pool of workers
                with multiprocessing.Pool(processes=num_processes) as pool:
                    # Use tqdm to show progress over the distributed tasks
                    results = list(tqdm(pool.imap_unordered(_scan_worker, worker_args), total=len(worker_args), desc="Scanning Dirs"))
            except Exception as e:
                 logging.error(f"Multiprocessing pool failed: {e}")
                 return # Cannot proceed if pool fails
        else: # Sequential execution
            logging.info("Running scan sequentially...")
            results = []
            for single_arg in tqdm(worker_args, desc="Scanning Dirs"):
                 results.append(_scan_worker(single_arg))


        # Combine results from all workers/tasks
        for result in results:
            all_found_files['als'].extend(result['als'])
            all_found_files['alp'].extend(result['alp'])
            all_found_files['keyword'].extend(result['keyword'])

        total_found = sum(len(v) for v in all_found_files.values())
        logging.info(f"Scan complete. Found {len(all_found_files['als'])} ALS, {len(all_found_files['alp'])} ALP, {len(all_found_files['keyword'])} keyword files (Total: {total_found}).")

        # --- Saving Phase ---
        if total_found > 0:
            logging.info("Starting file copy process...")
            
            # Combine all files for saving progress bar
            all_files_to_save = all_found_files['als'] + all_found_files['alp'] + all_found_files['keyword']
            
            # Use multiprocessing pool for potentially faster I/O bound saving
            # (May not always be faster due to disk contention, but worth trying)
            if num_processes > 1 and len(all_files_to_save) > num_processes: # Only use pool if enough files
                 try:
                     with multiprocessing.Pool(processes=num_processes) as pool:
                          save_results = list(tqdm(pool.imap_unordered(save_file, all_files_to_save), total=len(all_files_to_save), desc="Saving Files"))
                 except Exception as e:
                    logging.error(f"Multiprocessing pool failed during saving: {e}")
                    # Optionally: fallback to sequential saving here
                    save_results = [False] # Indicate failure
            else: # Sequential saving
                 logging.info("Running save sequentially...")
                 save_results = []
                 for file_tuple in tqdm(all_files_to_save, desc="Saving Files"):
                      save_results.append(save_file(file_tuple))

            successful_saves = sum(1 for r in save_results if r)
            failed_saves = len(all_files_to_save) - successful_saves
            logging.info(f"File saving complete. Successfully saved: {successful_saves}, Failed: {failed_saves}.")
        else:
            logging.info("No files matching the criteria were found.")

    except KeyboardInterrupt:
        logging.warning("\nScan interrupted by user. Exiting...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True) # Log stack trace

if __name__ == "__main__":
    # Required for multiprocessing, especially when bundled (e.g., with PyInstaller)
    multiprocessing.freeze_support()
    main()