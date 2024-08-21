"""
file_storage.py

This module provides a class to store, retrieve, and delete PDF files in a MongoDB database using GridFS.
"""
import gridfs


class PDFStorageInterface:
    """
    A class to interact with PDF files in a MongoDB database using GridFS.

    This class provides methods to store, retrieve, and delete PDF files in a MongoDB database using GridFS.
    It requires a MongoDB database object to be passed during initialization.

    Attributes:
        db (Database): The MongoDB database object used for storing PDF files.
        fs (GridFS): The GridFS object for handling file storage.

    Methods:
        retrieve_pdfs(pdf_names: list[str]) -> list[bytes] | None:
            Retrieves multiple PDF files by their names.

        store_pdf(pdf_path: str, pdf_name: str) -> None:
            Stores a single PDF file.

        bulk_insert_pdf(files_list: list[tuple[str, str]]) -> None:
            Stores multiple PDF files.

        delete_pdf(pdf_name: str) -> None:
            Deletes a PDF file by its name.

        retrieve_all_pdfs() -> tuple[list[str], list[bytes]]:
            Retrieves all PDF files.
    """

    def __init__(self, db):
        """
        Initializes the PDFStorageInterface with a MongoDB database object.

        Args:
            db (Database): The MongoDB database object used for storing PDF files.
        """
        self.db = db
        self.fs = gridfs.GridFS(db)

    def retrieve_pdfs(self, pdf_names: list[str]) -> list[bytes] | None:
        """
        Retrieve multiple PDF files from the MongoDB database.

        Args:
            pdf_names (list[str]): List of PDF file names to retrieve.

        Returns:
            list[bytes] | None: List of PDF file contents in bytes if found, otherwise None.
        """
        data = []
        for pdf_name in pdf_names:
            # Retrieve the file from GridFS
            file_data = self.fs.find_one({'filename': pdf_name})

            if file_data:
                # Read the file data into memory
                pdf_content = file_data.read()
                print(f"Retrieved PDF file '{pdf_name}' successfully.")
                data.append(pdf_content)
            else:
                print(f"PDF file '{pdf_name}' not found in the database.")
                return None
        return data

    def store_pdf_chunk(self, pdf_name: str, pdf_chunk: bytes) -> None:
        """
        Store a single PDF chunk in the MongoDB database using GridFS.

        Args:
            pdf_chunk (bytes): Content of the PDF chunk to store.
            pdf_name (str): Name to assign to the stored PDF chunk.
        """
        self.db.fs.files.create_index([('filename', 1)], unique=True)
        self.fs.put(pdf_chunk, filename=pdf_name)
        print(f"Stored PDF chunk '{pdf_name}' successfully.")

    def delete_pdf(self, pdf_name: str) -> None:
        """
        Delete a PDF file from the MongoDB database using GridFS.

        Args:
            pdf_name (str): Name of the PDF file to delete.
        """
        # Find the file in GridFS
        file_data = self.fs.find_one({'filename': pdf_name})

        if file_data:
            # Delete the file using its _id
            self.fs.delete(file_data._id)
            print(f"Deleted PDF file '{pdf_name}' successfully.")
        else:
            print(f"PDF file '{pdf_name}' not found in the database.")

    def retrieve_all_pdfs(self) -> tuple[list[str], list[bytes]]:
        """
        Retrieve all PDF files from the MongoDB database using GridFS.

        Returns:
            tuple[list[str], list[bytes]]: A tuple containing a list of filenames and their corresponding file contents.
        """
        filenames = []
        file_data = []
        # Find all files in the fs.files collection
        for grid_out in self.fs.find():
            filename = grid_out.filename
            filenames.append(filename)
            file_data.append(grid_out.read())
        return filenames, file_data


# Example usage:
if __name__ == "__main__":
    from utils import setup_mongo_db

    datab = setup_mongo_db()
    pdf_storage_interface = PDFStorageInterface(datab)
    print(pdf_storage_interface.retrieve_pdfs(['autism_handbook']))
    pdf_storage_interface.delete_pdf('autism_handbook')
    print(pdf_storage_interface.retrieve_all_pdfs())
