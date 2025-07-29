import os
import sys
import json
import uuid
import base64
import zipfile
import requests
from  pathlib import Path

from truffle.cli.shared import *
from truffle.cli.build import build
from truffle.common import get_logger
from truffle.cli.color_argparse import ColorArgParser
from truffle.platform.sdk_pb2 import AppUploadProgress

# good imports are always 1/x shaped

logger = get_logger()


def default_mainpy(proj_name : str) -> str:
    return str(r"""import truffle
import requests
from typing import Dict

class PROJECT_NAME:
    def __init__(self):
        # The client for using the SDK API
        # This allows you to perform LLM inference, text embeddings, ask the user for input, etc.
        self.client = truffle.TruffleClient()   

        # You can store state in your class, it will be saved between tool calls and by the backend to reload saved tasks!            
        self.notepad = ""


    # The icon is from Apple SF Symbols, you can find a full list here: https://hotpot.ai/free-icons
    @truffle.tool(description="A Hello World tool", icon="smiley")
    @truffle.args(example_str="The text to print after Hello World")   # Add descriptions to your arguments to help the model
    def HelloWorld(self, example_str: str) -> Dict[str, str]:  # You have to type annotate all arguments and the return type
        return { "response" : "Hello World " + example_str  }

    
    # You can call external APIs easily
    @truffle.tool("Returns a joke", icon="face-smile")
    def GetJoke(self, num_jokes : int) -> str:
        num_jokes = 1 if num_jokes < 1 else num_jokes
        response = requests.get(f"https://v2.jokeapi.dev/joke/Programming,Misc?format=txt&amount={num_jokes}")
        if response.status_code != 200:
            # Any logs or exceptions you raise are forwaded to the model and the client
            print("JokeAPI returned an error: ", response.status_code)
            raise ValueError("JokeAPI is down, try again later")   
        return response.content
    

    # An example of tools using state! You might want to use this to store things like API keys, or user preferences
    @truffle.tool("Take notes", icon="pencil")
    def TakeNote(self, note: str) -> str:
        self.notepad += note + "\n"
        return "Added note.\n Current notes: \n" + str(self.notepad)


    # We will use this function as a predicate for the ReadNotes tool
    # Predicates should take no arguments and return a boolean
    def _notes_exist(self) -> bool:
        return self.notepad != ""
    

    # This tool will only be visible to the model if _NotesExist returns True
    @truffle.tool("Read notes", icon="glasses", predicate=_notes_exist)
    @truffle.args(clear_after="Whether to clear notes after reading.")
    def ReadNotes(self, clear_after: bool) -> str:
        notes = self.notepad
        if clear_after is True:
            self.notepad = ""
        return "Current notes: \n" + str(notes)
    

    # Here we create an async tool, so the model can do other things while the tool is running
    @truffle.tool("Searches with Perplexity", icon="magnifying-glass")
    @truffle.args(query="The search query")
    @truffle.flags(nonblock=True)   # This will make the tool async 
    def AsyncPerplexitySearch(self, query: str) -> str:    
        self.client.tool_update("Searching perplexity...")  # Send an update to the client, will be displayed in the UI
        return self.client.perplexity_search(query=query, model="sonar-pro")    # SDK API provides free access to Perplexity!
    
    
    # You can add as many tools as you want to your app, just make sure they are all in the same class, and have the @truffle.tool decorator
    # Of course, you may also add any other methods you want to your class, they will not be exposed to the model but can be used in your tools
    # Any files in your project directory will be included in the bundle, so you can use them in your tools as well, use relative paths from main.py
        
    # Have fun building!

if __name__ == "__main__":
    truffle.run(PROJECT_NAME())
""").replace("PROJECT_NAME", proj_name)


