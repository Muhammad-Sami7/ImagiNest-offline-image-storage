# 🧠ImagiNest  
Offline Image Storage and Metadata Management Application using CouchDB

## Overview
ImagiNest is a desktop-based, offline image storage and metadata management application designed for structured image archiving. Built with Python, PyQt5, and CouchDB, the system enables users to store images along with rich, well-defined metadata in a fully local environment.

The application provides a structured approach to storing images and metadata in an offline environment.

---

## Motivation
Managing large collections of images often requires more than simple file storage. ImagiNest addresses this by:
- Enforcing structured metadata at upload time
- Eliminating naming conflicts through deterministic filename generation
- Providing a clean, user-friendly interface for repeated data entry
- Operating entirely offline for reliability and privacy

---

## Key Features
- Fully offline image storage using local CouchDB  
- Upload images with structured metadata (type, resolution, class)  
- Autocomplete-enabled metadata fields for fast and consistent input  
- Automatic generation of unique, informative filenames  
- Stores both image files and metadata as CouchDB documents  
- Clean and modern desktop interface built with PyQt5  
- Automatic form reset after successful upload  
- Designed for repeated, high-volume image uploads  

---

## Image Naming Strategy
Each image is stored using a deterministic and collision-free naming scheme derived from its metadata and upload time:

### Benefits
- Prevents duplicate filenames  
- Encodes metadata directly into the filename  
- Simplifies dataset inspection and debugging  
- Ensures long-term traceability of stored images
