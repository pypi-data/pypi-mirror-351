# bindings/llamacpp_server/binding.py
import json
import os
import pprint
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional, Callable, List, Union, Dict, Any, Set
import base64
import requests # For HTTP client
from lollms_client.lollms_llm_binding import LollmsLLMBinding
from lollms_client.lollms_types import MSG_TYPE, ELF_COMPLETION_FORMAT

from ascii_colors import ASCIIColors, trace_exception
import pipmaster as pm
import platform

# Ensure llama-cpp-binaries and requests are installed
pm.ensure_packages(["requests", "pillow"]) # pillow for dummy image in test
if not pm.is_installed("llama-cpp-binaries"):
    def install_llama_cpp():
        system = platform.system()

        if system == "Windows":
            url = "https://github.com/oobabooga/llama-cpp-binaries/releases/download/v0.12.0/llama_cpp_binaries-0.12.0+cu124-py3-none-win_amd64.whl"
        elif system == "Linux":
            url = "https://github.com/oobabooga/llama-cpp-binaries/releases/download/v0.12.0/llama_cpp_binaries-0.12.0+cu124-py3-none-linux_x86_64.whl"
        else:
            print(f"Unsupported OS: {system}")
            return
        pm.install(url)
    install_llama_cpp()

try:
    import llama_cpp_binaries
except ImportError:
    ASCIIColors.error("llama-cpp-binaries package not found. Please install it.")
    ASCIIColors.error("You can try: pip install llama-cpp-binaries")
    ASCIIColors.error("Or download a wheel from: https://github.com/oobabooga/llama-cpp-binaries/releases")
    llama_cpp_binaries = None


# --- Predefined patterns ---

# Quantization type strings (derived from ggml.h, llama.cpp, and common usage)
# These are the "core component" strings, without separators like '.', '-', or '_'
_QUANT_COMPONENTS_SET: Set[str] = {
    # K-quants (most common, often with S/M/L suffix, and now XS/XXS)
    "Q2_K", "Q3_K", "Q4_K", "Q5_K", "Q6_K",
    "Q2_K_S", "Q3_K_S", "Q4_K_S", "Q5_K_S", # No Q6_K_S usually
    "Q3_K_M", "Q4_K_M", "Q5_K_M",          # No Q2/Q6_K_M usually
    "Q3_K_L",                              # Only Q3_K_L is common
    # Adding XS and XXS variants for K-quants by analogy with IQ types
    "Q2_K_XS", "Q3_K_XS", "Q4_K_XS", "Q5_K_XS", "Q6_K_XS",
    "Q2_K_XXS", "Q3_K_XXS", "Q4_K_XXS", "Q5_K_XXS", "Q6_K_XXS",

    # Non-K-quant legacy types
    "Q4_0", "Q4_1", "Q5_0", "Q5_1", "Q8_0",

    # Floating point types
    "F16", "FP16", "F32", "FP32", "BF16",

    # IQ (Innovative Quantization) types
    "IQ1_S", "IQ1_M",
    "IQ2_XXS", "IQ2_XS", "IQ2_S", "IQ2_M",
    "IQ3_XXS", "IQ3_S", "IQ3_M",
    "IQ4_NL", "IQ4_XS",

    # Newer IQ K-Quant variants (IQ types using K-quant style super-blocks)
    "IQ3_M_K", "IQ3_S_K",  # Adding IQ3_S_K as it's plausible
    "IQ4_XS_K", "IQ4_NL_K", # Adding IQ4_NL_K as it's plausible

    # Basic integer types (less common in user-facing LLM filenames as primary quantizer)
    "I8", "I16", "I32",

    # Special GGUF type names that might appear (from ggml.c `ggml_type_name`)
    "ALL_F32", "MOSTLY_F16", "MOSTLY_Q4_0", "MOSTLY_Q4_1", "MOSTLY_Q5_0", "MOSTLY_Q5_1",
    "MOSTLY_Q8_0",
    "MOSTLY_Q2_K", "MOSTLY_Q3_K_S", "MOSTLY_Q3_K_M", "MOSTLY_Q3_K_L",
    "MOSTLY_Q4_K_S", "MOSTLY_Q4_K_M", "MOSTLY_Q5_K_S", "MOSTLY_Q5_K_M", "MOSTLY_Q6_K",
    "MOSTLY_IQ1_S", "MOSTLY_IQ1_M", # Adding these
    "MOSTLY_IQ2_XXS", "MOSTLY_IQ2_XS", "MOSTLY_IQ2_S", "MOSTLY_IQ2_M",
    "MOSTLY_IQ3_XXS", "MOSTLY_IQ3_S", "MOSTLY_IQ3_M", # Adding IQ3_M, IQ3_S
    "MOSTLY_IQ4_NL", "MOSTLY_IQ4_XS"
}

# Common descriptive suffixes for model names
_MODEL_NAME_SUFFIX_COMPONENTS_SET: Set[str] = {
    "instruct", "chat", "GGUF", "HF", "ggml", "pytorch", "AWQ", "GPTQ", "EXL2",
    "base", "cont", "continue", "ft", # Fine-tuning related
    "v0.1", "v0.2", "v1.0", "v1.1", "v1.5", "v1.6", "v2.0", # Common version tags if they are truly suffixes
    # Be cautious with general version numbers (e.g., "v1", "v2") or model sizes (e.g., "7b")
    # as they are often integral parts of the base name. Only add if they are
    # *always* extraneous suffixes in your context.
    # The ones above are more specific and often appear as full suffix components.
}

# Combine, ensure uniqueness by using sets, then sort by length descending.
# Sorting ensures longer patterns (e.g., "Q4_K_M") are checked before
# shorter sub-patterns (e.g., "Q4_K" or "K_M").
_ALL_REMOVABLE_COMPONENTS: List[str] = sorted(
    list(_QUANT_COMPONENTS_SET.union(_MODEL_NAME_SUFFIX_COMPONENTS_SET)),
    key=len,
    reverse=True
)

