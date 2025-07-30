import argparse
import warnings

import pandas as pd
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn

warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
)

console = Console()


def merge_xlsx(input_files, output_file):
    # Variable to hold the DataFrames:
    dataframes = []

    # Message to indicate the start of the process:
    console.print("[cyan]Merging Excel files...[/cyan]\n")

    # Create a progress bar to show the merging process
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        TextColumn(
            "[yellow]{task.completed}[/yellow]/[green]{task.total}[/green] files"
        ),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:

        # Initialize the progress bar task
        task = progress.add_task("Processing files", total=len(input_files))

        # Iterate through each input file and read it into a DataFrame
        for idx, file in enumerate(input_files):
            progress.console.print(
                f"[yellow][{idx+1}/{len(input_files)}][/yellow] Reading [green]{file}[/green]"
            )
            df = pd.read_excel(file)
            dataframes.append(df)
            progress.update(task, advance=1)

    # Message to indicate that the merging is in progress:
    console.print(f"\n[cyan]Writing merged file to [green]{output_file}[/green][/cyan]")

    # Merge all dataframes into one and save to output file
    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.to_excel(output_file, index=False)

    # Success message after merging:
    console.print("[green]Merge complete![/green]")


def main():
    parser = argparse.ArgumentParser(description="Merge multiple Excel files into one.")
    parser.add_argument(
        "input_files",
        nargs="+",
        help="List of input Excel files to merge (e.g., file1.xlsx file2.xlsx).",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output file name for the merged Excel file.",
    )

    # TODO: Add a little tip informing that user can use wildcards to select files (e.g., /path/to/directory/*.xlsx)
    # TODO: Add option to plain/clear stdout instead of rich console with progress bar and etc.

    args = parser.parse_args()

    merge_xlsx(args.input_files, args.output)
