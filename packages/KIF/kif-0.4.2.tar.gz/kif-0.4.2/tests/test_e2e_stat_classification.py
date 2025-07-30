"""
e2e test for stat modelling process ran on the small test dataset.

Note: These tests do not cover all possible variations- e.g. feature filtering not performed here.

No testing performed on pymol/Chimera projections here either.
"""

from pathlib import Path

import pandas as pd

from key_interactions_finder import data_preperation, post_proccessing, stat_modelling


def test_stat_classification(
    tmp_path: Path,
    features_dataset: pd.DataFrame,
    targets_dataset_path: Path,
) -> None:
    """
    Test the stat modelling process for a classification model.
    """
    supervised_dataset = data_preperation.SupervisedFeatureData(
        input_df=features_dataset, target_file=targets_dataset_path, is_classification=True, header_present=True
    )

    stat_model = stat_modelling.ClassificationStatModel(
        dataset=supervised_dataset.df_filtered,
        class_names=["Closed", "Open"],
        interaction_types_included=["Hbond", "Saltbr", "Hydrophobic"],
        out_dir="",
    )

    # # Per feature scores
    # stat_model.calc_js_distances()
    # stat_model.calc_mutual_info_to_target()
    # # TODO assert statement here...

    # post_proc = post_proccessing.StatClassificationPostProcessor(stat_model=stat_model, out_dir=tmp_path)
    # # TODO assert content of tmp_path is correct.

    # js_per_res_scores = post_proc.get_per_res_scores(stat_method="jensen_shannon")

    # mi_per_res_scores = post_proc.get_per_res_scores(stat_method="mutual_information")

    # post_proc.estimate_feature_directions()