def get_gguf_model_base_name(file_path_or_name: Union[str, Path]) -> str:
    """
    Extracts a base model name from a GGUF filename or path by removing
    the .gguf extension and then iteratively stripping known quantization
    patterns and common descriptive suffixes from the end of the name.

    The stripping is case-insensitive and checks for patterns preceded
    by '.', '-', or '_'.

    Args:
        file_path_or_name: The file path (as a string or Path object)
                           or just the filename string.

    Returns:
        The derived base model name string.
    """
    if isinstance(file_path_or_name, str):
        p = Path(file_path_or_name)
    elif isinstance(file_path_or_name, Path):
        p = file_path_or_name
    else:
        raise TypeError(
            "Input must be a string or Path object. "
            f"Got: {type(file_path_or_name)}"
        )

    name_part = p.name  # Full filename, e.g., "MyModel-7B-chat.Q4_K_M.gguf"

    # 1. Remove .gguf extension (case-insensitive)
    if name_part.lower().endswith(".gguf"):
        name_part = name_part[:-5]  # Remove last 5 chars: ".gguf"

    # 2. Iteratively strip known components (quantization, common suffixes)
    #    These components are usually preceded by '.', '-', or '_'
    while True:
        original_name_part_len = len(name_part)
        stripped_in_this_iteration = False

        for component in _ALL_REMOVABLE_COMPONENTS:
            component_lower = component.lower()
            # Check for patterns like ".component", "-component", or "_component"
            for separator in [".", "-", "_"]:
                pattern_to_check = f"{separator}{component_lower}"
                if name_part.lower().endswith(pattern_to_check):
                    # Remove from the original-case name_part
                    name_part = name_part[:-(len(pattern_to_check))]
                    stripped_in_this_iteration = True
                    break  # Break from separator loop
            if stripped_in_this_iteration:
                break # Break from component loop (found a match, restart while loop with shorter name_part)

        # If no component was stripped in a full pass through _ALL_REMOVABLE_COMPONENTS,
        # or if name_part became empty, we're done.
        if not stripped_in_this_iteration or not name_part:
            break

    # 3. Final cleanup: remove trailing separators if any are left after stripping
    while name_part and name_part[-1] in ['.', '-', '_']:
        name_part = name_part[:-1]

    return name_part


