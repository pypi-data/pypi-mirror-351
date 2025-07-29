"""
Operator Kernel Performance Benchmarking Script

This script benchmarks operator kernels using a specified inference module.
It supports timing measurements and (optionally) output comparisons with ONNXRuntime.
The configuration is provided via a JSON file.
"""

import argparse
import copy
from importlib import import_module, resources
import json
import os
import sys
from typing import Any

import numpy as np
import onnx

import aidge_core as ai
import aidge_onnx
from aidge_onnx.generate_singleop_onnx import create_onnx_model
from . import tree_structure
from . import logger
from . import manage_config

COLOR_ON = True

def show_available_config():
    config_dir = resources.files("aidge_core.benchmark.operator_config")
    config_files = [f for f in config_dir.iterdir() if f.is_file() and (f.suffix == ".json")]
    nb_files = len(config_files)
    tree = tree_structure.TreeStruct()
    print("Available configuration files")
    for i, cf in enumerate(config_files):
        print(f"{tree.grow(False, i >= nb_files - 1)} {cf.name}")


def load_inference_module(module_name: str):
    """
    Dynamically imports and returns the inference module.
    Exits if the module is not installed.
    """
    try:
        return import_module(module_name)
    except ImportError:
        return None


def measure_inference_time(
    module_name: str, model: onnx.ModelProto, input_data, nb_warmups, nb_iterations, inference_module=None
) -> list[float]:
    """
    Measures inference time using the appropriate benchmark function.
    """
    if module_name == "onnxruntime":
        from . import benchmark_onnxruntime

        return benchmark_onnxruntime.measure_inference_time(
            model, {v[0]: v[1] for v in input_data}, nb_warmups, nb_iterations
        )
    elif module_name == "torch":
        from . import benchmark_torch

        return benchmark_torch.measure_inference_time(
            model, {v[0]: v[1] for v in input_data}, nb_warmups, nb_iterations
        )
    else:
        model = aidge_onnx.convert_onnx_to_aidge(model=model) if "aidge" in module_name else model
        return inference_module.benchmark.measure_inference_time(
            model, input_data, nb_warmups, nb_iterations
        )


def compute_output(
    module_name: str, model: onnx.ModelProto, input_data, inference_module
) -> list[np.ndarray]:
    """
    Measures inference time using the appropriate benchmark function.
    """
    if module_name == "onnxruntime":
        from . import benchmark_onnxruntime

        return benchmark_onnxruntime.compute_output(
            model, {v[0]: v[1] for v in input_data}
        )
    elif module_name == "torch":
        from . import benchmark_torch

        return benchmark_torch.compute_output(model, {v[0]: v[1] for v in input_data})
    else:
        if "aidge" in module_name:
            model = aidge_onnx.convert_onnx_to_aidge(model=model)
            # TODO: find a way to catch if an Operator is not implemented for a backend/exportLib
        return inference_module.benchmark.compute_output(model, input_data)


def update_missing_inputs_with_random(
    input_properties: dict[str, Any]) -> list[str, np.ndarray]:
    """
    Generates random input data for the each `initializer_rank` inputs NOT ALREADY FIXED and returns them in a list .
    """
    for prop in input_properties:
        manage_config.validate_property(prop)
        if prop["values"] is None and prop["dims"] is not None: # not optional input
            prop["values"] = np.array(np.random.rand(*prop["dims"])).astype(np.float32)

