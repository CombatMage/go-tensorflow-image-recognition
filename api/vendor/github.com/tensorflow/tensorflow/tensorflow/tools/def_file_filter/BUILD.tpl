# Description:
# Tools for filtering DEF file for TensorFlow on Windows
#
# On Windows, we use a DEF file generated by Bazel to export
# symbols from the tensorflow dynamic library(_pywrap_tensorflow.dll).
# The maximum number of symbols that can be exported per DLL is 64K,
# so we have to filter some useless symbols through this python script.

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "def_file_filter",
    srcs = ["def_file_filter.py"],
    srcs_version = "PY2AND3",
)
