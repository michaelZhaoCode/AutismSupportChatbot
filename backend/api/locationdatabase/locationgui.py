import tkinter as tk
from tkinter import ttk
from sqlitelocationdatabase import SQLiteLocationDatabase

class LocationGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Location Mode GUI")
        self.geometry("800x900")

        # Initialize the database
        self.database = SQLiteLocationDatabase()

        # Create frames for different parts of the GUI
        self.create_main_switch_buttons()
        self.create_list_frame()
        self.create_mode_buttons()
        self.create_dynamic_content_frame()

        # Start in Region Mode
        self.switch_to_region()

    def create_main_switch_buttons(self):
        """Create top buttons to switch between Region and Service views."""
        self.switch_frame = ttk.Frame(self)
        self.switch_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        region_button = ttk.Button(self.switch_frame, text="Region", command=self.switch_to_region)
        region_button.pack(side=tk.LEFT, padx=5)

        service_button = ttk.Button(self.switch_frame, text="Service", command=self.switch_to_service)
        service_button.pack(side=tk.LEFT, padx=5)

    def create_list_frame(self):
        """Create a frame for displaying lists of regions or services."""
        self.list_frame = ttk.LabelFrame(self, text="Available Items")
        self.list_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Create a canvas and scrollbar for scrolling the list
        self.canvas = tk.Canvas(self.list_frame)
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.list_var = tk.IntVar()

    def create_mode_buttons(self):
        """Create buttons for different modes."""
        self.mode_frame = ttk.Frame(self)
        self.mode_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    def create_dynamic_content_frame(self):
        """Create a frame for dynamic content display based on the selected mode."""
        self.content_frame = ttk.LabelFrame(self, text="Options")
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)

    def switch_to_region(self):
        """Switch the interface to display regions."""
        self.clear_list_frame()
        self.clear_mode_buttons()

        # Set region-specific modes (1-3)
        modes = ["Insert Region", "Delete Region", "Mode 3"]
        for mode in modes:
            button = ttk.Button(self.mode_frame, text=mode, command=lambda m=mode: self.switch_mode(m))
            button.pack(side=tk.LEFT, padx=5)

        # Load the regions list
        self.load_regions()

    def switch_to_service(self):
        """Switch the interface to display services."""
        self.clear_list_frame()
        self.clear_mode_buttons()

        # Set service-specific modes
        modes = ["Insert Service", "Delete Service", "Mode 6"]
        for mode in modes:
            button = ttk.Button(self.mode_frame, text=mode, command=lambda m=mode: self.switch_mode(m))
            button.pack(side=tk.LEFT, padx=5)

        # Load the services list
        self.load_services()

    def load_regions(self):
        """Load regions from the database and display them as radio buttons."""
        regions = self.database.find_all_regions()

        self.style = ttk.Style(self)
        self.style.configure(
            "Monospace.TRadiobutton",
            font=("Courier", 10)  # Use "Courier" as a monospaced font
        )

        for region in regions:
            region_info = (
                f"{region['RegionID']}.".ljust(6) +
                f"{region['RegionType']}:".ljust(12) +
                f"{region['RegionName']}".ljust(20) +
                f"Parent: {region['ParentRegionID']}".ljust(16) +
                f"Lat: {region['Latitude']}, ".ljust(14) +
                f"Lon: {region['Longitude']}"
            )

            radio_button = ttk.Radiobutton(
                self.scrollable_frame,
                text=region_info,
                variable=self.list_var,
                value=region["RegionID"],
                style="Monospace.TRadiobutton"
            )
            radio_button.pack(anchor="w", padx=10, pady=2)

    def load_services(self):
        """Load services from the database and display them as radio buttons."""
        services = self.database.find_all_services()

        self.style = ttk.Style(self)
        self.style.configure(
            "Monospace.TRadiobutton",
            font=("Courier", 10)
        )

        for service in services:
            service_info = (
                f"{service['ServiceID']}.".ljust(6) +
                f"{service['ServiceType']}:".ljust(12) +
                f"{service['ServiceName']}".ljust(20) +
                f"Region: {service['RegionID']}".ljust(10) +
                f"Lat: {service['Latitude']}, ".ljust(14) +
                f"Lon: {service['Longitude']} ".ljust(14) +
                f"Address: {service['Address'] or 'N/A'} ".ljust(30) +
                f"Phone: {service['Phone'] or 'N/A'} ".ljust(20) +
                f"Website: {service['Website'] or 'N/A'}"
            )

            radio_button = ttk.Radiobutton(
                self.scrollable_frame,
                text=service_info,
                variable=self.list_var,
                value=service["ServiceID"],
                style="Monospace.TRadiobutton"
            )
            radio_button.pack(anchor="w", padx=10, pady=2)

    def clear_list_frame(self):
        """Clear the list frame for reloading regions or services."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def clear_mode_buttons(self):
        """Clear the mode buttons frame."""
        for widget in self.mode_frame.winfo_children():
            widget.destroy()

    def clear_dynamic_content(self):
        """Clear the dynamic content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def switch_mode(self, mode):
        """Clear dynamic content frame and prepare for the new mode setup."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if mode == "Insert Region":
            self.insert_region_mode()
        elif mode == "Delete Region":
            self.delete_region_mode()
        elif mode == "Insert Service":
            self.insert_service_mode()
        elif mode == "Delete Service":
            self.delete_service_mode()

    def insert_region_mode(self):
        """Display fields for inserting a new region."""
        tk.Label(self.content_frame, text="Insert New Region").pack(pady=5)

        # Region name
        tk.Label(self.content_frame, text="Region Name:").pack(anchor="w", padx=5, pady=2)
        region_name_entry = ttk.Entry(self.content_frame)
        region_name_entry.pack(fill=tk.X, padx=5, pady=2)

        # Region type
        tk.Label(self.content_frame, text="Region Type:").pack(anchor="w", padx=5, pady=2)
        region_type_entry = ttk.Entry(self.content_frame)
        region_type_entry.pack(fill=tk.X, padx=5, pady=2)

        # Parent ID
        tk.Label(self.content_frame, text="Parent ID:").pack(anchor="w", padx=5, pady=2)
        parent_id_entry = ttk.Entry(self.content_frame)
        parent_id_entry.pack(fill=tk.X, padx=5, pady=2)

        # Latitude
        tk.Label(self.content_frame, text="Latitude:").pack(anchor="w", padx=5, pady=2)
        latitude_entry = ttk.Entry(self.content_frame)
        latitude_entry.pack(fill=tk.X, padx=5, pady=2)

        # Longitude
        tk.Label(self.content_frame, text="Longitude:").pack(anchor="w", padx=5, pady=2)
        longitude_entry = ttk.Entry(self.content_frame)
        longitude_entry.pack(fill=tk.X, padx=5, pady=2)

        # Submit button
        submit_button = ttk.Button(
            self.content_frame,
            text="Insert Region",
            command=lambda: self.submit_region(
                region_name_entry.get(),
                region_type_entry.get(),
                parent_id_entry.get(),
                latitude_entry.get(),
                longitude_entry.get()
            )
        )
        submit_button.pack(pady=10)

    def submit_region(self, name, region_type, parent_id, latitude, longitude):
        """Attempt to insert a new region into the database."""
        try:
            parent_id = int(parent_id) if parent_id else None
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            self.display_message("Invalid input! Ensure numeric values are correctly entered.")
            return

        # Call the database method to insert the new region
        success = self.database.insert_region(name, region_type, parent_id, latitude, longitude)

        if success:
            self.add_region_to_list(name, region_type, parent_id, latitude, longitude)
        else:
            self.display_message("Failed to insert region. Please try again.")

    def add_region_to_list(self, name, region_type, parent_id, latitude, longitude):
        """Add a new region to the displayed list of regions."""
        new_region_id = "NEW"

        region_info = (
            f"{new_region_id}.".ljust(6) +
            f"{region_type}:".ljust(12) +
            f"{name}".ljust(20) +
            f"Parent: {parent_id}".ljust(16) +
            f"Lat: {latitude}, ".ljust(14) +
            f"Lon: {longitude}"
        )

        radio_button = ttk.Radiobutton(
            self.scrollable_frame,
            text=region_info,
            variable=self.list_var,
            value=new_region_id,
            style="Monospace.TRadiobutton"
        )
        radio_button.pack(anchor="w", padx=10, pady=2)

    def display_message(self, message):
        """Display an error message in the dynamic content area."""
        error_label = tk.Label(self.content_frame, text=message, fg="red")
        error_label.pack(pady=5)

    def delete_region_mode(self):
        """Update the dynamic content frame to show the Delete button."""
        self.clear_dynamic_content()

        delete_button = ttk.Button(
            self.content_frame,
            text="Delete",
            command=self.delete_region
        )
        delete_button.pack(pady=10)

    def delete_region(self):
        """Attempt to delete the selected region."""
        selected_region_id = self.list_var.get()

        if selected_region_id == 0:
            self.display_message("No region selected. Please select a region to delete.")
            return

        # Call the database method to remove the region
        success = self.database.remove_region(selected_region_id)

        if success:
            # Find and remove the radio button corresponding to the deleted region
            for widget in self.scrollable_frame.winfo_children():
                # Get the radio button's value (region ID)
                region_id = widget.cget("value")

                # Get the radio button's text to check for parent ID
                region_text = widget.cget("text")

                # Check if the radio button corresponds to the deleted region or its parent
                if region_id == selected_region_id or f"Parent: {selected_region_id} " in region_text:
                    widget.destroy()

            self.display_message("Region deleted successfully.")
        else:
            self.display_message("Failed to delete region. Please try again.")

    def insert_service_mode(self):
        """Display fields for inserting a new service."""
        tk.Label(self.content_frame, text="Insert New Service").pack(pady=5)

        # Service name
        tk.Label(self.content_frame, text="Service Name:").pack(anchor="w", padx=5, pady=2)
        service_name_entry = ttk.Entry(self.content_frame)
        service_name_entry.pack(fill=tk.X, padx=5, pady=2)

        # Service type
        tk.Label(self.content_frame, text="Service Type:").pack(anchor="w", padx=5, pady=2)
        service_type_entry = ttk.Entry(self.content_frame)
        service_type_entry.pack(fill=tk.X, padx=5, pady=2)

        # Region ID
        tk.Label(self.content_frame, text="Region ID:").pack(anchor="w", padx=5, pady=2)
        region_id_entry = ttk.Entry(self.content_frame)
        region_id_entry.pack(fill=tk.X, padx=5, pady=2)

        # Latitude
        tk.Label(self.content_frame, text="Latitude:").pack(anchor="w", padx=5, pady=2)
        latitude_entry = ttk.Entry(self.content_frame)
        latitude_entry.pack(fill=tk.X, padx=5, pady=2)

        # Longitude
        tk.Label(self.content_frame, text="Longitude:").pack(anchor="w", padx=5, pady=2)
        longitude_entry = ttk.Entry(self.content_frame)
        longitude_entry.pack(fill=tk.X, padx=5, pady=2)

        # Address
        tk.Label(self.content_frame, text="Address (Optional):").pack(anchor="w", padx=5, pady=2)
        address_entry = ttk.Entry(self.content_frame)
        address_entry.pack(fill=tk.X, padx=5, pady=2)

        # Phone
        tk.Label(self.content_frame, text="Phone (Optional):").pack(anchor="w", padx=5, pady=2)
        phone_entry = ttk.Entry(self.content_frame)
        phone_entry.pack(fill=tk.X, padx=5, pady=2)

        # Website
        tk.Label(self.content_frame, text="Website (Optional):").pack(anchor="w", padx=5, pady=2)
        website_entry = ttk.Entry(self.content_frame)
        website_entry.pack(fill=tk.X, padx=5, pady=2)

        # Submit button
        submit_button = ttk.Button(
            self.content_frame,
            text="Insert Service",
            command=lambda: self.submit_service(
                service_name_entry.get(),
                service_type_entry.get(),
                region_id_entry.get(),
                latitude_entry.get(),
                longitude_entry.get(),
                address_entry.get(),
                phone_entry.get(),
                website_entry.get()
            )
        )
        submit_button.pack(pady=10)

    def submit_service(self, service, service_type, region_id, latitude, longitude, address, phone, website):
        """Attempt to insert a new service into the database."""
        try:
            region_id = int(region_id)
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            self.display_message("Invalid input! Ensure numeric values are correctly entered.")
            return

        # Call the database method to insert the new service
        success = self.database.insert_service(service, service_type, region_id, latitude, longitude, address, phone,
                                               website)

        if success:
            self.add_service_to_list(service, service_type, region_id, latitude, longitude, address, phone, website)
        else:
            self.display_message("Failed to insert service. Please try again.")

    def add_service_to_list(self, service, service_type, region_id, latitude, longitude, address, phone, website):
        """Add a new service to the displayed list of services."""
        new_service_id = "NEW"

        service_info = (
                f"{new_service_id}.".ljust(6) +
                f"{service_type}:".ljust(12) +
                f"{service}".ljust(20) +
                f"Region: {region_id}".ljust(10) +
                f"Lat: {latitude}, ".ljust(14) +
                f"Lon: {longitude} ".ljust(14) +
                f"Address: {address or 'N/A'} ".ljust(30) +
                f"Phone: {phone or 'N/A'} ".ljust(20) +
                f"Website: {website or 'N/A'}"
        )

        radio_button = ttk.Radiobutton(
            self.scrollable_frame,
            text=service_info,
            variable=self.list_var,
            value=new_service_id,
            style="Monospace.TRadiobutton"
        )
        radio_button.pack(anchor="w", padx=10, pady=2)

    def delete_service_mode(self):
        """Update the dynamic content frame to show the Delete Service button."""
        tk.Label(self.content_frame, text="Delete Selected Service").pack(pady=5)

        delete_button = ttk.Button(
            self.content_frame,
            text="Delete",
            command=self.delete_service
        )
        delete_button.pack(pady=10)

    def delete_service(self):
        """Attempt to delete the selected service."""
        selected_service_id = self.list_var.get()

        if selected_service_id == 0:
            self.display_message("No service selected. Please select a service to delete.")
            return

        # Call the database method to remove the service
        success = self.database.remove_service(selected_service_id)

        if success:
            # Find and remove the radio button corresponding to the deleted service
            for widget in self.scrollable_frame.winfo_children():
                service_id = widget.cget("value")

                if service_id == selected_service_id:
                    widget.destroy()
                    break

            self.display_message("Service deleted successfully.")
        else:
            self.display_message("Failed to delete service. Please try again.")


if __name__ == "__main__":
    app = LocationGUI()
    app.mainloop()
