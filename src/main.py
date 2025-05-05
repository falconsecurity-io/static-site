import os
import shutil

from copystatic import copy_files_recursive
from gencontent import generate_page

dir_path_static = "./static"
dir_path_public = "./public"
dir_path_content = "./content"
template_path = "./template.html"


def generate_all_pages(content_dir, template_path, public_dir):
    for root, _, files in os.walk(content_dir):
        for file in files:
            if file.endswith(".md"):
                md_path = os.path.join(root, file)
                
                # Determine relative path and new .html filename
                rel_path = os.path.relpath(md_path, content_dir)
                html_filename = os.path.splitext(rel_path)[0] + ".html"
                dest_path = os.path.join(public_dir, html_filename)

                # Create destination directory if needed
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                print(f"Generating page from {md_path} to {dest_path}")
                generate_page(md_path, template_path, dest_path)

def main():
    print("Deleting public directory...")
    if os.path.exists(dir_path_public):
        shutil.rmtree(dir_path_public)

    print("Copying static files to public directory...")
    copy_files_recursive(dir_path_static, dir_path_public)

    print("Generating pages...")
    generate_all_pages(dir_path_content, template_path, dir_path_public)



main()
