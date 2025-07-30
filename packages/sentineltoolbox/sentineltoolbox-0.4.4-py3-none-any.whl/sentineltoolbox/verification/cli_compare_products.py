# Copyright 2024 ACRI-ST
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import pprint
import sys
from io import TextIOWrapper
from typing import Any, Hashable, TextIO

import click
import deepdiff
import numpy as np
import xarray as xr
from xarray import DataTree

from sentineltoolbox.attributes import guess_product_type
from sentineltoolbox.readers.datatree_subset import filter_datatree, filter_flags
from sentineltoolbox.readers.open_datatree import open_datatree
from sentineltoolbox.verification.compare import (
    _get_failed_formatted_string_flags,
    _get_failed_formatted_string_vars,
    _get_passed_formatted_string_flags,
    bitwise_statistics,
    compute_confusion_matrix_for_dataarray,
    parse_cmp_vars,
    product_exists,
    sort_datatree,
    variables_statistics,
)
from sentineltoolbox.verification.logger import (
    get_failed_logger,
    get_logger,
    get_passed_logger,
)


def compare_products(
    reference: str,
    actual: str,
    cmp_vars: str | None = None,
    cmp_grps: str | None = None,
    verbose: bool = False,
    info: bool = False,
    relative: bool = False,
    absolute: bool = False,
    threshold: float = 0.01,
    threshold_nb_outliers: float = 0.01,
    threshold_coverage: float = 0.01,
    structure: bool = True,
    data: bool = True,
    flags: bool = True,
    secret: str | None = None,
    output: str | None = None,
    **kwargs: Any,
) -> tuple[DataTree | None, DataTree | None, float | None, list[float] | None] | RuntimeError:
    """Compare two products Zarr or SAFE.

    Parameters
    ----------
    reference: Path
        Reference product path
    actual: Path
        New product path
    verbose: bool
        2-level of verbosity (INFO or DEBUG)
    info: bool
        Display statistics even if PASSED
    relative: bool
        Compute relative error (default for non-packed variables)
    absolute: bool
        Compute absolute error (default for packed variables)
    threshold: float
        Maximum allowed threshold defining the PASSED/FAILED result.
        In relative mode, this is a float between 0 and 1 (e.g. 0.01 for 1%).
        In absolute mode, packed variables use an hardcoded threshold of 1.5 * scale_factor.
    threshold_nb_outliers: float
        Maximum allowed relative number of outliers as a float between 0 and 1 (e.g. 0.01 for 1% outliers).
    threshold_coverage: float
        Maximum allowed valid coverage relative difference as a float between 0 and 1 (e.g. 0.01 for 1%)
    structure: bool
        Compare product structure and metadata like Zarr metadata/attributes
    data: bool
        Compare variables data
    flags: bool
        Compare flags/masks variables
    """
    # Initialize stream
    stream: TextIOWrapper | TextIO
    if output:
        stream = open(output, mode="w")
    else:
        stream = sys.stderr

    # Initialize logging
    level = logging.INFO
    if verbose:
        level = logging.DEBUG
    logger = get_logger("compare", level=level, stream=stream)
    logger.setLevel(level)

    passed_logger = get_passed_logger("passed", stream=stream)
    failed_logger = get_failed_logger("failed", stream=stream)

    # Check input products
    if not product_exists(reference, secret=secret):
        logger.error(f"{reference} cannot be found.")
        exit(1)
    if not product_exists(actual, secret=secret):
        logger.error(f"{actual} cannot be found.")
        exit(1)
    logger.info(
        f"Compare the new product {actual} to the reference product {reference}",
    )

    # Check if specific variables
    if cmp_vars:
        list_ref_new_vars = parse_cmp_vars(reference, actual, cmp_vars)
    if cmp_grps:
        list_ref_new_grps = parse_cmp_vars(reference, actual, cmp_grps)

    kwargs["decode_times"] = False
    if secret:
        kwargs["secret_alias"] = secret
    # Open reference product
    dt_ref = open_datatree(reference, **kwargs)
    dt_ref.name = "ref"
    logger.debug(dt_ref)

    # Open new product
    dt_new = open_datatree(actual, **kwargs)
    dt_new.name = "new"
    logger.debug(dt_new)

    # Sort datatree
    dt_ref = sort_datatree(dt_ref)
    dt_new = sort_datatree(dt_new)

    # Get product type
    eopf_type = guess_product_type(dt_ref)

    # Filter datatree
    if cmp_vars:
        dt_ref = filter_datatree(
            dt_ref,
            [var[0] for var in list_ref_new_vars],
            type="variables",
        )
        dt_new = filter_datatree(
            dt_new,
            [var[1] for var in list_ref_new_vars],
            type="variables",
        )
    if cmp_grps:
        dt_ref = filter_datatree(
            dt_ref,
            [var[0] for var in list_ref_new_grps],
            type="groups",
        )
        dt_new = filter_datatree(
            dt_new,
            [var[1] for var in list_ref_new_grps],
            type="groups",
        )

    # Check if datatrees are isomorphic
    if not dt_new.isomorphic(dt_ref):
        logger.error("Reference and new products are not isomorphic")
        logger.error("Comparison fails")
        raise RuntimeError

    # Compare structure and metadata if requested
    if structure:
        logger.info("-- Verification of structure and metadata")
        skip_data_comparison = compare_datatrees_structure(dt_ref, dt_new, passed_logger, failed_logger)
        if skip_data_comparison:
            logger.error("Reference and new products have fatal structure differences")
            logger.error("Comparison fails")
            raise RuntimeError

    # Variable statistics
    score: float | None = 0
    err = None
    if data:
        results, err = variables_statistics(dt_new, dt_ref, relative, absolute, threshold)

        logger.info("-- Verification of variables data")
        for name, val in results.items():
            if name.endswith("spatial_ref") or name.endswith("band"):
                continue
            # Check if the number of outliers is within the allowed threshold
            outliers_ratio = val[7] / val[9]  # outliers / total pixels
            # Check if the valid coverage difference is within the allowed threshold
            coverage_diff_ratio = val[10] / val[9]  # valid pixels / total pixels
            if (outliers_ratio <= threshold_nb_outliers) and (np.abs(coverage_diff_ratio) <= threshold_coverage):
                if info:
                    passed_logger.info(
                        _get_failed_formatted_string_vars(
                            name,
                            val,
                            threshold_nb_outliers,
                            threshold_coverage,
                        ),
                    )
                else:
                    passed_logger.info(f"{name}")
            else:
                failed_logger.info(
                    _get_failed_formatted_string_vars(
                        name,
                        val,
                        threshold_nb_outliers,
                        threshold_coverage,
                    ),
                )

        # Global scoring:
        if relative:
            score = 100.0 - np.abs(np.nanmedian([np.abs((res[2] + res[4]) * 0.5) for res in results.values()]) * 100)
            logger.debug(
                """Metrics is: 100% - |median_over_variables(0.5 * (
                                    (1 / npix) *sum_npix(err_rel[p]) + median_pix(err_rel[p])
                                    ) * 100|

                        with err_rel[p] = (val[p] - ref[p]) / ref[p]
                        """,
            )
            logger.info(f"   Global scoring for non-flag variables = {score:20.12f}%")
        else:
            # # score = np.median([(res[2] + res[4] + np.max([0, 1 - res[6] / 30])) / 3 for res in results.values()])
            # score = np.median([(res[2] + res[4]) / 2 for res in results.values()])
            # logger.debug(
            #     # """Metrics is: median_over_variables( 1/3 * (
            #     #             (1 / npix) *sum_npix(err[p]) + median_pix(err[p]) + max(0,1-psnr/30)
            #     """Metrics is: median_over_variables( 1/2 * (
            #                 (1 / npix) *sum_npix(err[p]) + median_pix(err[p])
            #                         )

            #             with err[p] = val[p] - ref[p]
            #             """,
            # )
            # logger.info(f"   Global precision for non-flag variables is = {score:20.12f}")
            score = None

    score_flag: list[float] = []
    err_flags = None
    if flags:
        # Flags statistics
        flags_ref = filter_flags(dt_ref)
        flags_new = filter_flags(dt_new)

        res: dict[str, xr.Dataset] = {}

        # Patch for S2 L2
        # Attributes for reference product are not correct so that filtering flags is ineffective
        # TODO: for exclusive flags (detected on attributes=flag_values), use the confusion matrix
        # instead of the bitwise statistics which is not correct
        try:
            if eopf_type in [
                "S02MSIL1C",
                "S02MSIL2A",
            ]:
                patch_s2l2 = True
            else:
                patch_s2l2 = False
        except KeyError:
            patch_s2l2 = False

        if patch_s2l2:
            score_flag_scl = compute_confusion_matrix_for_dataarray(
                dt_ref.conditions.mask.l2a_classification.r20m.scl,
                dt_new.conditions.mask.l2a_classification.r20m.scl,
                normalize="true",
            )
            score_flag.append(score_flag_scl)
            err_flags = None
            logger.info(f"   Score for scene classification is = {score_flag[0]}")
        else:
            try:
                with xr.set_options(keep_attrs=True):
                    err_flags = flags_ref ^ flags_new
            except TypeError:
                pass
            else:
                res = bitwise_statistics(err_flags)
                eps = 100.0 * threshold_nb_outliers
                logger.info("-- Verification of flags")
                for name, ds in res.items():
                    for bit in ds.index.data:
                        if ds.different_percentage[bit] > eps:
                            failed_logger.info(
                                _get_failed_formatted_string_flags(name, ds, bit, threshold_nb_outliers),
                            )
                        else:
                            passed_logger.info(
                                _get_passed_formatted_string_flags(name, ds, bit),
                            )

            # Global scoring for flags
            # score_flag: list[float] = []
            for name, ds in res.items():
                score_var: float = 0
                sum_weight: float = 0
                for bit in ds.index.data:
                    weight = ds.equal_count.data[bit] + ds.different_count.data[bit]
                    sum_weight += weight
                    score_var = score_var + ds.equal_percentage.data[bit] * weight
                score_var /= sum_weight
                score_flag.append(score_var)

            logger.info(f"   Scores for flag variables are = {score_flag}")
            logger.info(f"   Global scores for flag variables is = {np.nanmedian(score_flag)   :20.12f}")

    logger.info("Exiting compare")

    if output:
        stream.close()

    return err, err_flags, score, score_flag


