import argparse
import json
import sys
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import manage_config

# Set a default style
sns.set_theme(style="ticks", palette="flare")


def parse_args():
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--show-available-config", action="store_true")
    known_args, _ = pre_parser.parse_known_args()

    # Handle --show-available-config early and exit
    if known_args.show_available_config:
        manage_config.show_available_config()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Compare time performance of operator kernels by plotting relative differences."
    )
    parser.add_argument(
        "--operator-config", "-oc", type=str, default="config.json",
        help="Path to the configuration JSON file (default: config.json)"
    )
    parser.add_argument(
        "--results-directory", type = str, default="benchmark_results",
        help="Directory to add to the search path for results."
    )
    parser.add_argument(
        "--ref", "-r", type=str, required=True,
        help="Path to the JSON file with reference results"
    )
    parser.add_argument(
        "--libs", "-l", type=str, nargs='+', required=True,
        help=("Paths to one or more JSON files with library results. For violin/box mode, "
              "exactly one file must be provided. For bar mode, multiple files can be provided.")
    )
    # parser.add_argument(
    #     "--plot-type", "-pt", type=str, choices=["violin", "box", "bar"], default="violin",
    #     help="Type of plot to use: 'violin', 'box', or 'bar' (default: violin)"
    # )
    return parser.parse_args()

def create_relative_difference_plots(test_parameters: dict, ref_times: dict, ref_library: str,
                                       plot_type: str, new_times: dict = None, new_library: str = None,
                                       libraries: list = None):
    """
    Creates subplots comparing relative differences.

    For "violin" and "box" modes, `new_times` and `new_library` are used.
    For "bar" mode, a list of library tuples (library_name, times) in `libraries` is used.
    In bar mode the reference library (ref_library) is always added as the baseline (ratio = 1).
    """
    n_params = len(test_parameters)
    n_cols = 1
    if n_params > 1:
        if n_params == 2 or n_params == 4:
            n_cols = 2
        else:
            n_cols = 3

    n_rows = (n_params + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(10 if n_params == 1 else 15, 5 * n_rows))
    # Ensure axes is always iterable
    if n_params == 1:
        axes = [axes]
    axes_flat = axes.flatten() if n_params > 1 else axes

    for idx, (param_name, param_values) in enumerate(test_parameters.items()):
        ax = axes_flat[idx]
        # if plot_type in ["violin", "box"]:
        #     # Compute relative differences (%) per run
        #     plot_data = []
        #     for val in param_values:
        #         new_arr = np.array(new_times[param_name][str(val)])
        #         ref_arr = np.array(ref_times[param_name][str(val)])
        #         rel_diff = (new_arr - ref_arr) / ref_arr * 100
        #         plot_data.extend([(str(val), diff) for diff in rel_diff])
        #     df = pd.DataFrame(plot_data, columns=[f'{param_name} Value', 'Relative Difference (%)'])
        #     # Optionally filter extreme outliers using IQR
        #     for col in df.select_dtypes(include='number').columns:
        #         Q1 = df[col].quantile(0.25)
        #         Q3 = df[col].quantile(0.75)
        #         IQR = Q3 - Q1
        #         lower_bound = Q1 - IQR
        #         upper_bound = Q3 + IQR
        #         df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        #     if plot_type == "violin":
        #         sns.violinplot(
        #             data=df,
        #             x=f'{param_name} Value',
        #             y='Relative Difference (%)',
        #             hue=f'{param_name} Value',
        #             palette='flare',
        #             inner='quartile',
        #             ax=ax
        #         )
        #     else:  # box plot
        #         sns.boxplot(
        #             data=df,
        #             x=f'{param_name} Value',
        #             y='Relative Difference (%)',
        #             hue=f'{param_name} Value',
        #             palette='flare',
        #             ax=ax
        #         )
        #     if ax.get_legend() is not None:
        #         ax.legend_.remove()
        #     ax.grid(True, axis='y', alpha=0.5, color='gray')
        #     ax.axhline(y=0, color='red', linewidth=1)
        #     ax.set_ylim(-30, 150)
        #     stats_text = (f'Mean: {df["Relative Difference (%)"].mean():.2f}%\n'
        #                   f'Std: {df["Relative Difference (%)"].std():.2f}%')
        #     ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
        #             verticalalignment='top',
        #             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        # elif plot_type == "bar":
            # For bar plots: compute the median time ratio for each library compared to reference
        data = []
        for val in param_values:
            data.append((str(val), ref_library, 1.0))  # Reference baseline (ratio = 1)
            for lib_name, lib_times in libraries:
                lib_arr = np.array(lib_times[param_name][str(val)])
                ref_arr = np.array(ref_times[param_name][str(val)])
                median_lib = np.median(lib_arr)
                median_ref = np.median(ref_arr)
                ratio = median_lib / median_ref if median_ref != 0 else np.nan
                data.append((str(val), lib_name, ratio))
        df_bar = pd.DataFrame(data, columns=[f'{param_name}', 'Library', 'Ratio'])
        sns.barplot(
            data=df_bar,
            x=f'{param_name}',
            y='Ratio',
            hue='Library',
            palette='hls',
            ax=ax,
            errorbar=None
        )
        ax.grid(True, axis='y', alpha=0.5, color='gray')
        # Annotate bars with their ratio values
        for container in ax.containers:
            labels = [f'{h:.2f}' if h > 1e-6 else '' for h in container.datavalues]
            ax.bar_label(container, labels=labels, padding=3)
        ax.set_ylim(0, max(df_bar['Ratio'].max() * 1.1, 1.1))
        # else:
        #     ax.text(0.5, 0.5, "Unknown plot type", horizontalalignment='center', verticalalignment='center')

    # Remove any unused subplots
    for idx in range(len(test_parameters), len(axes_flat)):
        fig.delaxes(axes_flat[idx])
    if n_params == 1:
        plt.tight_layout(rect=[0, 0.05, 1, 0.88])
    else:
        plt.tight_layout(rect=[0, 0.05, 1, 0.93])

    # Create a common legend (if any) at the top center
    common_handles, common_labels = None, None
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is not None:
            common_handles, common_labels = ax.get_legend_handles_labels()
            break
    if common_handles is not None and common_labels is not None:
        fig.legend(common_handles, common_labels, loc='upper center', ncol=len(common_labels),
                   bbox_to_anchor=(0.5, 0.99), title="Library")
    # Remove legends from individual subplots
    for ax in axes_flat:
        if ax.get_legend() is not None:
            ax.get_legend().remove()
    return fig


