import tkinter as tk, os, pandas as pd
from tkinter import ttk, messagebox


class DataCleanerGUI:
    def __init__(self, master, dataframe):
        self.master = master
        self.master.title("Data Cleaner Interactive GUI")
        # Generic cleaning function
        self.data = dataframe
        
        # Initialize GUI elements
        self.init_ui()

    def init_ui(self):
        # Pixels of screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        # Frame for the treeview
        variable_frame = ttk.Frame(self.master)
        variable_frame.grid(row=0, column=0, sticky='ew')
        
        # Treeview for displaying the data
        self.tree = ttk.Treeview(variable_frame, columns=list(self.data.columns), show="headings")
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.grid(row=0, column=0, sticky='ew')
        
        # Scrollbar for the treeview
        scrollbar = ttk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.config(yscrollcommand=scrollbar.set)
        
        # Load data into the treeview
        self.load_data()
        
        # Frame for buttons
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=1, column=0, sticky='ew')
        
        
        # Buttons for actions
        ttk.Button(button_frame, text="Handle Missing Values", command=self.open_missing_value_handler).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Normalize Text", command=self.normalize_text).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Remove Duplicates", command=self.remove_duplicates).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT)
            
    def export_data(self):
        # Export the cleaned data to a CSV file
        name_iter = 1
        while f"cleaned_data{name_iter}.csv" in os.listdir():
            name_iter += 1
        self.data.to_csv(f"cleaned_data{name_iter}.csv", index=False)
        messagebox.showinfo("Info", f"Data exported to cleaned_data{name_iter}.csv.")

    def load_data(self):
        # Load data into the treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        for index, row in self.data.iterrows():
            self.tree.insert('', 'end', values=list(row))
        # Resize columns to fit the data
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=125)
            
    
    def remove_duplicates(self):
        # Remove duplicates and refresh the data display
        original_length = len(self.data)
        self.data.drop_duplicates(inplace=True)
        self.load_data()
        new_length = len(self.data)
        messagebox.showinfo("Info", f"Removed {original_length - new_length} duplicates.")
        
    def normalize_text(self):
        # Normalize text data in the dataframe
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                self.data[col] = self.data[col].str.lower()
                self.data[col] = self.data[col].str.strip()
        self.load_data()
        messagebox.showinfo("Info", "Normalized text data.")

    def open_missing_value_handler(self):
        # Open a new window to handle missing values
        self.mv_window = tk.Toplevel(self.master)
        self.mv_window.title("Handle Missing Values")
        
        tk.Label(self.mv_window, text="Select Column:").grid(row=0, column=0)
        
        # Dropdown to select the column
        columns_with_missing = [col for col in self.data.columns if self.data[col].isnull().any()]
        self.column_var = tk.StringVar(self.mv_window)
        self.column_var.set(columns_with_missing[0])  # default value
        column_menu = tk.OptionMenu(self.mv_window, self.column_var, *columns_with_missing)
        column_menu.grid(row=0, column=1)
        
        # Button to confirm column selection
        ttk.Button(self.mv_window, text="Confirm", command=self.display_missing_data).grid(row=0, column=2)

    def display_missing_data(self):
        # Display data from the selected column that has missing values
        selected_column = self.column_var.get()
        missing_data = self.data[self.data[selected_column].isnull()]
        
        # Clean up previous widgets
        for widget in self.mv_window.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()
        
        # Re-display the column selection
        tk.Label(self.mv_window, text="Select Column:").grid(row=0, column=0)
        column_menu = tk.OptionMenu(self.mv_window, self.column_var, *self.column_var.get())
        column_menu.grid(row=0, column=1)
        ttk.Button(self.mv_window, text="Confirm", command=self.display_missing_data).grid(row=0, column=2)

        # Display rows with missing values
        tk.Label(self.mv_window, text=f"Missing Data in {selected_column}:").grid(row=1, column=0, columnspan=3)
        text = tk.Text(self.mv_window, height=20, width=125)
        text.grid(row=2, column=0, columnspan=3)
        for index, row in missing_data.iterrows():
            text.insert(tk.END, str(row) + '\n')

        # Options for handling missing values
        ttk.Button(self.mv_window, text="Fill with Mean", command=lambda: self.fill_missing_values(selected_column, 'mean')).grid(row=3, column=0)
        ttk.Button(self.mv_window, text="Fill with Median", command=lambda: self.fill_missing_values(selected_column, 'median')).grid(row=3, column=1)
        ttk.Button(self.mv_window, text="Drop Rows", command=lambda: self.drop_rows_with_missing(selected_column)).grid(row=3, column=2)
        
    def fill_missing_values(self, column, method):
        if method == 'mean':
            fill_value = self.data[column].mean()
        elif method == 'median':
            fill_value = self.data[column].median()
        else:
            fill_value = self.data[column].mode()[0]
        self.data[column].fillna(fill_value, inplace=True)
        self.load_data()
        messagebox.showinfo("Info", f"Filled missing values in {column} with {method} ({fill_value}).")

    def drop_rows_with_missing(self, column):
        original_length = len(self.data)
        self.data.dropna(subset=[column], inplace=True)
        new_length = len(self.data)
        self.load_data()
        messagebox.showinfo("Info", f"Dropped {original_length - new_length} rows with missing values in {column}.")

if __name__ == '__main__':
    # Load data
    data = pd.read_csv('data.csv')
    
    # Create the main window
    root = tk.Tk()
    app = DataCleanerGUI(root, data)
    root.mainloop()