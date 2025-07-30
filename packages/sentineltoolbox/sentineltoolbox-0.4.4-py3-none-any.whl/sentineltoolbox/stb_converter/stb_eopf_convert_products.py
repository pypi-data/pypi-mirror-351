from pathlib import Path
from typing import Any

import click
from eopf import EOProduct, EOZarrStore, OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.store.mapping_factory import EOPFMappingFactory
from eopf.store.mapping_manager import EOPFMappingManager
from eopf.store.safe import EOSafeStore
from xarray import DataTree

from sentineltoolbox.attributes import guess_product_type
from sentineltoolbox.readers.open_datatree import open_datatree
from sentineltoolbox.resources.reference import PRODUCT
from sentineltoolbox.tools.stb_dump_product import convert_datatree_to_structure_str


@click.command()
@click.argument(
    "input",
    type=str,
    nargs=1,
)
@click.option(
    "-m",
    "--mapping",
    type=str,
)
@click.option(
    "-o",
    "--output-dir",
    type=str,
)
@click.option(
    "--dry-run",
    is_flag=True,
    show_default=True,
    default=False,
)
@click.option(
    "-n",
    "--name",
    type=str,
)
@click.option(
    "-d",
    "--dump",
    is_flag=True,
    show_default=True,
    default=False,
)
@click.option(
    "-c",
    "--cache",
    type=str,
)
def main(input: Any, mapping: Any, output_dir: Any, dry_run: Any, name: Any, dump: Any, cache: Any) -> None:
    convert_input(input, mapping, output_dir, dry_run, name, dump, cache)


def convert_input(
    input: str | Path,
    mapping: str | None = None,
    output_dir: str | Path | None = None,
    dry_run: bool = False,
    name: str | None = None,
    dump: bool = False,
    cache: Path | str | None = None,
) -> None:
    if output_dir is None:
        path_output_dir = Path(".").absolute()
    else:
        path_output_dir = Path(output_dir)
    if not path_output_dir.exists():
        path_output_dir.mkdir(parents=True, exist_ok=True)

    if cache:
        open_datatree_args: dict[str, Any] = dict(local_copy_dir=Path(cache), cache=True)
    else:
        open_datatree_args = {}

    print(f"{input=}, {mapping=}, {path_output_dir=}, {dry_run=}")
    mask_and_scale = True
    if mapping:
        # add tutorial mapping files to mapping manager
        mp = AnyPath(mapping)
        mf = EOPFMappingFactory(mapping_path=mp)
        mm = EOPFMappingManager(mf)
    else:
        mm = None
    product_path = AnyPath.cast(input)
    safe_store = EOSafeStore(
        product_path,
        mask_and_scale=True,
        mapping_manager=mm,
    )  # legacy store to access a file on the given URL
    eop = safe_store.load(name="NEWMAPPING")  # create and return the EOProduct
    target_store_kwargs: dict[Any, Any] = {}
    target_store = EOZarrStore(path_output_dir.as_posix(), mask_and_scale=mask_and_scale, **target_store_kwargs)
    target_store.open(mode=OpeningMode.CREATE_OVERWRITE)
    if not name:
        name = eop.get_default_file_name_no_extension()[:-4] + "XXXX"
    target_store[name] = eop
    target_store.close()
    # eop.to_datatree().to_zarr(name, mode="w")
    if dump:
        dump_name = name  # [:-4] + "LAST"
        path_converted_prod = (path_output_dir / name).as_posix() + ".zarr"
        converted_zarr = open_datatree(path_converted_prod)

        products: dict[str, DataTree] = {}
        products[dump_name + "_zarr"] = converted_zarr
        if isinstance(eop, EOProduct):
            products[dump_name + "_eop"] = eop.to_datatree()

        try:
            reference_path = PRODUCT.map()[guess_product_type(eop.attrs)]
        except KeyError:
            pass
        else:
            products[dump_name + "_ref"] = open_datatree(reference_path, **open_datatree_args)

        try:
            reference = PRODUCT[guess_product_type(eop.attrs)]
        except KeyError:
            pass
        else:
            products[dump_name + "_ref_metadata"] = reference

        for name, datatree in products.items():
            struct_name = name + ".structure.out"
            with open(path_output_dir / struct_name, "w") as fp:
                fp.write(convert_datatree_to_structure_str(datatree))

            struct_name = name + ".structure_and_type.out"
            with open(path_output_dir / struct_name, "w") as fp:
                fp.write(convert_datatree_to_structure_str(datatree, dtype=True))

            detail_name = f"{name}.structure-details.out"
            final_path = path_output_dir / "details" / detail_name
            final_path.parent.mkdir(parents=True, exist_ok=True)
            with open(final_path, "w") as fp:
                fp.write(convert_datatree_to_structure_str(datatree, details=True, dtype=True))
