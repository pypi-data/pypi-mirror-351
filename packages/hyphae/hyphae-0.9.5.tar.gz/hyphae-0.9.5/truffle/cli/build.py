import ast
import sys
import json
import zipfile
import importlib
import sysconfig
from pathlib import Path

from truffle.cli.shared import *
from truffle.common import get_logger

logger = get_logger()


def _get_png_dimensions(file_path):
    with open(file_path, "rb") as f:
        signature = f.read(8)  
        if signature != b"\x89PNG\r\n\x1a\n":
            raise ValueError("Not a valid PNG file: " + file_path)
        f.read(4) 
        if f.read(4) != b"IHDR":
            raise ValueError("Invalid PNG structure: header not found in " + file_path)

        width = int.from_bytes(f.read(4), "big")
        height = int.from_bytes(f.read(4), "big")
        return width, height

def _check_file(p : Path):
    name = p.name
    if name == "manifest.json":
        manifest = json.loads(p.read_text())
        required_keys = [
            'name', 'description', 'app_bundle_id', 'manifest_version'
        ]
        for key in required_keys:
            if key not in manifest:
                logger.error(f"Missing key {key} in manifest.json")
                sys.exit(1)
        # if 'developer_id' not in manifest: manifest['developer_id'] = get_user_id()
        if 'example_prompts' not in manifest or len(manifest['example_prompts']) == 0:
            logger.warning("No example prompts found in manifest.json, auto-selection performance may be poor")
    elif name == "requirements.txt":
        reqs = p.read_text().strip().split("\n")
        if len(reqs) == 0:
            logger.error("Empty/unparseable requirements.txt file")
            sys.exit(1)
    elif name == "main.py":
        main_text = p.read_text()
        if main_text.find("import truffle") == -1:
            logger.error("Missing import truffle in main.py")
            sys.exit(1)
        
        if main_text.find("class") == -1:
            logger.error("Missing class definition in main.py")
            sys.exit(1)
        
    elif name == "icon.png":
        try:
            w, h = _get_png_dimensions(p)
            MIN_ICON_SIZE = 128
            if w < MIN_ICON_SIZE or h < MIN_ICON_SIZE:
                logger.error(f"Invalid icon.png size: {w}x{h} - must be more than {MIN_ICON_SIZE}x{MIN_ICON_SIZE}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Invalid icon.png file: {e}")
            sys.exit(1)
    else:
        logger.error(f"Unknown file: {p}")
        sys.exit(1)
    logger.debug(f"Checked {p} - OK")

def _must_exist(p : Path):
    if not p.exists() or not p.is_file():
        logger.error(f"Missing file: {p} - invalid project")
        sys.exit(1)
    if p.stat().st_size == 0:
        logger.error(f"Empty file: {p} - invalid project")
        if p.name == "requirements.txt":
            logger.warning("if a requirements.txt file is not needed, please remove it")
        sys.exit(1)
    _check_file(p)

def _check_syntax_and_decorators(path: Path):
    src = path.read_text()
    # check syntax
    try: tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        logger.error(f"SyntaxError in {e.filename}, line {e.lineno}: {e.msg}")
        return False

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for deco in node.decorator_list:
                lineno = getattr(deco, "lineno", "?")

                # pull out the actual decorator name whether it's @mod.attr or @mod.attr(...)
                # will add checks for arguments later
                if isinstance(deco, ast.Call): func = deco.func
                else: func = deco

                # func should be an ast.Attribute if it's mod.attr
                if not isinstance(func, ast.Attribute): continue

                # ensure the “mod” side is a simple Name (e.g. “truffle”)
                if not isinstance(func.value, ast.Name): continue

                mod_name  = func.value.id
                attr_name = func.attr

                # try importing and hasattr
                try: module = importlib.import_module(mod_name)
                except ImportError:
                    logger.error(
                        f"ImportError: module '{mod_name}' not found "
                        f"(in decorator on '{node.name}', line {lineno})"
                    )
                    return False
                else:
                    if not hasattr(module, attr_name):
                        logger.error(
                            f"AttributeError: module '{mod_name}' has no "
                            f"attribute '{attr_name}' (in decorator on '{node.name}', line {lineno})"
                        )
                        return False            
    return True

def _load_requirements_pkgs(req_path: Path):
    pkgs = set()
    for line in req_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        # strip off version specifiers
        name = line.split(";", 1)[0] # drop env markers
        name = name.split("==", 1)[0]
        name = name.split(">=", 1)[0]
        name = name.split("<=", 1)[0]
        name = name.split("!=", 1)[0]
        name = name.split("~=", 1)[0]
        name = name.split(">", 1)[0]
        name = name.split("<", 1)[0]
        pkgs.add(name.strip().lower())
    return pkgs