def compare_datatrees_structure(
    dt_ref: DataTree,
    dt_new: DataTree,
    passed_logger: logging.Logger,
    failed_logger: logging.Logger,
) -> bool:
    """
    Compare the structure of two DataTree objects except variables data, log differences and
    return a flag to skip variables data comparison when fatal differences are found
    (e.g. dimensions or shape are different for at least one variable).

    Traverses through all nodes in the reference DataTree and compares them with corresponding
    nodes in the new DataTree. For each node, it compares dataset and variable objects fields,
    attributes, encoding, etc... and logs whether they are identical or different.

    Args:
        dt_ref: Reference DataTree to compare against
        dt_new: New DataTree being compared
        passed_logger: Logger for recording successful comparisons
        failed_logger: Logger for recording failed comparisons or differences

    Returns:
        True if variables data comparison should be skipped, False otherwise.
    """

    skip_data_comparison = False

    for ref_node in dt_ref.subtree:
        ref_path = ref_node.path

        # Check if the node exists in the new product
        try:
            new_node = dt_new[ref_path]
        except KeyError:
            failed_logger.info(f"{ref_path}: Node exists in reference but not in new product")
            continue

        ref_ds = ref_node.to_dataset()
        new_ds = new_node.to_dataset()

        # Compare dataset fields
        for field, ref_obj, new_obj in get_fields_for_comparisons(ref_ds, new_ds):
            diff = deepdiff_compare_objects(ref_obj, new_obj)
            if diff:
                failed_logger.info(f"{ref_path}: {field} fields are not identical:\n{diff}")

        # Compare variables fields
        for ref_var in ref_ds.values():
            new_var = new_ds[ref_var.name]
            for field, ref_obj, new_obj in get_fields_for_comparisons(ref_var, new_var):
                diff = deepdiff_compare_objects(ref_obj, new_obj)
                if diff:
                    # Skip data comparison if variable dimensions or shape are different because
                    # it is not possible to compare the data in this case.
                    skip_data_comparison_message = ""
                    if field in ("dims", "shape"):
                        skip_data_comparison = True
                        skip_data_comparison_message = (
                            " (WARNING: variable dimensions or shape are different, "
                            "all variables data comparison will be skipped)"
                        )
                    failed_logger.info(
                        f"{ref_path}/{ref_var.name}: {field} fields are not identical{skip_data_comparison_message}:\n"
                        f"{diff}",
                    )

    return skip_data_comparison


