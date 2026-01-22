from flask import render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename as w_secure_filename
import magic, uuid, markdown, bleach



class File_Security:
    @staticmethod
    def check_image_extension(filename):
        ALLOWED_EXTENSIONS = {"png", "webp", "jpeg", "jpg", "gif"}
        extension = filename.rsplit(".", 1)[-1].lower()
        if "." not in filename:
            raise ValueError("File has no extension.")
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("Image file type not supported. Please try again.")
        # If the filename is valid, do nothing.


    @staticmethod
    def check_image_size(file_size):
        MAX_FILE_UPLOAD_SIZE = 5 * 1024 ** 2 # - 5 MB size limit
        if file_size > MAX_FILE_UPLOAD_SIZE:
            raise ValueError("File exceeds 5 MB. Please try again.")

    @staticmethod
    def check_image_type(file):
        ALLOWED_TYPES = ["image/png", "image/webp", "image/jpeg", "image/gif"] 
        # Check magic bytes of file and obtain file type
        file_type = magic.from_buffer(file, mime = True)
        if file_type not in ALLOWED_TYPES:
            raise ValueError("File type not valid. Please try again")
        
    @staticmethod
    def generate_secure_image_name(original_filename):
        # Sanitisation
        sanitised_filename = w_secure_filename(original_filename)
        # Extract extension
        if "." not in sanitised_filename:
            raise ValueError("Invalid filename.")
        extension = sanitised_filename.rsplit(".", 1)[-1].lower()
        # Generate new UUID file name
        secure_filename = f"{uuid.uuid4().hex}.{extension}"
        return secure_filename
    
class Data_Security:
    @staticmethod
    def sanitise_text_to_markdown(text):
        """ Sanitising comment and converting it to markdown format"""
        html_output = markdown.markdown(text)
        ALLOWED_TAGS = ['p','b','i','em','br','li','ol','ul','strong','em','h1','h2','h3']
        ALLOWED_ATTRIBUTES = {}
        cleaned_text = bleach.clean(
            html_output,
            tags = ALLOWED_TAGS,
            attributes = ALLOWED_ATTRIBUTES,
            strip = True
        )
        return cleaned_text