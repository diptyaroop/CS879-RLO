#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/cdma_ref.cpp"
out_dir="${repo_root}/ref"

if [[ ! -f "${src}" ]]; then
  echo "Missing source file: ${src}" >&2
  exit 1
fi

mkdir -p "${out_dir}"

if ! command -v g++ >/dev/null 2>&1; then
  echo "g++ was not found in PATH. Install a C++ toolchain and retry." >&2
  exit 1
fi

uname_s="$(uname -s)"
if [[ "${uname_s}" == "Darwin" ]]; then
  out_lib="${out_dir}/libcdma_ref.dylib"
else
  out_lib="${out_dir}/libcdma_ref.so"
fi

echo "Building reference library..."
g++ -shared -fPIC -O2 "${src}" -o "${out_lib}"
echo "Done: ${out_lib}"
