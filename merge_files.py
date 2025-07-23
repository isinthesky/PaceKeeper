import os


def collect_python_files(directory: str) -> list:
    """
    Recursively collects all Python file paths from the specified directory.
    """
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):  # Only collect Python files
                python_files.append(os.path.join(root, file))
    return python_files


def add_file_header(file_path: str) -> str:
    """
    Reads the content of a file, adds a comment at the top with the file path and name
    if it does not already contain a header.
    """
    with open(file_path, encoding="utf-8") as file:
        content = file.readlines()

    # Check if the first line is already a comment with the file path
    if content and content[0].startswith("# File:"):
        return "".join(content)  # Return as is if header exists

    # Add header with file path and name
    header = f"# File: {file_path}\n\n"
    return header + "".join(content)


def merge_and_output(directory: str, output_directory: str):
    """
    Merges all Python files in the directory into a single output file with headers.
    Ensures unique numbering for output files.
    """
    # Collect all Python files
    python_files = collect_python_files(directory)

    # Prepare merged content with headers
    merged_content = []
    for file_path in python_files:
        try:
            file_content_with_header = add_file_header(file_path)
            merged_content.append(file_content_with_header)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Generate unique output file name
    base_output_name = "collections-summary"
    numbering = 1
    while True:
        output_file = os.path.join(output_directory, f"{base_output_name}-{numbering}.py")
        if not os.path.exists(output_file):
            break
        numbering += 1

    # Write merged content to output file
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("\n\n".join(merged_content))

    print(f"Merged file created: {output_file}")


# Example usage
if __name__ == "__main__":
    source_directory = "./breaktrack"
    output_directory = "./output"

    os.makedirs(output_directory, exist_ok=True)  # Ensure output directory exists
    merge_and_output(source_directory, output_directory)
