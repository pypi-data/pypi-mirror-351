import os
import sys
import ctypes
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import shutil

REQUIRED_FILES = [
    # "libaoti_custom_ops.so",
    # "libbackend_with_compiler.so",
    "libc10.so",
    # "libjitbackend_test.so",
    # "libnnapi_backend.so",
    # "libshm.so",
    "libtorch.so",
    "libtorch_cpu.so",
    # "libtorch_global_deps.so",
    # "libtorch_python.so",
    # "libtorchbind_test.so",
]

def download_libtorch():
    # URL e arquivo zip
    libtorch_cpu_zip = "libtorch-cxx11-abi-shared-with-deps-2.5.0+cpu.zip"
    libtorch_cpu_url = (
        "https://download.pytorch.org/libtorch/cpu/"
        "libtorch-cxx11-abi-shared-with-deps-2.5.0%2Bcpu.zip"
    )
    
    # Caminho base: d_libs/
    pkg_dir = os.path.join(os.path.dirname(__file__), "d_libs")
    libtorch_dir = os.path.join(pkg_dir, "libtorch")
    cpu_dir = os.path.join(libtorch_dir, "cpu")
    lib_path = os.path.join(cpu_dir, "lib")  # É aqui que os .so devem estar

    # 1) Verifica se todos os arquivos necessários já existem
    all_files_present = True
    if os.path.exists(lib_path):
        for f in REQUIRED_FILES:
            if not os.path.exists(os.path.join(lib_path, f)):
                all_files_present = False
                break
    else:
        all_files_present = False

    if all_files_present:
        # print("All required files are already present in:", lib_path)
        return
    else:
        print("Not all files are present. Downloading libtorch...")

    # 2) Se faltou algum arquivo, remove tudo e baixa novamente
    if os.path.exists(pkg_dir):
        shutil.rmtree(pkg_dir)
    os.makedirs(libtorch_dir, exist_ok=True)

    # Baixa o arquivo zip
    subprocess.check_call(["wget", libtorch_cpu_url, "-O", libtorch_cpu_zip])

    # Descompacta no libtorch_dir
    subprocess.check_call(["unzip", "-o", libtorch_cpu_zip, "-d", libtorch_dir])

    # Renomeia libtorch -> cpu
    extracted_dir = os.path.join(libtorch_dir, "libtorch")
    if os.path.exists(extracted_dir):
        os.rename(extracted_dir, cpu_dir)
    else:
        print("Error: extracted_dir does not exist")

    # Remove o zip
    os.remove(libtorch_cpu_zip)
    print("Libtorch downloaded and extracted successfully.")

    # Só para debug, lista o que ficou em d_libs/
    result = subprocess.run(["ls", pkg_dir], capture_output=True, text=True)
    print("Conteúdo de d_libs/:", result.stdout)

download_libtorch()

LIB_PATH = os.path.join(os.path.dirname(__file__), "d_libs", "libtorch", "cpu", "lib")

# Pegando o valor atual do LD_LIBRARY_PATH ou uma string vazia se não existir
current_ld_library_path = os.environ.get("LD_LIBRARY_PATH", "")

# Criando o novo LD_LIBRARY_PATH garantindo que os caminhos não sejam sobrescritos
new_ld_library_path = f"{LIB_PATH}:/usr/local/lib:{current_ld_library_path}".strip(":")

# Atualizando a variável de ambiente
os.environ["LD_LIBRARY_PATH"] = new_ld_library_path
# Carrega manualmente as bibliotecas necessárias, *antes* de importar o módulo C++
try:
    #ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libaoti_custom_ops.so"))
    #ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libbackend_with_compiler.so"))
    ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libc10.so"))
    #ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libjitbackend_test.so"))
    #ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libnnapi_backend.so"))
    #ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libshm.so"))
    ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libtorch.so"))
    ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libtorch_cpu.so"))
    #ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libtorch_global_deps.so"))
    #ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libtorch_python.so"))
    #ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH, "libtorchbind_test.so"))
    # ... e assim por diante, se houver mais .so que o PyTorch exija
except OSError as e:
    # Se quiser, você pode tratar o erro aqui de forma mais amigável
    raise ImportError(f"Não foi possível carregar libtorch: {e}")

# Só agora importamos o módulo compilado,
# que depende de libtorch.so etc.

from .purecpp_chunks_clean_dev import *
from .purecpp_meta_dev import *
from .purecpp_extract_dev import *
from .purecpp_embed_dev import *
from .purecpp_libs_dev import *

from . import purecpp_chunks_clean_dev
from . import purecpp_meta_dev
from . import purecpp_extract_dev
from . import purecpp_embed_dev
from . import purecpp_libs_dev