def get_fields_for_comparisons(
    ref_obj: xr.Dataset | xr.DataArray,
    new_obj: xr.Dataset | xr.DataArray,
) -> tuple[Any, ...]:
    """
    Extract fields to compare from two xarray objects (Dataset or DataArray).

    Args:
        ref_obj: Reference object (Dataset or DataArray)
        new_obj: Object to compare against the reference (must be same type as ref_obj)

    Returns:
        A tuple of tuples containing field names to compare, with their values from both objects
    """
    if not isinstance(ref_obj, type(new_obj)):
        raise TypeError(f"Objects must be of the same type, got {type(ref_obj)} and {type(new_obj)}")

    # Common fields for both Dataset and DataArray
    common_fields: list[tuple[str, Any, Any]] = [
        ("attrs", ref_obj.attrs, new_obj.attrs),
        ("chunks", ref_obj.chunks, new_obj.chunks),
        ("chunksizes", ref_obj.chunksizes, new_obj.chunksizes),
        ("coords", list(ref_obj.coords), list(new_obj.coords)),
        ("encoding", dict_remove_keys(ref_obj.encoding, ["source"]), dict_remove_keys(new_obj.encoding, ["source"])),
        ("nbytes", ref_obj.nbytes, new_obj.nbytes),
        ("sizes", ref_obj.sizes, new_obj.sizes),
    ]

    ds_fields: list[tuple[str, Any, Any]]
    if isinstance(ref_obj, xr.Dataset):
        # Dataset specific fields
        ds_fields = [
            ("data_vars", list(ref_obj.data_vars), list(new_obj.data_vars)),
        ]
        fields = common_fields + ds_fields
    else:  # DataArray
        # DataArray specific fields
        da_fields = [
            ("dims", ref_obj.dims, new_obj.dims),
            ("dtype", ref_obj.dtype, new_obj.dtype),
            ("name", ref_obj.name, new_obj.name),
            ("shape", ref_obj.shape, new_obj.shape),
        ]
        fields = common_fields + da_fields

    return tuple(fields)


