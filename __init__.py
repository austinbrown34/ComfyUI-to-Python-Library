import sys
import os

from io import StringIO

import traceback
import io

from aiohttp import web

ext_dir = os.path.dirname(__file__)
sys.path.append(ext_dir)

try:
    import black
except ImportError:
    print("Unable to import requirements for ComfyUI-SaveAsScript.")
    print("Installing...")

    import importlib

    spec = importlib.util.spec_from_file_location(
        "impact_install", os.path.join(os.path.dirname(__file__), "install.py")
    )
    impact_install = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(impact_install)

    print("Successfully installed. Hopefully, at least.")

# Prevent reimporting of custom nodes
os.environ["RUNNING_IN_COMFYUI"] = "TRUE"

from comfyui_to_python import ComfyUItoPython

sys.path.append(os.path.dirname(os.path.dirname(ext_dir)))

import server

WEB_DIRECTORY = "js"
NODE_CLASS_MAPPINGS = {}


@server.PromptServer.instance.routes.post("/saveasscript")
async def save_as_script(request):
    try:
        data = await request.json()
        name = data["name"]
        workflow = data["workflow"]

        sio = StringIO()
        ComfyUItoPython(workflow=workflow, output_file=sio)

        sio.seek(0)
        data = sio.read()

        return web.Response(text=data, status=200)
    except Exception as e:
        traceback.print_exc()
        return web.Response(text=str(e), status=500)

import tempfile
import shutil
import zipfile

@server.PromptServer.instance.routes.post("/saveaslibrary")
async def save_as_library(request):
    try:
        data = await request.json()
        name = data["name"]
        
        # We don't need destination anymore, we'll use a temp dir
        workflow = data["workflow"]

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            from comfyui_to_python import ComfyUItoLibrary
            # Generate the library in the temp directory
            ComfyUItoLibrary(workflow=workflow, library_name=name, destination_path=temp_dir)
            
            # The library is now at os.path.join(temp_dir, name)
            lib_path = os.path.join(temp_dir, name)
            
            # Create a zip file in memory
            sio = StringIO()
            # We need bytes for zip file
            bio = io.BytesIO()
            
            # Create a zip file from the directory
            shutil.make_archive(os.path.join(temp_dir, name), 'zip', lib_path)
            
            # Read the zip file back
            zip_path = os.path.join(temp_dir, name + ".zip")
            with open(zip_path, "rb") as f:
                zip_data = f.read()

            return web.Response(
                body=zip_data, 
                status=200,
                headers={
                    "Content-Type": "application/zip",
                    "Content-Disposition": f"attachment; filename={name}.zip"
                }
            )
    except Exception as e:
        traceback.print_exc()
        return web.Response(text=str(e), status=500)
