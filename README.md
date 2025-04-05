# Ableton Live Project Recovery Scripts

This project contains a collection of Python scripts designed to help locate and recover potentially lost or damaged Ableton Live Set (`.als`) and Ableton Live Pack (`.alp`) files from your file system. The scripts range from basic file extension scanning to more advanced methods involving file header analysis, keyword searching, parallel processing, command-line configuration, and progress tracking.

## Scripts Overview

There are five main scripts in this collection, each building upon the previous one or offering different capabilities:

1.  **`recover_als_files.py`**
    * **Functionality:** Performs a basic recursive scan of a specified directory for files ending with the `.als` extension.
    * **Method:** Simple filename matching (`*.als`).
    * **Use Case:** Best for straightforward situations where files likely retain their original extensions. Configuration requires editing the script.

2.  **`recover_als_files2.py`**
    * **Functionality:** Improves upon the basic script by adding a file header check.
    * **Method:** Scans for files ending in `.als` **OR** files whose initial bytes match the typical header of an `.als` file (which are often zip-compressed). This helps find `.als` files even if their extension has been changed or lost.
    * **Use Case:** Useful when file extensions might be unreliable or missing. Configuration requires editing the script.

3.  **`recover_als_files3.py`**
    * **Functionality:** Extends recovery by adding a keyword-based search alongside the `.als` detection from Script 2.
    * **Method:** Finds `.als` files (using extension and header check) **AND** any other file whose name contains one of the specified keywords (case-insensitive). Keywords might relate to project names, specific samples, or common backup naming conventions.
    * **Use Case:** Helpful for finding not just the main `.als` files but also potentially related project files, samples, or backups based on naming patterns. Configuration requires editing the script.

4.  **`recover_als_files4.py`**
    * **Functionality:** Comprehensive and parallelized recovery for `.als`, `.alp`, and keyword files using basic configuration within the script.
    * **Method:**
        * Uses enhanced header checking to identify both `.als` (XML marker or ZIP header) and `.alp` (ZIP header) files.
        * Includes the keyword search functionality.
        * Utilizes the `multiprocessing` module to perform the scan in parallel across multiple CPU cores.
        * Saves recovered `.als`, `.alp`, and keyword-matched files into separate subdirectories (`ALS_Files`, `ALP_Files`, `Keyword_Files`) within the main output folder.
    * **Use Case:** Good for comprehensive scans on large volumes when basic script editing for configuration is acceptable. Leverages multi-core CPUs for speed.

5.  **`recover_als_files5.py`**
    * **Functionality:** The most advanced and user-friendly script, featuring command-line configuration, progress tracking, enhanced error handling, and better output organization.
    * **Method:**
        * Builds on Script 4's robust header checking for `.als` and `.alp` files and keyword searching.
        * Uses `argparse` for **command-line configuration** of scan/output directories and keywords (no script editing needed).
        * Employs the `logging` module for structured output (info, warnings, errors). Optional verbose mode (`-v`).
        * Displays a **progress bar** (`tqdm`) during scanning and saving phases.
        * Copies found files while **preserving the relative directory structure** from the scan source within the output directory, preventing filename collisions.
        * Uses `shutil.copy2` to preserve file metadata (like modification time).
        * Includes enhanced error handling (e.g., logs permission errors during scanning).
        * Offers parallel processing (`multiprocessing`) by default, with an option to disable (`--no-parallel`).
    * **Use Case:** Recommended for most recovery tasks due to its flexibility, user feedback (progress bar, logging), robustness, and better output management. Ideal for large or complex scans. **Requires `tqdm` library.**

## Usage

### Scripts 1-4 (Manual Configuration)

1.  **Choose a Script:** Select script 1, 2, 3, or 4.
2.  **Configure:** Open the chosen `.py` script in a text editor or VS Code.
    * Modify the `scan_directory` variable to the path you want to search (e.g., `'D:\\'`, `'/Users/your_user/Documents'`). **Be cautious when scanning entire drives like `'C:\\'` as it can take a very long time.**
    * Modify the `output_directory` variable to the path where you want the recovered files to be copied.
    * For `recover_als_files3.py` and `recover_als_files4.py`, update the `keywords` list.
3.  **Run the Script:** Open a terminal or command prompt, navigate to the directory containing the scripts, and run your chosen script using Python:
    ```bash
    python recover_als_files.py
    # or
    python recover_als_files2.py
    # etc.
    ```
4.  **Check Output:** Once the script finishes, check the specified `output_directory`. Script 4 creates subdirectories.

### Script 5 (Command-Line Configuration)

1.  **Install Dependency:** If you haven't already, install the `tqdm` library:
    ```bash
    pip install tqdm
    ```
2.  **Run from Command Line:** Open a terminal or command prompt, navigate to the directory containing the script, and run `recover_als_files5.py` providing the scan and output directories as arguments. Use options for keywords, parallelism, and verbosity.

    **Basic Syntax:**
    ```bash
    python recover_als_files5.py <SCAN_DIRECTORY> <OUTPUT_DIRECTORY> [options]
    ```

    **Common Options:**
    * `-k KEYWORD1 KEYWORD2 ...` or `--keywords KEYWORD1 KEYWORD2 ...`: Specify keywords to search for in filenames.
    * `-p NUM` or `--processes NUM`: Set the number of parallel processes (default: all CPU cores).
    * `--no-parallel`: Disable parallel scanning and run sequentially.
    * `-v` or `--verbose`: Enable detailed debug logging output.
    * `-h` or `--help`: Show all available options.

    **Examples:**
    * Scan drive `D:\` and save results to `C:\RecoveredData`, searching for "projectX" or "backup":
        ```bash
        python recover_als_files5.py D:\ C:\RecoveredData -k projectX backup
        ```
    * Scan user's `Documents`, save to `Recovered_Ableton` folder, use 4 processes, show verbose logs:
        ```bash
        # macOS/Linux:
        python recover_als_files5.py ~/Documents Recovered_Ableton -p 4 -v
        # Windows:
        python recover_als_files5.py C:\Users\YourUser\Documents Recovered_Ableton -p 4 -v
        ```
    * Scan `C:\` sequentially, save to `C:\Recovery`:
        ```bash
        python recover_als_files5.py C:\ C:\Recovery --no-parallel
        ```
3.  **Check Output:** Once the script finishes, check the specified `<OUTPUT_DIRECTORY>`. Files will be organized mirroring their original location relative to the `<SCAN_DIRECTORY>`.

## Dependencies

* **Scripts 1-3:** Use only Python standard libraries (`os`). *(Note: Scripts 2 & 3 import `datetime` and `subprocess` but don't use them)*.
* **Script 4:** Uses standard libraries (`os`, `multiprocessing`).
* **Script 5:**
    * Standard Libraries: `os`, `multiprocessing`, `argparse`, `logging`, `shutil`, `pathlib`.
    * External Library: `tqdm` (for progress bars). Install using: `pip install tqdm`