def dict_remove_keys(d: dict[Hashable, Any], keys: list[str]) -> dict[Hashable, Any]:
    """
    Remove specified keys from a dictionary.

    Args:
        d: Input dictionary
        keys: List of keys to remove from the dictionary

    Returns:
        A new dictionary with the specified keys removed
    """
    return {k: v for k, v in d.items() if k not in keys}


def deepdiff_compare_objects(ref_obj: Any, new_obj: Any) -> str | None:
    """
    Compare two objects using DeepDiff and return a formatted representation of the differences.

    Args:
        ref_obj: Reference object
        new_obj: Object to compare against the reference

    Returns:
        A formatted string describing the differences between objects if any differences exist,
        None otherwise
    """
    ddiff = deepdiff.DeepDiff(ref_obj, new_obj, threshold_to_diff_deeper=0)
    if ddiff:
        return pprint.pformat(ddiff, width=120)
        # Below an alternative using DeepDiff pretty print, but it doesn't show (for example) new coords name.
        # return ddiff.pretty()
    else:
        return None


@click.command()
@click.argument("reference", type=str, nargs=1, required=True)
@click.argument("actual", type=str, nargs=1, required=True)
@click.option(
    "--cmp-vars",
    type=str,
    help="Compare only specific variables, defined as: path/to/var_ref:path/to/var_new,... ",
)
@click.option(
    "--cmp-grps",
    type=str,
    help="Compare only specific groups, defined as: path/to/grp_ref:path/to/grp_new,... ",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    show_default=True,
    help="increased verbosity",
)
@click.option(
    "--info",
    is_flag=True,
    default=False,
    show_default=True,
    help="always display statistics even if PASSED",
)
# We do not use the https://click.palletsprojects.com/en/stable/options/#feature-switches
# because no error is automatically raised if both --relative and --absolute options are used.
@click.option(
    "--relative",
    is_flag=True,
    default=False,
    show_default=True,
    help="Compute relative error (default for non-packed variables)",
    cls=click.Option,
    is_eager=True,
)
@click.option(
    "--absolute",
    is_flag=True,
    default=False,
    show_default=True,
    help="Compute absolute error (default for packed variables)",
    cls=click.Option,
    is_eager=True,
)
@click.option(
    "--threshold",
    required=False,
    type=float,
    default=0.01,
    show_default=True,
    help="Maximum allowed threshold defining the PASSED/FAILED result. "
    "In relative mode, this is a float between 0 and 1 (e.g. 0.01 for 1%). "
    "In absolute mode, packed variables use an hardcoded threshold of 1.5 * scale_factor.",
)
@click.option(
    "--threshold-nb-outliers",
    required=False,
    type=float,
    default=0.01,
    show_default=True,
    help="Maximum allowed relative number of outliers as a float between 0 and 1 (e.g. 0.01 for 1% outliers).",
)
@click.option(
    "--threshold-coverage",
    required=False,
    type=float,
    default=0.01,
    show_default=True,
    help="Maximum allowed valid coverage relative difference as a float between 0 and 1 (e.g. 0.01 for 1%)",
)
@click.option(
    "--structure/--no-structure",
    required=False,
    default=True,
    show_default=True,
    help="Compare products structure and metadata like Zarr metadata/attributes",
)
@click.option(
    "--data/--no-data",
    required=False,
    default=True,
    show_default=True,
    help="Compare variables data",
)
@click.option(
    "--flags/--no-flags",
    required=False,
    default=True,
    show_default=True,
    help="Compare flags/masks variables",
)
@click.option(
    "-s",
    "--secret",
    required=False,
    show_default=True,
    help="Secret alias if available extracted from env. variable S3_SECRETS_JSON_BASE64 or in /home/.eopf/secrets.json",
)
@click.option("-o", "--output", required=False, help="output file")
def compare(
    reference: str,
    actual: str,
    cmp_vars: str,
    cmp_grps: str,
    verbose: bool,
    info: bool,
    relative: bool,
    absolute: bool,
    threshold: float,
    threshold_nb_outliers: float,
    threshold_coverage: float,
    structure: bool,
    data: bool,
    flags: bool,
    secret: str,
    output: str,
    **kwargs: Any,
) -> None:
    """CLI tool to compare two products Zarr or SAFE."""
    if relative and absolute:
        raise click.UsageError("Options --relative and --absolute are mutually exclusive.")

    compare_products(
        reference,
        actual,
        cmp_vars=cmp_vars,
        cmp_grps=cmp_grps,
        verbose=verbose,
        info=info,
        relative=relative,
        absolute=absolute,
        threshold=threshold,
        threshold_nb_outliers=threshold_nb_outliers,
        threshold_coverage=threshold_coverage,
        structure=structure,
        data=data,
        flags=flags,
        secret=secret,
        output=output,
        **kwargs,
    )