def _check_imports(path: Path, reqs_path: Path):
    src = path.read_text()
    try: tree = ast.parse(src, filename=str(path))
    except SyntaxError as e: 
        logger.error(f"SyntaxError when parsing imports: {e.msg} (line {e.lineno})")
        return False
    required_pkgs = _load_requirements_pkgs(reqs_path)
    stdlib_dir = sysconfig.get_paths()["stdlib"]
    seen = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names: seen.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module: seen.add(node.module.split(".", 1)[0])

    for mod in sorted(seen):
        spec = importlib.util.find_spec(mod)
        if spec is None and mod not in BANNED_REQS:
            logger.error(f"Module not found at all: '{mod}'")
            return False

        origin = spec.origin or ""
        if origin == "built-in": continue
        if origin.startswith(stdlib_dir): continue
        # third-party → must be in requirements.txt
        if mod.lower() not in required_pkgs and mod.lower() not in BANNED_REQS:
            logger.error(f"Third-party module '{mod}' not listed in requirements.txt")
            return False
        logger.debug(f"-> found requirement '{mod}' - OK")

    for r in required_pkgs:
        if r.lower() in BANNED_REQS:
            logger.error(f"Do not include '{r}' in requirements.txt")
            return False

    return True


def _looks_like_venv(builddir: Path, dirname: str) -> bool:
    venv_path = builddir / dirname
    if not venv_path.is_dir(): return False
    markers = [
        venv_path / 'pyvenv.cfg',
        venv_path / 'bin' / 'activate',
        venv_path / 'bin' / 'activate.fish',
        venv_path / 'bin' / 'activate.csh',
        venv_path / 'Scripts' / 'activate.bat'
    ]
    return any(marker.exists() for marker in markers)

def _make_zip(builddir: Path, dst_file: Path):
    blacklist_files = ['.DS_Store', '.gitignore']
    blacklist_dirs = ['__pycache__', '.git']
    assert builddir.exists() and builddir.is_dir(), f"Invalid source directory: {builddir}"
    assert dst_file.suffix == ".truffle", f"Invalid destination file: {dst_file}"
    with zipfile.ZipFile(dst_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(builddir):
            original_dirs = list(dirs)
            dirs[:] = [d for d in dirs if d not in blacklist_dirs and not _looks_like_venv(builddir, d)]
            for d in original_dirs:
                if d not in dirs:
                    logger.warning(f"Skipping directory '{d}', matches blacklist or venv pattern")
            zipf.write(root, arcname=os.path.join(builddir.name, os.path.relpath(root, builddir)))
            for file in files:
                if file.endswith('.truffle'): continue
                if file in blacklist_files: continue
                file_path = os.path.join(root, file)
                arcname = os.path.join(builddir.name, os.path.relpath(file_path, builddir))
                zipf.write(file_path, arcname)
                logger.debug(f"Added file to zip: {arcname}")
    bundle_size = dst_file.stat().st_size
    if bundle_size > 10 * 1024 * 1024:
        logger.error(f"Bundle size too large ({bundle_size/(1024 * 1024):.2f} MB > 10 MB), consider deleting some files")
        dst_file.unlink()
        return None
    return dst_file

def build(builddir: Path, from_upload: bool = False):
    if not builddir.exists():
        logger.error(f"Path {builddir} does not exist - cannot build")
        sys.exit(1)
    if not builddir.is_dir():
        logger.error("Path is not a directory, please provide a directory to build")
        sys.exit(1)

    for f in APP_FILES:
        _must_exist(builddir / f)

    for file in builddir.iterdir():
        try:
            if file.is_file() and not file.name.endswith(".truffle"):
                size = file.stat().st_size
                if size > (1024 * 1024 * 10): 
                    logger.error(f"Unexpectedly large file {file}, did you mean to include this?")
                    sys.exit(1)
        except Exception as e: continue
    
    main_path = builddir / "main.py"
    reqs_txt_path = builddir / "requirements.txt"

    if not os.getenv("TRUFFLE_SKIP_VALIDATE"):
        # check if truffle.run() exists
        inst_code = None
        for node in ast.walk(ast.parse(main_path.read_text())):
            if isinstance(node, ast.Call):
                func = node.func
                if (
                    isinstance(func, ast.Attribute) and func.attr == "run" and
                    isinstance(func.value, ast.Name) and func.value.id == "truffle"
                ):
                    inst_code = ast.get_source_segment(main_path.read_text(), node)
                    break
        if not inst_code:
            logger.error("Unable to find truffle.run(...) in main.py")
            sys.exit(1)

        # check for syntax and decorators
        logger.info("Checking main.py for syntax + decorators")
        if not _check_syntax_and_decorators(main_path):
            logger.error("Found errors, aborting.")
            exit(1)
        else: logger.success("No syntax or decorator errors detected.")

        # checking requirements
        logger.info("Checking requirements and imports")
        if not _check_imports(main_path, reqs_txt_path):
            logger.error("Found errors, aborting.")
            exit(1)
        else: logger.success("No errors in requiremenets.txt")

    bundle = _make_zip(builddir, builddir / f"{builddir.name}.truffle")
    if bundle == None: exit(1)
    try: rel_bundle = bundle.relative_to(Path.cwd())
    except ValueError: rel_bundle = bundle
    try:
        rel_dir = builddir.relative_to(Path.cwd())
        rel_upload_dir = f" {rel_dir}" if str(rel_dir) != "." else ""
    except ValueError: rel_upload_dir = f" {builddir}"
    logger.success(f"Built project {builddir.name} to {rel_bundle}")
    if not from_upload: 
        logger.info(f"Upload with 'truffle upload{rel_upload_dir}'")
        sys.exit(0)