#!/usr/bin/python3

import typer
import tkinter as tk
from tkinter import filedialog

from pdf_password_remover.utils import pdf_utils


# Add Tkinter for file/directory picker
def pick_path():
    try:
        from tkinterdnd2 import TkinterDnD, DND_FILES
        import tkinter as tk
        from tkinter import filedialog
        use_tkdnd = True
    except ImportError:
        use_tkdnd = False
        try:
            import tkinter as tk
            from tkinter import filedialog
        except ImportError:
            tk = None
            filedialog = None

    while True:
        use_picker = typer.prompt("Would you like to use a file/directory picker dialog? (y = yes, n = manual input)", default="y", show_default=False)
        if use_picker.lower() == "n" or not (tk and filedialog):
            return typer.prompt("Enter the path to the password-protected PDF file or directory")
        else:
            picker_type = typer.prompt("Would you like to select a file or a directory? (f = file, d = directory)", default="f", show_default=False)
            typer.echo("Please choose a file or directory in the dialog.")
            if use_tkdnd:
                root = TkinterDnD.Tk()
            else:
                root = tk.Tk()
            root.withdraw()
            if picker_type.lower() == "d":
                path = filedialog.askdirectory(title="Select a directory containing PDF files", parent=root)
            else:
                path = filedialog.askopenfilename(title="Select a PDF file", parent=root)
            root.destroy()
            if path:
                return path
            else:
                typer.echo("No file or directory selected.")

app = typer.Typer(add_completion=False)

@app.command()
def remove_password(
    input_path: str = typer.Argument(None, help="Path to the password-protected PDF file or directory", show_default=False),
    password: str = typer.Argument(None, help="Password for the PDF file(s)", show_default=False),
    output_dir: str = typer.Option(None, "--output", "-o", help="Directory to save the unlocked PDF file(s)")
):
    """Remove password from a PDF file or all PDF files in a directory and save as new file(s)."""
    if not input_path:
        input_path = pick_path()
        if not input_path:
            typer.echo("No file or directory selected. Exiting.")
            raise typer.Exit(code=1)
    if not password:
        typer.echo("Please focus the terminal window before entering the password.")
        import getpass
        password = getpass.getpass("Enter the password for the PDF file(s): ")
    if output_dir is None:
        output_dir = typer.prompt("Enter the output directory for the unlocked PDF file(s) (press Enter to use the source directory)", default="", show_default=False)
        if output_dir == "":
            output_dir = None

    output_paths = pdf_utils.PDFPasswordRemover.remove_password(input_path, password, output_dir)
    if len(output_paths) == 1:
        typer.echo(f"Unlocked PDF saved as: {output_paths[0]}")
    elif len(output_paths) > 1:
        typer.echo("Unlocked PDFs saved:")
        for path in output_paths:
            typer.echo(f"- {path}")
    else:
        typer.echo("No PDF files were processed.")


if __name__ == "__main__":
    app()