def main():
    args = parse_args()
    config = manage_config.load_json(args.operator_config)
    ref_results = manage_config.load_json(args.ref, args.results_directory)
    library_files = args.libs

    operator = config["operator"]
    test_parameters = config["test_configurations"]

    # Load reference times and library name from reference JSON
    ref_times = ref_results.get("time")
    ref_library = ref_results.get("library", "ref_lib")
    if ref_times is None:
        print("Reference JSON does not contain time results.")
        sys.exit(1)

    # if args.plot_type in ["violin", "box"]:
    #     if len(library_files) != 1:
    #         print("Error: For violin/box mode, exactly one library JSON file must be provided.")
    #         sys.exit(1)
    #     comp_results = load_json(library_files[0])
    #     comp_times = comp_results.get("time")
    #     comp_library = comp_results.get("library", "comp_lib")
    #     if comp_times is None:
    #         print("Library JSON does not contain time results.")
    #         sys.exit(1)
    #     fig = create_relative_difference_plots(
    #         test_parameters, ref_times, ref_library,
    #         plot_type=args.plot_type, new_times=comp_times, new_library=comp_library
    #     )
    #     filename = f"{operator}_comp_{comp_library}-vs-{ref_library}.svg"
    # elif args.plot_type == "bar":
    libraries = []
    for lib_file in library_files:
        lib_result = manage_config.load_json(lib_file, args.results_directory)
        lib_times = lib_result.get("time")
        lib_name = lib_result.get("library", "lib")
        if lib_times is None:
            print(f"Library JSON {lib_file} does not contain time results. Skipping.")
            continue
        libraries.append((lib_name, lib_times))
    if not libraries:
        print("No valid library results available for bar plot.")
        sys.exit(1)
    fig = create_relative_difference_plots(
        test_parameters, ref_times, ref_library,
        plot_type="bar", libraries=libraries
    )
    # lib_names = "-".join([name for name, _ in libraries])
    filename = f"{operator}_inference_time_comparison.svg"
    # else:
    #     print("Unsupported plot type.")
    #     sys.exit(1)

    ##############################
    # Prepare footer texts
    footer_title = f'[{operator}] kernel relative inference time comparison'
    default_config = config.get("base_configuration", {})

    # Wrap the default configuration text to a given width.
    wrapped_config = textwrap.wrap(f'Base configuration: {default_config}', width=160)
    n_lines = len(wrapped_config)
    config_text = "\n".join(wrapped_config)

    # Adjust the figure layout to provide extra space at the bottom.
    if len(test_parameters) == 1:
        plt.subplots_adjust(bottom=0.2+0.02*n_lines)
    else:
        plt.subplots_adjust(bottom=0.14+0.02*n_lines)

    # Add the footer title (bottom center) with fontsize 16.
    fig.text(0.5, 0.035+n_lines*0.025, footer_title, ha='center', va='bottom', fontsize=18)

    # Add the default configuration text just below the title with the computed fontsize.
    fig.text(0.5, 0.02, config_text, ha='center', va='bottom', fontsize=12)

    ############################
    # save
    plt.savefig(filename)
    print(f"Plot saved as {filename}")


if __name__ == "__main__":
    main()
