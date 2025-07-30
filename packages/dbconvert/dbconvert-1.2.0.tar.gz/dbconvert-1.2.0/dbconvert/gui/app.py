import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from dbconvert.converters.converter_factory import ConverterFactory
from dbconvert.writers.sqlite_writer import SQLiteWriter
from dbconvert.core.enums import DatabaseType
from dbconvert.core.loggingsetup import LoggerManager
import os
from importlib.metadata import version
from dbconvert.core.metadata import load_pyproject_metadata
from PIL import Image, ImageTk
import webbrowser

logger = LoggerManager.get_logger()

class DbConvertGUI:
    def __init__(self):
        self.current_version = version("dbconvert")
        self.metadata = load_pyproject_metadata()
        self.root = tk.Tk()
        self.root.title(f"DbConvert v{self.current_version}")
        self.root.minsize(600, 400)
        
        self.setup_window_icon()
        self.setup_ui()
        self.setup_logging()
        self.setup_footer()
    
    def setup_window_icon(self):
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                icon = Image.open(logo_path)
                icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon)
                self.root.iconphoto(True, icon_photo)
            except Exception as e:
                logger.error(f"Could not set window icon: {str(e)}")

    def setup_logging(self):
        # Create a ScrolledText widget for logging
        self.output_text = scrolledtext.ScrolledText(self.root, height=20, width=50)
        self.output_text.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        # Configure the logger to use the text widget
        LoggerManager.set_gui_logger(self.output_text)

    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Database type selection
        ttk.Label(main_frame, text="Database Type").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.db_type = tk.StringVar(value=DatabaseType.values()[0])
        db_combo = ttk.Combobox(main_frame, textvariable=self.db_type, values=DatabaseType.values(), state="readonly")
        db_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Connection string
        ttk.Label(main_frame, text="Connection String").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.conn_string = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.conn_string, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # SQLite file path
        ttk.Label(main_frame, text="SQLite File Path").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sqlite_path = tk.StringVar()
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(path_frame, textvariable=self.sqlite_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_sqlite).pack(side=tk.RIGHT, padx=(5,0))
        
        # Convert button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Button(button_frame, text="Convert", command=self.convert).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(button_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)

    def setup_footer(self):
        footer = tk.Frame(self.root, bg="#f0f0f0", pady=5)
        footer.grid(row=6, column=0, columnspan=3, sticky="ew")
        self.root.grid_rowconfigure(6, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        internal_urls = self.metadata.get("internalurls", {})
        author_username = internal_urls.get("author_username", "Author")
        author_url = internal_urls.get("author_linkedin", "#")
        project_name = self.metadata.get("name", "Project")
        project_repo = self.metadata.get("repository", "#")

        author_link = tk.Label(footer, text=author_username, fg="blue", cursor="hand2", bg="#f0f0f0", font=(None, 9, "underline"))
        separator = tk.Label(footer, text=" | ", bg="#f0f0f0")
        repo_link = tk.Label(footer, text=project_name, fg="blue", cursor="hand2", bg="#f0f0f0", font=(None, 9, "underline"))

        # Pack all to the left
        author_link.pack(side="left", padx=(10, 2))
        separator.pack(side="left", padx=(2, 2))
        repo_link.pack(side="left")

        # Click events
        author_link.bind("<Button-1>", lambda e: webbrowser.open_new(author_url))
        repo_link.bind("<Button-1>", lambda e: webbrowser.open_new(project_repo))

    def browse_sqlite(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".sqlite",
            filetypes=[("SQLite databases", "*.sqlite"), ("All files", "*.*")]
        )
        if filename:
            self.sqlite_path.set(filename)

    def reset(self):
        """Reset all input fields to their default values"""
        self.db_type.set(DatabaseType.values()[0])
        self.conn_string.set("")
        self.sqlite_path.set("")

    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)

    def convert(self):
        logger = LoggerManager.get_logger()
        try:
            # Validate inputs
            if not self.conn_string.get():
                logger.error("Please enter a connection string")
                messagebox.showerror("Error", "Please enter a connection string")
                return
            if not self.sqlite_path.get():
                logger.error("Please select a SQLite file path")
                messagebox.showerror("Error", "Please select a SQLite file path")
                return

            # Create converter
            converter = ConverterFactory.create_converter(
                self.db_type.get(),
                self.conn_string.get()
            )

            # Read source database
            tables = converter.read_all_tables()

            # Write to SQLite
            writer = SQLiteWriter(self.sqlite_path.get())
            writer.write_all_tables(tables)

            # Show success message
            logger.info("Conversion completed successfully!")
            messagebox.showinfo("Success", "Database conversion completed successfully!")

        except Exception as e:
            logger.error(f"Error occurred during conversion: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def mainloop(self):
        self.root.mainloop()

def main():
    app = DbConvertGUI()
    app.mainloop()

if __name__ == "__main__":
    main() 