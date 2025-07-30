import celldex
import scrnaseq
from biocframe import BiocFrame

import singler


def test_with_minimal_args():
    sce = scrnaseq.fetch_dataset("zeisel-brain-2015", "2023-12-14", realize_assays=True)

    blueprint_ref = celldex.fetch_reference(
        "blueprint_encode", "2024-02-26", realize_assays=True
    )
    immune_cell_ref = celldex.fetch_reference("dice", "2024-02-26", realize_assays=True)

    single, integrated = singler.annotate_integrated(
        test_data=sce,
        ref_data=(
            blueprint_ref,
            immune_cell_ref
        ),
        ref_labels=[
            blueprint_ref.get_column_data().column("label.main"),
            immune_cell_ref.get_column_data().column("label.main")
        ],
        num_threads=2
    )
    assert len(single) == 2
    assert isinstance(integrated, BiocFrame)


def test_with_all_supplied():
    sce = scrnaseq.fetch_dataset("zeisel-brain-2015", "2023-12-14", realize_assays=True)

    blueprint_ref = celldex.fetch_reference(
        "blueprint_encode", "2024-02-26", realize_assays=True
    )
    immune_cell_ref = celldex.fetch_reference("dice", "2024-02-26", realize_assays=True)

    single, integrated = singler.annotate_integrated(
        test_data=sce.assays["counts"],
        test_features=sce.get_row_names(),
        ref_data=(
            blueprint_ref,
            immune_cell_ref
        ),
        ref_labels=[
            blueprint_ref.get_column_data().column("label.main"),
            immune_cell_ref.get_column_data().column("label.main")
        ],
        ref_features=[
            blueprint_ref.get_row_names(),
            immune_cell_ref.get_row_names()
        ],
        num_threads=2
    )

    assert len(single) == 2
    assert isinstance(integrated, BiocFrame)


def test_with_colname():
    sce = scrnaseq.fetch_dataset("zeisel-brain-2015", "2023-12-14", realize_assays=True)

    blueprint_ref = celldex.fetch_reference(
        "blueprint_encode", "2024-02-26", realize_assays=True
    )
    immune_cell_ref = celldex.fetch_reference("dice", "2024-02-26", realize_assays=True)

    single, integrated = singler.annotate_integrated(
        test_data=sce,
        ref_data=(blueprint_ref, immune_cell_ref),
        ref_labels=["label.main"] * 2,
        num_threads=2
    )

    assert len(single) == 2
    assert isinstance(integrated, BiocFrame)
