# Ableton Live Project Recovery Scripts

This project contains a collection of Python scripts designed to help locate and recover potentially lost or damaged Ableton Live Set (`.als`) and Ableton Live Pack (`.alp`) files from your file system. The scripts range from basic file extension scanning to more advanced methods involving file header analysis, keyword searching, and parallel processing.

## Scripts Overview

There are four main scripts in this collection, each offering different capabilities:

1.  **`recover_als_files.py`**
    * **Functionality:** Performs a basic recursive scan of a specified directory for files ending with the `.als` extension.
    * **Method:** Simple filename matching (`*.als`).
    * **Use Case:** Best for straightforward situations where files likely retain their original extensions.

2.  **`recover_als_files2.py`**
    * **Functionality:** Improves upon the basic script by adding a file header check.
    * **Method:** Scans for files ending in `.als` **OR** files whose initial bytes match the typical header of an `.als` file (which are often zip-compressed). This helps find `.als` files even if their extension has been changed or lost.
    * **Use Case:** Useful when file extensions might be unreliable or missing.

3.  **`recover_als_files3.py`**
    * **Functionality:** Extends recovery by adding a keyword-based search alongside the `.als` detection from Script 2.
    * **Method:** Finds `.als` files (using extension and header check) **AND** any other file whose name contains one of the specified keywords (case-insensitive). Keywords might relate to project names, specific samples, or common backup naming conventions.
    * **Use Case:** Helpful for finding not just the main `.als` files but also potentially related project files, samples, or backups based on naming patterns.

4.  **`recover_als_files4.py`**
    * **Functionality:** The most advanced script, offering parallelized scanning for `.als`, `.alp`, and keyword-matching files with improved detection and organization.
    * **Method:**
        * Uses enhanced header checking to identify both `.als` (XML marker or ZIP header) and `.alp` (ZIP header) files.
        * Includes the keyword search functionality.
        * Utilizes the `multiprocessing` module to perform the scan in parallel across multiple CPU cores, significantly speeding up the process on large drives or directories.
        * Attempts to prioritize scanning folders that look like standard Ableton project directories.
        * Saves recovered `.als`, `.alp`, and keyword-matched files into separate subdirectories within the main output folder for better organization.
        * Includes basic error handling during file saving and allows graceful exit on `Ctrl+C`.
    * **Use Case:** Best for comprehensive scans on large storage volumes, recovering both `.als` and `.alp` files, leveraging multi-core CPUs for speed, and organizing the output effectively.

## Usage

1.  **Choose a Script:** Select the script that best suits your recovery needs based on the descriptions above.
2.  **Configure:** Open the chosen `.py` script in a text editor or VS Code.
    * Modify the `scan_directory` variable to the path you want to search (e.g., `'D:\\'`, `'/Users/your_user/Documents'`). **Be cautious when scanning entire drives like `'C:\\'` as it can take a very long time.**
    * Modify the `output_directory` variable to the path where you want the recovered files to be copied. Ensure this directory exists or the script can create it.
    * For `recover_als_files3.py` and `recover_als_files4.py`, update the `keywords` list with terms relevant to the projects you are trying to find.
3.  **Run the Script:** Open a terminal or command prompt, navigate to the directory containing the scripts, and run your chosen script using Python:
    ```bash
    python recover_als_files.py
    # or
    python recover_als_files2.py
    # or
    python recover_als_files3.py
    # or
    python recover_als_files4.py
    ```
4.  **Check Output:** Once the script finishes, check the specified `output_directory` for the recovered files. Script 4 will create subdirectories (`ALS_Files`, `ALP_Files`, `Keyword_Files`).

## Dependencies

These scripts primarily rely on Python's standard libraries:
* `os`: For file system interaction (walking directories, checking paths, joining paths).
* `multiprocessing`: Used only in `recover_als_files4.py` for parallel scanning.

No external libraries need to be installed via pip.

*(Note: `recover_als_files2.py` and `recover_als_files3.py` import `datetime` and `subprocess` but do not appear to use them. These could be removed for cleanup.)*