def upload(path: Path):
    if not path.exists():
        logger.error(f"Path {path} does not exist, cannot upload")
        sys.exit(1)
    
    if path.is_dir():
        truffle_files = [f for f in os.listdir(path) if f.endswith('.truffle')]
        if not truffle_files:
            logger.warning("No .truffle file found in the directory, attempting build...")
            build(path, from_upload=True)
            print()
            upload(path) # this exists with 0, but just in case
            sys.exit(0)
        if len(truffle_files) > 1:
            logger.error("Multiple .truffle files found in the directory")
            sys.exit(1)
        path = path / truffle_files[0]
    elif path.is_file():
        if not path.suffix == '.truffle':
            logger.error("File does not have a .truffle extension")
            sys.exit(1)
        if not zipfile.is_zipfile(path):
            logger.error("File is not a valid zip archive")
            sys.exit(1)
    else:
        logger.error("Path is neither a directory nor a file") # is this possible?
        sys.exit(1)
    
    logger.info(f"Uploading project: {path}")

    def post_zip_and_log_sse(url : str, zip_path : Path, user_id : str) -> bool:
        headers = {'user_id': user_id}
        assert zip_path.exists(), f"path {zip_path} does not exist"
        assert zip_path.is_file(), f"path {zip_path} is not a file"
        assert zip_path.suffix == '.truffle', f"zip_path {zip_path} is not a truffle file"
        with open(zip_path, 'rb') as f:
            files = {'file': ( zip_path.stem, f, 'application/zip')}
            with requests.post(url + "/install", headers=headers, files=files, stream=True, timeout=120) as resp:
                if resp.status_code != 200: raise requests.exceptions.HTTPError(f"Error: {resp.status_code} {resp.text}")
                buffer = bytes()
                for line_bytes in resp.iter_lines(decode_unicode=False, chunk_size=1024):
                    line = line_bytes.decode('utf-8', errors='replace')
                    logger.debug(f"decode line: ''{line}''")
                    if not line:
                        if buffer:
                            try: #deserialize the event
                                event_bytes = buffer
                                prog = AppUploadProgress()
                                decoded = base64.b64decode(event_bytes)
                                while decoded.endswith(b'\0'): decoded = decoded[:-1] # remove trailing null bytes 
                                prog.ParseFromString(decoded)
                                
                                if prog.substep: logger.info(f"{prog.substep}")
                                if str(prog.error) != "": logger.error(f"Error: '{prog.error}'")
                                if prog.step == AppUploadProgress.UploadStep.STEP_INSTALLED: return True
    
                            except Exception as e:
                                # long logs still might cause a parsing error, will be fixed later
                                # assume you can keep reading on past the occasional bad msg until the connection closes/ network errors happen
                                # FIXME, just hiding for now, will be fixed later from fw
                                # logger.error(f"Error parsing event pb: {e}")
                                logger.debug(f"Caught error: {e}")
                                logger.debug(f"buffer: <<<\n{buffer}\n>>>")
                                logger.debug(f"line: <<<\n{buffer.decode('utf-8',errors='replace')}\n>>>")
                            buffer = bytes()
                        continue
                    
                    # basic SSE format is data: <data> \n\n (so \n\n delimiter and data: prefix)
                    # this is not a great way to parse this but for sake of example - dont copy paste it (what if I did)
                    if line.startswith('data:'): buffer += line_bytes[5:].lstrip()
                    if 'error:' in line: logger.error(f"Error: {line}")
        return False

    URL = get_base_url()
    user_id = get_user_id()
    logger.debug(f"Uploading to {URL} with user ID {user_id}")

    try:
        if(post_zip_and_log_sse(URL, path, user_id)):
            logger.success("Upload successful, check your client for installation errors and confirmation")
            sys.exit(0)
        else:
            logger.error("Upload failed, please try again")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Upload failed: unknown error: {e}")
        sys.exit(1)