BindingName = "LlamaCppServerBinding"
DEFAULT_LLAMACPP_SERVER_HOST = "127.0.0.1"
DEFAULT_LLAMACPP_SERVER_PORT = 9641
# Based on the LlamaServer class provided in the prompt
class LlamaCppServerProcess:
    def __init__(self, model_path: str|Path, clip_model_path: str = None, server_binary_path: str=None, port: int=None, server_args: Dict[str, Any]={}):
        self.model_path = Path(model_path)
        self.clip_model_path = clip_model_path
        self.server_binary_path = Path(server_binary_path)
        if self.server_binary_path is None:
            self.server_binary_path = llama_cpp_binaries.get_binary_path()
        self.port = port if port else DEFAULT_LLAMACPP_SERVER_PORT
        self.server_args = server_args
        self.process: Optional[subprocess.Popen] = None
        self.session = requests.Session()
        self.host = DEFAULT_LLAMACPP_SERVER_HOST
        self.base_url = f"http://{self.host}:{self.port}"
        self.is_healthy = False
        self._stderr_lines = [] # Store last few stderr lines for debugging
        self._stderr_thread = None

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        if not self.server_binary_path.exists():
            raise FileNotFoundError(f"Llama.cpp server binary not found: {self.server_binary_path}")

        self._start_server()

    def _filter_stderr(self, stderr_pipe):
        try:
            for line in iter(stderr_pipe.readline, ''):
                if line:
                    self._stderr_lines.append(line.strip())
                    if len(self._stderr_lines) > 50: # Keep last 50 lines
                        self._stderr_lines.pop(0)
                    # Simple progress or key info logging
                    if "llama_model_loaded" in line or "error" in line.lower() or "failed" in line.lower():
                        ASCIIColors.debug(f"[LLAMA_SERVER_STDERR] {line.strip()}")
                    elif "running" in line and "port" in line: # Server startup message
                        ASCIIColors.info(f"[LLAMA_SERVER_STDERR] {line.strip()}")

        except ValueError: # Pipe closed
            pass
        except Exception as e:
            ASCIIColors.warning(f"Exception in stderr filter thread: {e}")


    def _start_server(self, is_embedding=False):
        cmd = [
            str(self.server_binary_path),
            "--model", str(self.model_path),
            "--host", self.host,
            "--port", str(self.port),
            # Add other common defaults or arguments from self.server_args
        ]

        # Common arguments mapping from LlamaCppBinding to server CLI args
        # (This needs to be kept in sync with llama.cpp server's CLI)
        arg_map = {
            "n_ctx": "--ctx-size", "n_gpu_layers": "--gpu-layers", "main_gpu": "--main-gpu",
            "tensor_split": "--tensor-split", "use_mmap": (lambda v: ["--no-mmap"] if not v else []),
            "use_mlock": (lambda v: ["--mlock"] if v else []), "seed": "--seed",
            "n_batch": "--batch-size", "n_threads": "--threads", "n_threads_batch": "--threads-batch",
            "rope_scaling_type": "--rope-scaling", "rope_freq_base": "--rope-freq-base",
            "rope_freq_scale": "--rope-freq-scale",
            "embedding": (lambda v: ["--embedding"] if is_embedding else []), # Server needs to be started with embedding support
            "verbose": (lambda v: ["--verbose"] if v else []),
            "chat_template": "--chat-template", # For newer servers if they support jinja chat templates
                                              # Old llama.cpp server used --chatml or specific format flags
        }
        
        # For LLaVA, specific args are needed
        if self.clip_model_path:
            cmd.extend(["--mmproj", str(self.clip_model_path)])
            # The server might automatically detect LLaVA chat format or need a specific flag
            # e.g., --chat-template llava-1.5 (if server supports templates)
            # For older servers, a specific chat format flag like --chatml with LLaVA prompt structure was used.
            # The server from llama-cpp-binaries is usually quite up-to-date.

        for key, cli_arg in arg_map.items():
            val = self.server_args.get(key)
            if val is not None:
                if callable(cli_arg): # For args like --no-mmap
                    cmd.extend(cli_arg(val))
                else:
                    cmd.extend([cli_arg, str(val)])
        
        # Add any extra CLI flags directly
        extra_cli_flags = self.server_args.get("extra_cli_flags", [])
        if isinstance(extra_cli_flags, str): # If it's a string, split it
            extra_cli_flags = extra_cli_flags.split()
        cmd.extend(extra_cli_flags)


        ASCIIColors.info(f"Starting Llama.cpp server with command: {' '.join(cmd)}")
        
        # Prevent paths with spaces from breaking the command on some OS, though Popen usually handles this.
        # For safety, ensure paths are quoted if necessary, or rely on Popen's list-based command.

        env = os.environ.copy()
        # On Linux, it might be necessary to set LD_LIBRARY_PATH if server binary has shared lib dependencies in its folder
        if os.name == 'posix' and self.server_binary_path.parent != Path('.'):
            lib_path_str = str(self.server_binary_path.parent.resolve())
            current_ld_path = env.get('LD_LIBRARY_PATH', '')
            if current_ld_path:
                env['LD_LIBRARY_PATH'] = f"{lib_path_str}:{current_ld_path}"
            else:
                env['LD_LIBRARY_PATH'] = lib_path_str

        try:
            ASCIIColors.green(f"running server: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE, # Capture stdout as well for debugging
                text=True,
                bufsize=1, # Line buffered
                env=env
            )
        except Exception as e:
            ASCIIColors.error(f"Failed to start llama.cpp server process: {e}")
            trace_exception(e)
            raise

        # Start stderr/stdout reading threads
        self._stderr_thread = threading.Thread(target=self._filter_stderr, args=(self.process.stderr,), daemon=True)
        self._stderr_thread.start()
        # self._stdout_thread = threading.Thread(target=self._filter_stderr, args=(self.process.stdout,), daemon=True) # can use same filter
        # self._stdout_thread.start()


        # Wait for server to be healthy
        health_url = f"{self.base_url}/health"
        max_wait_time = self.server_args.get("server_startup_timeout", 60) # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            if self.process.poll() is not None:
                exit_code = self.process.poll()
                stderr_output = "\n".join(self._stderr_lines[-10:]) # Last 10 lines
                raise RuntimeError(f"Llama.cpp server process terminated unexpectedly with exit code {exit_code} during startup. Stderr:\n{stderr_output}")
            try:
                response = self.session.get(health_url, timeout=2)
                if response.status_code == 200 and response.json().get("status") == "ok":
                    self.is_healthy = True
                    ASCIIColors.green(f"Llama.cpp server started successfully on port {self.port}.")
                    return
            except requests.exceptions.ConnectionError:
                time.sleep(1) # Wait and retry
            except Exception as e:
                ASCIIColors.warning(f"Health check failed: {e}")
                time.sleep(1)
        
        self.is_healthy = False
        self.stop() # Ensure process is killed if health check failed
        stderr_output = "\n".join(self._stderr_lines[-10:])
        raise TimeoutError(f"Llama.cpp server failed to become healthy on port {self.port} within {max_wait_time}s. Stderr:\n{stderr_output}")

    def stop(self):
        self.is_healthy = False
        if self.process:
            ASCIIColors.info(f"Stopping Llama.cpp server (PID: {self.process.pid})...")
            try:
                # Try graceful termination first
                if os.name == 'nt': # Windows
                    # Sending CTRL_C_EVENT to the process group might be more effective for console apps
                    # self.process.send_signal(signal.CTRL_C_EVENT) # Requires creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                     self.process.terminate() # For Windows, terminate is often like kill
                else: # POSIX
                    self.process.terminate() # Sends SIGTERM

                self.process.wait(timeout=10) # Wait for graceful shutdown
            except subprocess.TimeoutExpired:
                ASCIIColors.warning("Llama.cpp server did not terminate gracefully, killing...")
                self.process.kill() # Force kill
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    ASCIIColors.error("Failed to kill llama.cpp server process.")
            except Exception as e:
                ASCIIColors.error(f"Error during server stop: {e}")
            finally:
                self.process = None
                if self._stderr_thread and self._stderr_thread.is_alive():
                    self._stderr_thread.join(timeout=1) # Wait for thread to finish
                ASCIIColors.info("Llama.cpp server stopped.")


