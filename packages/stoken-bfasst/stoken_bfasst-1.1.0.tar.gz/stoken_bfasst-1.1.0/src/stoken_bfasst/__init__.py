from stoken_bfasst_core import library_loader as _loader, ctypes as _ctypes

_lib = _ctypes.Lib(_ctypes.RawLib(_loader.load_library()))

Parameters = _ctypes.Parameters
generate_passcode = _lib.generate_passcode
search_seed = _lib.search_seed
params_from_time_blocks = _lib.params_from_time_blocks
params_from_token = _lib.params_from_token
