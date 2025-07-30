from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
import typer

class PDFPasswordRemover:
    @staticmethod
    def remove_password(input_path: str, password: str, output_dir: str = None) -> list:
        """
        Remove password from a PDF file or all PDF files in a directory and save as new files.
        Returns a list of output paths to the unlocked PDFs.
        Raises typer.Exit on error for CLI integration.
        output_dir: Optional directory to save unlocked PDFs. If not supplied, uses the same directory as the source file(s).
        """
        path = Path(input_path).expanduser().resolve()
        output_paths = []
        if not path.exists():
            typer.echo(f"File or directory not found: {input_path}")
            raise typer.Exit(code=1)

        output_dir_path = None
        if output_dir:
            # Make output_dir_path relative to the input path (file or directory)
            if path.is_file():
                base_dir = path.parent
            else:
                base_dir = path
            output_dir_path = (base_dir / output_dir).expanduser().resolve()
            if not output_dir_path.exists():
                try:
                    output_dir_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    typer.echo(f"Could not create output directory: {output_dir_path}\nError: {e}")
                    raise typer.Exit(code=1)
            elif not output_dir_path.is_dir():
                typer.echo(f"Output path is not a directory: {output_dir_path}")
                raise typer.Exit(code=1)

        def process_pdf(pdf_path, password):
            try:
                reader = PdfReader(str(pdf_path))
                if reader.is_encrypted:
                    if not reader.decrypt(password):
                        typer.echo(f"Incorrect password or unable to decrypt PDF: {pdf_path}")
                        raise typer.Exit(code=1)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                # Determine output path
                if output_dir_path:
                    out_path = output_dir_path / (pdf_path.stem + "_unlocked" + pdf_path.suffix)
                else:
                    out_path = pdf_path.with_stem(pdf_path.stem + "_unlocked")
                with open(out_path, "wb") as f:
                    writer.write(f)
                return out_path
            except Exception as e:
                typer.echo(f"Error processing {pdf_path}: {e}")
                raise typer.Exit(code=1)

        if path.is_file() and path.suffix.lower() == ".pdf":
            out_path = process_pdf(path, password)
            if out_path:
                output_paths.append(out_path)
        elif path.is_dir():
            for pdf_file in path.glob("*.pdf"):
                out_path = process_pdf(pdf_file, password)
                if out_path:
                    output_paths.append(out_path)
        else:
            typer.echo(f"Input must be a PDF file or a directory containing PDF files: {input_path}")
            raise typer.Exit(code=1)
        return output_paths