class LlamaCppServerBinding(LollmsLLMBinding):
    """
    Binding for llama.cpp server using pre-compiled binaries.
    Manages a local llama.cpp server subprocess and communicates via HTTP.
    """
    # Default parameters for the llama.cpp server
    DEFAULT_SERVER_ARGS = {
        "n_gpu_layers": 0,
        "n_ctx": 128000,
        "n_batch": 512,
        "embedding": False, # Enable if embeddings are needed via /embedding or /v1/embeddings
        "verbose": False,
        "server_startup_timeout": 120, # seconds
        # "chat_format": "chatml", # Deprecated in favor of --chat-template, but some old servers might need it
        # For LLaVA
        # "clip_model_path": None, 
        # "chat_template": "llava-1.5" # if server supports it. Or specific prompt structure.
    }

    def __init__(self,
                 model_name: str, # Name of the GGUF file (e.g., "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
                 models_path: str,
                 clip_model_name: str = None,
                 config: Optional[Dict[str, Any]] = None, # Binding specific config from global_config.yaml
                 default_completion_format: ELF_COMPLETION_FORMAT = ELF_COMPLETION_FORMAT.Chat,
                 **kwargs # Overrides for server_args
                 ):
        
        super().__init__(binding_name=BindingName)

        if llama_cpp_binaries is None:
            raise ImportError("llama-cpp-binaries package is required but not found.")

        self.models_path = Path(models_path)
        self.model_name = model_name
        self.model_path = self.models_path/self.model_name
        self.clip_model_path = self.models_path/clip_model_name if clip_model_name else None
        self.default_completion_format = default_completion_format
        
        self.server_args = {**self.DEFAULT_SERVER_ARGS, **(config or {})}
        self.server_args.update(kwargs) # Apply direct kwargs overrides

        self.server_binary_path = self._get_server_binary_path()
        self.current_model_path: Optional[Path] = None
        self.server_process: Optional[LlamaCppServerProcess] = None
        self.port: Optional[int] = None

        # Attempt to load the model (which starts the server)
        self.load_model(str(self.model_path))

    def _get_server_binary_path(self) -> Path:
        try:
            # Check if a custom path is provided in config
            custom_path_str = self.server_args.get("llama_server_binary_path")
            if custom_path_str:
                custom_path = Path(custom_path_str)
                if custom_path.exists() and custom_path.is_file():
                    ASCIIColors.info(f"Using custom llama.cpp server binary path: {custom_path}")
                    return custom_path
                else:
                    ASCIIColors.warning(f"Custom llama.cpp server binary path '{custom_path_str}' not found or not a file. Falling back.")

            # Default to using llama_cpp_binaries
            bin_path_str = llama_cpp_binaries.get_binary_path() # specify "server"
            if bin_path_str:
                bin_path = Path(bin_path_str)
                if bin_path.exists() and bin_path.is_file():
                    ASCIIColors.info(f"Using llama.cpp server binary from llama-cpp-binaries: {bin_path}")
                    return bin_path
            
            raise FileNotFoundError("Could not locate llama.cpp server binary via llama-cpp-binaries or custom path.")

        except Exception as e:
            ASCIIColors.error(f"Error getting llama.cpp server binary path: {e}")
            trace_exception(e)
            # As a last resort, try a common name in system PATH or a known location if Lollms ships one
            # For now, rely on llama-cpp-binaries or explicit config.
            raise FileNotFoundError(
                "Llama.cpp server binary not found. Ensure 'llama-cpp-binaries' is installed "
                "or provide 'llama_server_binary_path' in the binding's configuration."
            ) from e

    def _resolve_model_path(self, model_path: str) -> Path:
        # Search order:
        # 1. Absolute path
        # 2. Relative to binding-specific models path (e.g., personal_models_path/LlamaCppServerBinding/)
        # 3. Relative to personal_models_path
        # 4. Relative to models_zoo_path
        
        model_p = Path(model_path)
        if model_p.is_absolute() and model_p.exists():
            return model_p

        paths_to_check = []
        binding_specific_folder_name = self.binding_name # "LlamaCppServerBinding"
        paths_to_check.append(self.models_path)

        for p in paths_to_check:
            if p.exists() and p.is_file():
                ASCIIColors.info(f"Found model at: {p}")
                return p
        
        raise FileNotFoundError(f"Model '{model_path}' not found in standard Lollms model paths or as an absolute path.")

    def _find_available_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0)) # Bind to port 0 to get an OS-assigned available port
            return s.getsockname()[1]

    def load_model(self, model_name: str) -> bool:
        resolved_path = self._resolve_model_path(model_name)

        if self.server_process and self.server_process.is_healthy and self.current_model_path == resolved_path:
            ASCIIColors.info(f"Model '{model_name}' is already loaded and server is running.")
            return True

        if self.server_process:
            self.unload_model() # Stop existing server

        self.model_name = model_name # Store the name provided by user
        self.current_model_path = resolved_path
        self.port = self._find_available_port()
        
        ASCIIColors.info(f"Attempting to start Llama.cpp server for model: {self.current_model_path} on port {self.port}")
        
        # Prepare server_args specifically for this model load
        current_server_args = self.server_args.copy()

        if not self.clip_model_path:
            # Try to find a corresponding .mmproj file or allow user to specify in config
            # e.g. if model is llava-v1.5-7b.Q4_K_M.gguf, look for llava-v1.5-7b.mmproj or mmproj-modelname.gguf
            base_name = get_gguf_model_base_name(self.current_model_path.stem) # etc.
            
            potential_clip_paths = [
                self.current_model_path.parent / f"{base_name}.mmproj",
                self.current_model_path.parent / f"mmproj-{base_name}.gguf", # Common pattern
                self.current_model_path.with_suffix(".mmproj"),
            ]
            found_clip_path = None
            for p_clip in potential_clip_paths:
                if p_clip.exists():
                    found_clip_path = str(p_clip)
                    ASCIIColors.info(f"Auto-detected LLaVA clip model: {found_clip_path}")
                    break
            if found_clip_path:
                self.clip_model_path = found_clip_path
                # Set a default LLaVA chat template if server supports it, or rely on server auto-detection
                #if not current_server_args.get("chat_template") and not current_server_args.get("chat_format"):
                #    current_server_args["chat_template"] = "llava-1.5" # Common default
            else:
                ASCIIColors.warning("Vision capabilities will likely not work. Please ensure the .mmproj file is "
                                    "next to the model or specify 'clip_model_path' in binding config.")


        try:
            self.server_process = LlamaCppServerProcess(
                model_path=str(self.current_model_path),
                clip_model_path = str(self.clip_model_path),
                server_binary_path=str(self.server_binary_path),
                port=self.port,
                server_args=current_server_args,
            )
            return self.server_process.is_healthy
        except Exception as e:
            ASCIIColors.error(f"Failed to load model '{model_name}' and start server: {e}")
            trace_exception(e)
            self.server_process = None
            self.current_model_path = None
            return False

    def unload_model(self):
        if self.server_process:
            self.server_process.stop()
            self.server_process = None
        self.current_model_path = None 
        self.port = None
        ASCIIColors.info("Llama.cpp server and model unloaded.")
    
    def _get_request_url(self, endpoint: str) -> str:
        if not self.server_process or not self.server_process.is_healthy:
            raise ConnectionError("Llama.cpp server is not running or not healthy.")
        return f"{self.server_process.base_url}{endpoint}"

    def _prepare_generation_payload(self,
                                   prompt: str, 
                                   system_prompt: str = "",
                                   n_predict: Optional[int] = None,
                                   temperature: float = 0.7,
                                   top_k: int = 40,
                                   top_p: float = 0.9,
                                   repeat_penalty: float = 1.1,
                                   repeat_last_n: Optional[int] = 64, # Server calls this repeat_last_n or penalty_last_n
                                   seed: Optional[int] = None,
                                   stream: bool = False,
                                   use_chat_format: bool = True, # True for /v1/chat/completions, False for /completion
                                   images: Optional[List[str]] = None,
                                   **extra_params # For things like grammar, mirostat, etc from server_args
                                   ) -> Dict:
        
        # Start with defaults from server_args, then override with call params
        payload_params = {
            "temperature": self.server_args.get("temperature", 0.7),
            "top_k": self.server_args.get("top_k", 40),
            "top_p": self.server_args.get("top_p", 0.9),
            "repeat_penalty": self.server_args.get("repeat_penalty", 1.1),
            "repeat_last_n": self.server_args.get("repeat_last_n", 64),
            "mirostat": self.server_args.get("mirostat_mode", 0), # llama.cpp server uses mirostat (0=disabled, 1=v1, 2=v2)
            "mirostat_tau": self.server_args.get("mirostat_tau", 5.0),
            "mirostat_eta": self.server_args.get("mirostat_eta", 0.1),
            # Add other mappable params from self.server_args like min_p, typical_p, grammar etc.
        }
        if "grammar_string" in self.server_args and self.server_args["grammar_string"]: # From config
             payload_params["grammar"] = self.server_args["grammar_string"]

        # Override with specific call parameters
        payload_params.update({
            "temperature": temperature, "top_k": top_k, "top_p": top_p,
            "repeat_penalty": repeat_penalty, "repeat_last_n": repeat_last_n,
        })
        if n_predict is not None: payload_params['n_predict'] = n_predict # Server uses n_predict
        if seed is not None: payload_params['seed'] = seed

        # Filter None values, as server might not like them
        payload_params = {k: v for k, v in payload_params.items() if v is not None}
        payload_params.update(extra_params) # Add any other specific params for this call

        if use_chat_format and self.default_completion_format == ELF_COMPLETION_FORMAT.Chat:
            # Use /v1/chat/completions format
            messages = []
            if system_prompt and system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})
            
            user_content: Union[str, List[Dict[str, Any]]] = prompt
            if images and self.clip_model_path: # Check if it's a LLaVA setup
                image_parts = []
                for img_path in images:
                    try:
                        with open(img_path, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                        image_type = Path(img_path).suffix[1:].lower() or "png"
                        if image_type == "jpg": image_type = "jpeg"
                        # Llama.cpp server expects image data directly for LLaVA with /completion
                        # For /v1/chat/completions, it expects OpenAI's format for multimodal
                        image_parts.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/{image_type};base64,{encoded_string}"}
                        })
                    except Exception as ex:
                        trace_exception(ex)
                user_content = [{"type": "text", "text": prompt}] + image_parts # type: ignore

            messages.append({"role": "user", "content": user_content})
            
            final_payload = {"messages": messages, "stream": stream, **payload_params}
            # n_predict is max_tokens for OpenAI API
            if 'n_predict' in final_payload:
                final_payload['max_tokens'] = final_payload.pop('n_predict')

            return final_payload
        else:
            # Use /completion format (legacy or for raw text)
            # For LLaVA with /completion, images are typically passed in a special way in the prompt
            # or via an 'image_data' field if the server supports it.
            # The example class uses tokenized prompt for /completion.
            # For simplicity here, we'll send text prompt, server tokenizes.
            # Llama.cpp server's /completion often expects 'prompt' as string or tokens.
            # If images are involved with /completion, it needs specific handling.
            # Example: 'prompt': "USER: <image>\nWhat is this?\nASSISTANT:", 'image_data': [{'data': base64_image, 'id': 10}]
            
            full_prompt = prompt
            if system_prompt and system_prompt.strip():
                # Heuristic for instruct models, actual formatting depends on model/template
                full_prompt = f"{system_prompt}\n\nUSER: {prompt}\nASSISTANT:" 
            
            final_payload = {"prompt": full_prompt, "stream": stream, **payload_params}

            if images and self.server_args.get("clip_model_path"):
                image_data_list = []
                for i, img_path in enumerate(images):
                    try:
                        with open(img_path, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                        image_data_list.append({"data": encoded_string, "id": i + 10}) # ID needs to be > 9 for llama.cpp server
                    except Exception as e_img:
                        ASCIIColors.error(f"Could not encode image {img_path} for /completion: {e_img}")
                if image_data_list:
                    final_payload["image_data"] = image_data_list
                    # The prompt needs to contain placeholder like USER: <image 1>\n<prompt>\nASSISTANT:
                    # This part is tricky and model-dependent. For now, we assume user's prompt is already formatted.
                    # Or, the server (if new enough) might handle it with chat_template even for /completion.

            return final_payload


    def generate_text(self, 
                     prompt: str,
                     images: Optional[List[str]] = None, 
                     system_prompt: str = "",
                     n_predict: Optional[int] = None,
                     stream: bool = False,
                     temperature: float = None, # Use binding's default if None
                     top_k: int = None,
                     top_p: float = None,
                     repeat_penalty: float = None,
                     repeat_last_n: Optional[int] = None,
                     seed: Optional[int] = None,
                     streaming_callback: Optional[Callable[[str, int], bool]] = None,
                     use_chat_format_override: Optional[bool] = None, # Allow overriding binding's default format
                     **generation_kwargs 
                     ) -> Union[str, Dict[str, any]]:

        if not self.server_process or not self.server_process.is_healthy:
             return {"status": False, "error": "Llama.cpp server is not running or not healthy."}

        _use_chat_format = use_chat_format_override if use_chat_format_override is not None \
                           else (self.default_completion_format == ELF_COMPLETION_FORMAT.Chat)

        payload = self._prepare_generation_payload(
            prompt=prompt, system_prompt=system_prompt, n_predict=n_predict,
            temperature=temperature if temperature is not None else self.server_args.get("temperature",0.7),
            top_k=top_k if top_k is not None else self.server_args.get("top_k",40),
            top_p=top_p if top_p is not None else self.server_args.get("top_p",0.9),
            repeat_penalty=repeat_penalty if repeat_penalty is not None else self.server_args.get("repeat_penalty",1.1),
            repeat_last_n=repeat_last_n if repeat_last_n is not None else self.server_args.get("repeat_last_n",64),
            seed=seed if seed is not None else self.server_args.get("seed", -1), # Use server's default seed if not provided
            stream=stream, use_chat_format=_use_chat_format, images=images,
            **generation_kwargs
        )
        
        endpoint = "/v1/chat/completions" if _use_chat_format else "/completion"
        request_url = self._get_request_url(endpoint)
        
        # For debugging, print payload (excluding potentially large image data)
        debug_payload = {k:v for k,v in payload.items() if k not in ["image_data"]}
        if "messages" in debug_payload:
            debug_payload["messages"] = [{k:v for k,v in msg.items() if k !="content" or not isinstance(v,list) or not any("image_url" in part for part in v)} for msg in debug_payload["messages"]]
        ASCIIColors.debug(f"Request to {request_url} with payload: {json.dumps(debug_payload, indent=2)[:500]}...")

        full_response_text = ""
        try:
            response = self.server_process.session.post(request_url, json=payload, stream=stream, timeout=self.server_args.get("generation_timeout", 300))
            response.raise_for_status()

            if stream:
                for line in response.iter_lines():
                    if not line: continue
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '): line_str = line_str[6:]
                    if line_str == '[DONE]': break # OpenAI stream end
                    
                    try:
                        chunk_data = json.loads(line_str)
                        chunk_content = ""
                        if _use_chat_format: # OpenAI /v1/chat/completions format
                            delta = chunk_data.get('choices', [{}])[0].get('delta', {})
                            chunk_content = delta.get('content', '')
                        else: # /completion format
                            chunk_content = chunk_data.get('content', '')
                        
                        if chunk_content:
                            full_response_text += chunk_content
                            if streaming_callback and not streaming_callback(chunk_content, MSG_TYPE.MSG_TYPE_CHUNK):
                                # If callback returns False, we should try to stop generation.
                                # Llama.cpp server's /completion doesn't have a direct way to stop mid-stream via API.
                                # Closing the connection might be the only way if server supports it.
                                ASCIIColors.info("Streaming callback requested stop.")
                                response.close() # Attempt to signal server by closing connection
                                break
                        if chunk_data.get('stop', False) or chunk_data.get('stopped_eos',False) or chunk_data.get('stopped_limit',False): # /completion specific stop flags
                            break
                    except json.JSONDecodeError:
                        ASCIIColors.warning(f"Failed to decode JSON stream chunk: {line_str}")
                        continue # Or handle error
                return full_response_text
            else: # Not streaming
                response_data = response.json()
                return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')

        except requests.exceptions.RequestException as e:
            error_message = f"Llama.cpp server request error: {e}"
            if e.response is not None:
                try:
                    error_details = e.response.json()
                    error_message += f" - Details: {error_details.get('error', e.response.text)}"
                except json.JSONDecodeError:
                    error_message += f" - Response: {e.response.text[:200]}"
            ASCIIColors.error(error_message)
            return {"status": False, "error": error_message, "details": str(e.response.text if e.response else "No response text")}
        except Exception as ex:
            error_message = f"Llama.cpp generation error: {str(ex)}"
            trace_exception(ex)
            return {"status": False, "error": error_message}

    def tokenize(self, text: str) -> List[int]:
        if not self.server_process or not self.server_process.is_healthy:
            raise ConnectionError("Llama.cpp server is not running.")
        try:
            response = self.server_process.session.post(self._get_request_url("/tokenize"), json={"content": text})
            response.raise_for_status()
            return response.json().get("tokens", [])
        except Exception as e:
            ASCIIColors.error(f"Tokenization error: {e}"); trace_exception(e)
            return [] # Or raise

    def detokenize(self, tokens: List[int]) -> str:
        if not self.server_process or not self.server_process.is_healthy:
            raise ConnectionError("Llama.cpp server is not running.")
        try:
            response = self.server_process.session.post(self._get_request_url("/detokenize"), json={"tokens": tokens})
            response.raise_for_status()
            return response.json().get("content", "")
        except Exception as e:
            ASCIIColors.error(f"Detokenization error: {e}"); trace_exception(e)
            return "" # Or raise

    def count_tokens(self, text: str) -> int:
        return len(self.tokenize(text))

    def embed(self, text: str, **kwargs) -> List[float]:
        if not self.server_process or not self.server_process.is_healthy:
             raise Exception("Llama.cpp server is not running.")
        if not self.server_args.get("embedding"):
            raise Exception("Embedding support was not enabled in server_args (set 'embedding: true').")
        
        try:
            # llama.cpp server has /embedding endpoint (non-OpenAI) and /v1/embeddings (OpenAI-compatible)
            # Let's try /v1/embeddings first for compatibility
            payload = {"input": text}
            if "model" in kwargs: payload["model"] = kwargs["model"] # Can specify model if server handles multiple embedding models (unlikely for llama.cpp server)
            
            request_url = self._get_request_url("/v1/embeddings")
            response = self.server_process.session.post(request_url, json=payload)

            if response.status_code == 404: # Fallback to /embedding if /v1/embeddings not found
                ASCIIColors.debug("Trying /embedding endpoint as /v1/embeddings was not found.")
                request_url = self._get_request_url("/embedding")
                response = self.server_process.session.post(request_url, json={"content": text}) # /embedding uses "content"

            response.raise_for_status()
            data = response.json()
            
            if "data" in data and isinstance(data["data"], list) and "embedding" in data["data"][0]: # /v1/embeddings format
                return data["data"][0]["embedding"]
            elif "embedding" in data and isinstance(data["embedding"], list): # /embedding format
                return data["embedding"]
            else:
                raise ValueError(f"Unexpected embedding response format: {data}")

        except requests.exceptions.RequestException as e:
            err_msg = f"Llama.cpp server embedding request error: {e}"
            if e.response: err_msg += f" - {e.response.text[:200]}"
            raise Exception(err_msg) from e
        except Exception as ex:
            trace_exception(ex); raise Exception(f"Llama.cpp embedding failed: {str(ex)}") from ex
        
    def get_model_info(self) -> dict:
        info = {
            "name": self.binding_name,
            "model_name": self.model_name, # User-provided name
            "model_path": str(self.current_model_path) if self.current_model_path else "Not loaded",
            "loaded": self.server_process is not None and self.server_process.is_healthy,
            "server_args": self.server_args,
            "port": self.port if self.port else "N/A"
        }
        if info["loaded"]:
            # Try to get more info from server's /props or /v1/models
            try:
                props_url = self._get_request_url("/props") # llama.cpp specific
                props_resp = self.server_process.session.get(props_url, timeout=5).json()
                info.update({
                    "server_n_ctx": props_resp.get("default_generation_settings",{}).get("n_ctx"), # Example path
                    "server_chat_format": props_resp.get("chat_format"),
                    "server_clip_model": props_resp.get("mmproj"),
                })
            except Exception: pass # Ignore if /props fails or data missing
            
            is_llava = ("llava" in self.model_name.lower() or "bakllava" in self.model_name.lower()) or \
                       (self.server_args.get("clip_model_path") is not None) or \
                       (info.get("server_clip_model") is not None)
            
            info["supports_vision"] = is_llava
            info["supports_structured_output"] = self.server_args.get("grammar_string") is not None
        return info

    def listModels(self) -> List[Dict[str, str]]:
        # This binding manages one GGUF model at a time by starting a server for it.
        # To "list models", we could scan the Lollms model directories for .gguf files.
        models_found = []
        gguf_pattern = "*.gguf"
        
        search_paths = []
        binding_specific_folder_name = self.binding_name

        search_paths.append(self.models_path)
        
        unique_models = set()
        for spath in search_paths:
            if spath.exists() and spath.is_dir():
                for model_file in spath.rglob(gguf_pattern): # rglob for recursive
                    if model_file.is_file() and model_file.name not in unique_models:
                        models_found.append({
                            'model_name': model_file.name,
                            # Path relative to one of the main model roots for display/selection
                            'path_hint': str(model_file.relative_to(spath.parent) if model_file.is_relative_to(spath.parent) else model_file),
                            'size_gb': f"{model_file.stat().st_size / (1024**3):.2f} GB"
                        })
                        unique_models.add(model_file.name)
        return models_found
    
    def __del__(self):
        self.unload_model() # Ensure server is stopped when binding is deleted


if __name__ == '__main__':
    global full_streamed_text
    ASCIIColors.yellow("Testing LlamaCppServerBinding...")

    # --- Configuration ---
    # This should be the NAME of your GGUF model file. The binding will search for it.
    # e.g., "Mistral-7B-Instruct-v0.2-Q4_K_M.gguf"
    # Ensure this model is placed in one of the Lollms model directories.
    # For testing, you can put a small GGUF model in the same directory as this script
    # and set personal_models_path to "."

    # Adjust current_directory if your models are elsewhere for testing
    current_directory = Path(__file__).parent 
    models_path = "E:\lollms\models\gguf\Mistral-Nemo-Instruct-2407-GGUF" #replace with your own model path
    model_name = "Mistral-Nemo-Instruct-2407-Q2_K.gguf"

    # Binding config (passed to server_args)
    binding_config = {
        "n_gpu_layers": 0,    # Set to -1 or a number for GPU offload
        "n_ctx": 512,         # Short context for testing
        "embedding": True,    # Enable for embedding tests
        "verbose": False,     # llama.cpp server verbose logs
        # "extra_cli_flags": ["--cont-batching"] # Example of extra flags
        "server_startup_timeout": 180 # Give more time for server to start, esp. with large models
    }

    active_binding = None
    try:
        ASCIIColors.cyan("\n--- Initializing LlamaCppServerBinding ---")
        active_binding = LlamaCppServerBinding(
            model_name=model_name,
            models_path=models_path,
            config=binding_config
        )
        if not active_binding.server_process or not active_binding.server_process.is_healthy:
            raise RuntimeError("Server process failed to start or become healthy.")

        ASCIIColors.green(f"Binding initialized. Server for '{active_binding.model_name}' running on port {active_binding.port}.")
        ASCIIColors.info(f"Model Info: {json.dumps(active_binding.get_model_info(), indent=2)}")

        
        # --- List Models (scans configured directories) ---
        ASCIIColors.cyan("\n--- Listing Models (from search paths) ---")
        listed_models = active_binding.listModels()
        if listed_models:
            ASCIIColors.green(f"Found {len(listed_models)} GGUF files. First 5:")
            for m in listed_models[:5]: print(m)
        else: ASCIIColors.warning("No GGUF models found in search paths.")

        # --- Tokenize/Detokenize ---
        ASCIIColors.cyan("\n--- Tokenize/Detokenize ---")
        sample_text = "Hello, Llama.cpp server world!"
        tokens = active_binding.tokenize(sample_text)
        ASCIIColors.green(f"Tokens for '{sample_text}': {tokens[:10]}...")
        token_count = active_binding.count_tokens(sample_text)
        ASCIIColors.green(f"Token count: {token_count}")
        if tokens: # Only detokenize if tokenization worked
            detokenized_text = active_binding.detokenize(tokens)
            ASCIIColors.green(f"Detokenized text: {detokenized_text}")
            # Note: exact match might depend on BOS/EOS handling by server's tokenizer
            # assert detokenized_text.strip() == sample_text.strip(), "Tokenization/Detokenization mismatch!"
        else: ASCIIColors.warning("Tokenization returned empty list, skipping detokenization.")

        # --- Text Generation (Non-Streaming, Chat Format using /v1/chat/completions) ---
        ASCIIColors.cyan("\n--- Text Generation (Non-Streaming, Chat API) ---")
        prompt_text = "What is the capital of Germany?"
        system_prompt_text = "You are a concise geography expert."
        generated_text = active_binding.generate_text(
            prompt_text, system_prompt=system_prompt_text, n_predict=20, stream=False,
            use_chat_format_override=True # Force /v1/chat/completions
        )
        if isinstance(generated_text, str): ASCIIColors.green(f"Generated text: {generated_text}")
        else: ASCIIColors.error(f"Generation failed: {generated_text}")

        # --- Text Generation (Streaming, /completion API) ---
        ASCIIColors.cyan("\n--- Text Generation (Streaming, Completion API) ---")
        full_streamed_text = ""
        def stream_callback(chunk: str, msg_type: int):
            global full_streamed_text; ASCIIColors.green(f"{chunk}", end="", flush=True)
            full_streamed_text += chunk; return True
        
        result = active_binding.generate_text(
            prompt_text, system_prompt=system_prompt_text, n_predict=30, stream=True, 
            streaming_callback=stream_callback, use_chat_format_override=False # Force /completion
        )
        print("\n--- End of Stream ---")
        if isinstance(result, str): ASCIIColors.green(f"Full streamed text: {result}")
        else: ASCIIColors.error(f"Streaming generation failed: {result}")

        # --- Embeddings ---
        if binding_config.get("embedding"):
            ASCIIColors.cyan("\n--- Embeddings ---")
            embedding_text = "Test sentence for server-based embeddings."
            try:
                embedding_vector = active_binding.embed(embedding_text)
                ASCIIColors.green(f"Embedding for '{embedding_text}' (first 3 dims): {embedding_vector[:3]}...")
                ASCIIColors.info(f"Embedding vector dimension: {len(embedding_vector)}")
            except Exception as e_emb: ASCIIColors.warning(f"Could not get embedding: {e_emb}")
        else: ASCIIColors.yellow("\n--- Embeddings Skipped (embedding: false in config) ---")

        # --- LLaVA Test (Conceptual - requires a LLaVA model and mmproj) ---
        # To test LLaVA:
        models_path = "E:\drumber" #replace with your own model path
        model_name = "llava-v1.6-mistral-7b.Q3_K_XS.gguf"
        model_path = Path(models_path)/model_name
        ASCIIColors.cyan("\n--- LLaVA Vision Test ---")
        dummy_image_path = Path("E:\\drumber\\drumber.png")
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (150, 70), color = ('magenta'))
            d = ImageDraw.Draw(img); d.text((10,10), "Server LLaVA", fill=('white'))
            img.save(dummy_image_path)
            ASCIIColors.info(f"Created dummy image for LLaVA: {dummy_image_path}")

            llava_prompt = "Describe this image."
            # For /v1/chat/completions with LLaVA, images are passed in messages.
            # For /completion with LLaVA, prompt needs <image> placeholder and image_data field.
            llava_response = active_binding.generate_text(
                prompt=llava_prompt, images=[str(dummy_image_path)], n_predict=40, stream=False,
                use_chat_format_override=True # Use /v1/chat/completions for easier multimodal
            )
            if isinstance(llava_response, str): ASCIIColors.green(f"LLaVA response: {llava_response}")
            else: ASCIIColors.error(f"LLaVA generation failed: {llava_response}")
        except ImportError: ASCIIColors.warning("Pillow not found. Cannot create dummy image for LLaVA.")
        except Exception as e_llava: ASCIIColors.error(f"LLaVA test error: {e_llava}"); trace_exception(e_llava)
        finally:
            if dummy_image_path.exists(): dummy_image_path.unlink()
        
        # --- Test changing model ---
        # This part is conceptual. You'd need another GGUF model file for a real test.
        # For now, we'll just call load_model with the same model to test the logic.

        ASCIIColors.cyan("\n--- Testing Model Change (reloading same model) ---")
        reload_success = active_binding.load_model(str(model_path))
        if reload_success and active_binding.server_process and active_binding.server_process.is_healthy:
            ASCIIColors.green(f"Model reloaded/re-confirmed successfully. Server on port {active_binding.port}.")
            # Quick generation test after reload
            reloaded_gen = active_binding.generate_text("Ping", n_predict=5, stream=False)
            if isinstance(reloaded_gen, str): ASCIIColors.green(f"Post-reload ping response: {reloaded_gen.strip()}")
            else: ASCIIColors.error(f"Post-reload generation failed: {reloaded_gen}")
        else:
            ASCIIColors.error("Failed to reload model or server not healthy after reload attempt.")


    except ImportError as e_imp:
        ASCIIColors.error(f"Import error: {e_imp}. Ensure llama-cpp-binaries is installed.")
    except FileNotFoundError as e_fnf:
        ASCIIColors.error(f"File not found error: {e_fnf}. Check model or server binary paths.")
    except ConnectionError as e_conn:
        ASCIIColors.error(f"Connection error (server might have failed to start or is unresponsive): {e_conn}")
    except RuntimeError as e_rt:
        ASCIIColors.error(f"Runtime error (often server process issue): {e_rt}")
        if active_binding and active_binding.server_process:
             ASCIIColors.error("Last stderr lines from server:")
             for line in active_binding.server_process._stderr_lines[-20:]: print(line) # Print last 20
    except Exception as e_main:
        ASCIIColors.error(f"An unexpected error occurred: {e_main}")
        trace_exception(e_main)
    finally:
        if active_binding:
            ASCIIColors.cyan("\n--- Unloading Model and Stopping Server ---")
            active_binding.unload_model()
            ASCIIColors.green("Server stopped and model unloaded.")
                


    ASCIIColors.yellow("\nLlamaCppServerBinding test finished.")