def main():
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--show-available-config", action="store_true")
    known_args, _ = pre_parser.parse_known_args()

    # Handle --show-available-config early and exit
    if known_args.show_available_config:
        show_available_config()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Operator Kernel Performance Benchmarking across multiple inference modules."
    )

    parser.add_argument(
        "--show-available-config",
        action="store_true",
        help="show JSON configuration files stored in the standard configuration directory."
    )
    onnx_model_group = parser.add_mutually_exclusive_group(required=True)
    onnx_model_group.add_argument(
        "--config-file",
        "-cf",
        type=str,
        help="Path to a JSON configuration file containing an ONNX operator description with reference and tested parameter values. A new ONNX model will automatically be generated for each test case. Cannot be specified with '--onnx-file' option",
    )
    onnx_model_group.add_argument(
        "--onnx-file",
        "-of",
        type=str,
        help="Path to an existing ONNX file that will be used for benchmarking. Cannot be specified with '--config-file' option.",
    )
    parser.add_argument(
        "--modules",
        "-m",
        type=str,
        nargs="+",
        required=True,
        help="List of inference module names to benchmark (e.g., 'torch', 'onnxruntime').",
    )
    parser.add_argument(
        "--time",
        "-t",
        action="store_true",
        help="Measure inference time for each module."
    )
    parser.add_argument(
        "--nb-iterations",
        type=int,
        default=50,
        help="Number of iterations to run for the 'time' test (default: 50)."
    )
    parser.add_argument(
        "--nb-warmups",
        type=int,
        default=10,
        help="Number of warmup steps to run for the 'time' test (default: 10)."
    )
    parser.add_argument(
        "--compare",
        "-c",
        action="store_true",
        help="Compare the inference outputs of each module against a reference implementation.",
    )
    parser.add_argument(
        "--ref",
        type=str,
        default="onnxruntime",
        help="Reference module used for comparing results (default: 'onnxruntime').",
    )
    parser.add_argument(
        "--results-directory",
        type=str,
        default="benchmark_results",
        help="Directory to save the benchmarking results",
    )
    parser.add_argument(
        "--results-filename",
        type=str,
        required=False,
        default="",
        help="Name of the saved result file. If not provided, it will default to the '<operator_name>_<module_to_bench>.json'. If a file with that nae and at tha location already exists, it will be overrided with elements individually replaced only if new ones are computed"
    )
    args = parser.parse_args()

    log = logger.Logger(COLOR_ON)

    COMPARE: bool = args.compare
    TIME: bool = args.time

    NB_WARMUPS: int = args.nb_warmups
    NB_ITERATIONS: int = args.nb_iterations

    tree = tree_structure.TreeStruct() # structure informations about the script execution

    modules: list[dict] = [{"name": m_name} for m_name in args.modules]
    NB_MODULES = len(args.modules)

    print("Loading modules...")
    ref_module_name: str = args.ref
    ref_module = None
    if COMPARE and (ref_module_name not in list(m["name"] for m in modules)):
        ref_module = load_inference_module(ref_module_name)
        print(f"{tree.grow(branch=False, leaf=False )}{ref_module_name} ", end="")
        if ref_module:
            print(f"[ {log.to_color('ok', logger.Color.GREEN)} ]")
        else :
            print(f"[ {log.to_color('xx', logger.Color.RED)} ]")
            sys.exit(1)

    # Load the inference module
    for m_id, m in enumerate(modules):
        m["module"] = load_inference_module(m["name"])
        if (m["name"] != ref_module_name) or not COMPARE:
            print(f"{tree.grow(branch=False, leaf= (m_id >= NB_MODULES - 1))}{m["name"]} ", end='')
            if m["module"]:
                print(f"[ {log.to_color('ok', logger.Color.GREEN)} ]")
            else :
                print(f"[ {log.to_color('xx', logger.Color.RED)} ]")
                sys.exit(1)

    # Configure aidge logging
    ai.Log.set_console_level(ai.Level.Warn)
    ai.Log.set_precision(10)

    if args.onnx_file:
        ai.Log.fatal("ONNX single file not supported yet")
        sys.exit(1)

    # Load configuration
    config = manage_config.load_json(args.config_file)
    operator_name: str = config["operator"]
    opset_version: int = config["opset_version"]
    initializer_rank: int = config.get("initializer_rank", 1)

    test_meta_data: dict[str, Any] = config["test_meta_data"]
    if test_meta_data["multiple_batchs"] == True and "export" in list(m["name"] for m in modules):
        ai.Log.warn("The tested module seems to be an export module and your test cases contains "
            "\033[31;1;multiple\033[0m batchs inputs. This could lead to inaccurate results due to "
            "the stream-based (single batch) nature of exports implementations, or an error during "
            "export the 'export generation' step. Unless you know what you are doing, you should "
            "probably change your configuration file for single batch tests.")

    # set every config to the format
    # {"attributes": {},
    #  "input_properties": [
    #       {"name": "",
    #        "dims": [],
    #        "values":[]
    #        }
    #    ]
    # }
    manage_config.clean_benchmark_configuration(config)

    # Initialize or load existing benchmark results
    results_directory = os.path.expanduser(args.results_directory)
    if not os.path.isdir(results_directory):
        print("Creating result directory at: ", results_directory)
        os.makedirs(results_directory, exist_ok=True)
    base_result_filename: str = ((args.results_filename + '_') if args.results_filename else "") + (f"{operator_name.lower()}" if args.config_file else args.onnx_file) + '_'
    for m in modules:
        m["result_file_path"] = os.path.join(results_directory, base_result_filename + f'{m["name"]}.json')
        m["results"] = {"library": m["name"], "compare": {}, "time": {}}
        for param in config["test_configurations"].keys():
            m["results"]["time"][param] = {}
            m["results"]["compare"][param] = {}

    # we override existing file
    # if os.path.exists(results_file_path):
    #     with open(results_file_path, "r") as f:
    #         results = json.load(f)

    # Loop over each test parameter and its values
    tree.reset()
    print("\nStarting tests...")
    for param, test_values in config["test_configurations"].items():
        for value_str, test_config in test_values.items():
            # at this stage, each test configuration is "valid"
            print(f"▷ {param} -- {value_str}")
            updated_config = manage_config.merge_test_with_base_configuration(test_config, config["base_configuration"])
            update_missing_inputs_with_random(updated_config["input_properties"])

            # Create the updated ONNX model
            model: onnx.ModelProto
            if args.config_file:
                model = create_onnx_model(
                    operator_name,
                    opset_version,
                    updated_config["input_properties"],
                    initializer_rank,
                    **updated_config["attributes"],
                )
            elif args.onnx_file:
                model = aidge_onnx.load_onnx(args.onnx_file)
            else:
                ai.Log.fatal("No ONNX model to generate or load. Ending the script.")
                sys.exit(1)

            input_data = [(updated_config["input_properties"][i]["name"], updated_config["input_properties"][i]["values"]) for i in range(initializer_rank)]
            for m_id, m in enumerate(modules):
                print(f"{tree.grow(branch=True, leaf= (m_id >= NB_MODULES - 1))}{m["name"]}")
                if TIME:
                    print(f"{tree.grow(branch=False, leaf=not COMPARE)}time ", end='')
                    timing = measure_inference_time(m["name"], model, input_data, NB_WARMUPS, NB_ITERATIONS, m["module"])
                    m["results"]["time"][param][value_str] = timing
                    time_str = f"[ {np.array(timing).mean():.2e} ± {np.array(timing).std():.2e} ] (seconds)"
                    print(time_str)

                if COMPARE:
                    print(f"{tree.grow(branch=False, leaf=True)}comp ", end='')
                    ref = compute_output(ref_module_name, model, input_data, ref_module)
                    tested = compute_output(m["name"], model, input_data, m["module"])
                    if len(ref) > 1:
                        print("Multi-output comparison not handled yet")
                        print([i.shape for i in ref])
                        sys.exit(1)
                    res = bool(np.all(np.isclose(ref, tested, rtol=1e-3, atol=1e-5)))
                    m["results"]["compare"][param][value_str] = res
                    comp_str = f"[ {log.to_color('ok', logger.Color.GREEN) if res else log.to_color('xx', logger.Color.RED)} ]"
                    print(f"{comp_str}")
            print()

    # Save results
    tree.reset()
    print("Saving resutls to JSON files...")
    for m_id, m in enumerate(modules):
        with open(m["result_file_path"], "w") as outfile:
            print(f"{tree.grow(branch=False, leaf= (m_id >= NB_MODULES - 1))}'{m["result_file_path"]}'")
            json.dump(m['results'], outfile, indent=4)


if __name__ == "__main__":
    main()