def init_project(project : Path):
    if project.exists() and not project.is_dir():
            logger.error(f"Path {project} exists and is not a directory, cannot init")
            sys.exit(1)
    
    def alphanum_camel(string: str) -> str:
        return ''.join(w.capitalize() for w in string.split() if w.isalnum())

    def get_input(prompt : str, default : str = None, field : str = 'Input'):
        has_default = default is not None and len(default) > 0
        txt = logger.input(f"{prompt}: ") if not has_default else logger.input(f"{prompt} ({default}): ")
        if len(txt) > 0:
            return txt
        elif len(txt) == 0 and has_default:
            return default
        else:
            logger.error(f"{field} cannot be empty!")
            return get_input(prompt, default)
    
    logger.info("Provide some information about your project: ")
    proj_name = get_input(f"Name for your app", project.name, "App name")
    proj_desc = get_input("Description for your app", "Does app things", "App description")
    example_prompts = []
    logger.info("(optional) Provide some example prompts for your app: ")
    logger.info("These will be used for the automatic app selection feature, and can be edited in the manifest.json post-init")
    while True:
        msg = "Enter an example prompt for your app (or leave empty to finish): " if len(example_prompts) == 0 else "Enter another example prompt for your app (or leave empty to finish): "
        ex = logger.input(msg)
        if len(ex) == 0: break
        example_prompts.append(ex)
    
    print('')

    # If user runs in non empty dir, create a file with project name in CamelCase, increment number if dir exists
    # else if the dir is empty or doesn't exist then create the files there
    if project.exists() and any(project.iterdir()):
        for i in range(999):
            new_path = Path(project / (alphanum_camel(proj_name)+(str(i) if i>0 else '')))
            if not new_path.exists():
                project = new_path
                break
            i += 1
    project.mkdir(parents=True)

    for f in APP_FILES:
        if f == "icon.png":
            try:
                c = requests.get("https://pngimg.com/d/question_mark_PNG68.png")
                if c.status_code != 200: raise requests.HTTPError(c.status_code)
                with open(project / f, "wb") as icon: icon.write(c.content)
            except Exception as e:
                logger.error(f"Failed to download and create default icon: {e}")
                logger.warning("Creating a placeholder icon, please change it manually")
                (project / f).touch()
            logger.debug(f"-> Created default icon.png")
        elif f == "manifest.json":
            manifest = {
                "name": proj_name,
                "description": proj_desc,
                "example_prompts": example_prompts,
                "packages": [],
                "manifest_version": 1,
                "app_bundle_id" : str(uuid.uuid4()) # we can't just find your app by name, we need a unique identifier in case you change it! 
            }
            with open(project / f, "w") as mani:
                mani.write(json.dumps(manifest, indent=4, sort_keys=False, ensure_ascii=False))
            logger.debug(f"-> Created manifest.json with:\n {manifest}")
        elif f == "requirements.txt":
            with open(project / f, "w") as reqs: reqs.write("requests\n")
            logger.debug(f"-> Created requirements.txt")
        elif f == "main.py":
            class_name = alphanum_camel(proj_name)
            with open(project / f, "w") as main: main.write(default_mainpy(class_name))
            logger.debug(f"-> Created main.py with default content")
        else:
            (project / f).touch()

    logger.success(f"Initialized project in {project.resolve()}")
    try: rel_path = project.relative_to(Path.cwd())
    except ValueError: rel_path = project
    logger.info(f"You can now build your project with 'truffle build {rel_path}', and upload it with 'truffle upload {rel_path}'")
    sys.exit(0)


def cli():
    parser = ColorArgParser(prog="truffle", description="Truffle SDK CLI")
    subparsers = parser.add_subparsers(dest="action", description="the CLI action: upload / init / or build", required=True, help="The action to perform")
    
    def add_subcommand(name: str, help: str):
        p = subparsers.add_parser(name, help=help)
        p.add_argument("path", help="The path to the project", nargs="?", default=os.getcwd())
    
    actions = {
         "upload" : {"help": "Upload the project to the cloud", "fn": upload},
         "init" : {"help": "Initialize a new project", "fn": init_project},
         "build" : {"help": "Build the project", "fn": build},
    }

    for name, args in actions.items():
        add_subcommand(name, args["help"])

    args = parser.parse_args()
    if not args.action or args.action not in actions:
        parser.print_help()
        logger.error(f"\t-> please provide one of the following actions: {', '.join(actions.keys())}")
        sys.exit(1)
    
    cmd = actions[args.action]
    cmd["fn"](Path(args.path).resolve()) # resolve() fixes . as an arg
    

def main():
    cli()

if __name__ == "__main__":
    main()
