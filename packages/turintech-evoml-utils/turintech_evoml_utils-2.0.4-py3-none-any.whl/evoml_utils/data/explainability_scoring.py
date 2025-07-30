import pickle
import re
import sys
from typing import Tuple, Dict, Union, Callable, Optional, NamedTuple

import numpy as np

# MetaModel for type checking
# @pyright: can't recognise types because of nuitka compilation
from metaml.meta_models.names import ClassifierName, RegressorName, ForecasterName  # type: ignore
from metaml.meta_models import MetaModel  # type: ignore
from evoml_api_models import MlTask  # type: ignore


class JustifiedScore(NamedTuple):
    score: Union[np.float64, float]
    justification: str


def interpretability_score(model: MetaModel) -> JustifiedScore:
    """Interpretability score.

    A combination of a base score as determined by ChatGPT4 (an approximate
    measure of how easy it is to understand how a model is making predictions)
    and a series of complexity modifiers that are specific to the model type.

    Args:
        model (MetaModel): The model to score.

    Returns:
        Tuple[float, str]: Score and justification.
    """
    justification = "Interpretability score measures how easy it is to understand how a model is making predictions."

    n_samples = 1000  # this defines the assumed number of samples in the dataset

    scores: Dict[
        Union[ClassifierName, RegressorName, ForecasterName], Callable[[MetaModel], Union[float, np.float64]]
    ] = {
        ClassifierName.adagrad_classifier: lambda x: _base_loss_clf(x.params.loss)
        - _regularization_penalty(0.0, x.params.alpha),
        ClassifierName.base_reduction_stacking_classifier: lambda x: 0.3,
        ClassifierName.catboost_classifier: lambda x: 0.8
        - _max_depth_penalty(x.params.depth, 1.0, 1.0)
        - _n_estimators_penalty(x.params.iterations)
        - _regularization_penalty(0.0, x.params.l2_leaf_reg)
        - _class_weight_penalty(x.params.auto_class_weights),
        ClassifierName.cd_classifier: lambda x: _base_loss_clf(x.params.loss)
        - _regularization_penalty_general(x.params.alpha / x.params.C, x.params.penalty),
        ClassifierName.decision_tree_classifier: lambda x: 1.0
        - _max_depth_penalty(
            x.params.max_depth, float(x.params.min_samples_split * n_samples), float(x.params.min_samples_leaf)
        ),
        ClassifierName.extra_trees_classifier: (
            lambda x: 1.0
            - _max_depth_penalty(
                x.params.max_depth,
                float(x.params.min_samples_split * n_samples),
                float(x.params.min_samples_leaf * n_samples),
            )
            - _n_estimators_penalty(x.params.n_estimators)
            - _feature_sampling_penalty(x.params.max_features.value)
        ),
        ClassifierName.feature_reduction_stacking_classifier: lambda x: 0.3,
        ClassifierName.fista_classifier: lambda x: _base_loss_clf(x.params.loss)
        - _regularization_penalty_general(x.params.alpha / x.params.C, x.params.penalty),
        ClassifierName.gaussian_naivebayes_classifier: lambda x: 0.8 - 0.1 * x.params.var_smoothing,
        ClassifierName.gaussian_process_classifier: lambda x: 0.4
        - _gaussian_process_penalty(x.params.n_restarts_optimizer, x.params.max_iter_predict),
        ClassifierName.gradient_boosting_classifier: (
            lambda x: 0.8
            - _max_depth_penalty(
                x.params.max_depth,
                float(x.params.min_samples_split * n_samples),
                float(x.params.min_samples_leaf * n_samples),
            )
            - _n_estimators_penalty(x.params.n_estimators * 2)
        ),
        ClassifierName.hist_gradient_boosting_classifier: (
            lambda x: 0.8
            - _max_depth_penalty(x.params.max_depth, 1.0, 1.0)
            - _n_estimators_penalty(x.params.max_iter * 2)
            - _regularization_penalty(0.0, x.params.l2_regularization)
        ),
        # ClassifierName.intelex_logistic_regression_classifier: (
        #     lambda x: base_loss_clf("log")
        #     - regularization_penalty_general(1.0 / x.params.C, x.params.penalty, x.params.l1_ratio)
        #     - class_weight_penalty(x.params.class_weight)
        # ),
        # ClassifierName.intelex_random_forest_classifier: (
        #     lambda x: 1.0
        #     - max_depth_penalty(
        #         x.params.max_depth,
        #         float(x.params.min_samples_split * n_samples),
        #         float(x.params.min_samples_leaf * n_samples),
        #     )
        #     - n_estimators_penalty(x.params.n_estimators)
        # ),
        # ClassifierName.intelex_svm_classifier: lambda x: base_kernel(x.params.kernel)
        # - int(x.params.kernel == "poly") * 0.1 * (x.params.degree - 2)
        # - class_weight_penalty(x.params.class_weight)
        # - regularization_penalty(0.0, 1.0 / x.params.C),
        ClassifierName.lightgbm_classifier: (
            lambda x: 0.8
            - _max_depth_penalty(x.params.max_depth, float(x.params.min_child_samples * n_samples), 1.0)
            - _n_estimators_penalty(x.params.n_estimators * 2)
            - _regularization_penalty(x.params.reg_alpha, x.params.reg_lambda)
            - 0.1 * int(x.params.boosting_type == "dart")
        ),
        ClassifierName.linear_discriminant_analysis_classifier: lambda x: 0.8
        - 0.1 * (x.params.shrinkage if x.params.shrinkage is not None else 0.0)
        - {"svd": 0.0, "lsqr": 0.1, "eigen": 0.2}[x.params.solver],
        ClassifierName.linearsvc_classifier: lambda x: _base_kernel("linear")
        - _class_weight_penalty(x.params.class_weight)
        - _regularization_penalty(0.0, 1.0 / x.params.C),
        ClassifierName.logistic_regression_classifier: (
            lambda x: _base_loss_clf("log")
            - _regularization_penalty_general(1.0 / x.params.C, x.params.penalty, x.params.l1_ratio)
            - _class_weight_penalty(x.params.class_weight)
        ),
        ClassifierName.nearest_centroid_classifier: lambda x: 0.8
        - 0.1 * (x.params.shrink_threshold if x.params.shrink_threshold is not None else 0.0),
        ClassifierName.nlp_sequence_classifier: lambda x: _base_nlp(x.params.model) - 0.2 * x.params.epochs,
        ClassifierName.passive_aggressive_classifier: (
            lambda x: _base_loss_clf(x.params.loss)
            - _regularization_penalty(0.0, 1.0 / x.params.C)
            - _class_weight_penalty(x.params.class_weight)
        ),
        ClassifierName.perceptron_classifier: (
            lambda x: _base_loss_clf("perceptron")
            - _regularization_penalty_general(x.params.alpha * 100, x.params.penalty)
            - _class_weight_penalty(x.params.class_weight)
        ),
        ClassifierName.prior_dummy_classifier: lambda x: 1.0,
        ClassifierName.quadratic_discriminant_analysis_classifier: lambda x: 0.6 - 0.1 * x.params.reg_param,
        ClassifierName.random_forest_classifier: (
            lambda x: 1.0
            - _max_depth_penalty(
                x.params.max_depth,
                float(x.params.min_samples_split * n_samples),
                float(x.params.min_samples_leaf * n_samples),
            )
            - _n_estimators_penalty(x.params.n_estimators)
        ),
        ClassifierName.saga_classifier: lambda x: _base_loss_clf(x.params.loss)
        - _regularization_penalty(0.0, x.params.alpha),
        ClassifierName.sdca_classifier: lambda x: _base_loss_clf(x.params.loss)
        - _regularization_penalty(x.params.l1_ratio * x.params.alpha, (1 - x.params.l1_ratio) * x.params.alpha),
        ClassifierName.sgd_classifier: (
            lambda x: _base_loss_clf(x.params.loss)
            - _regularization_penalty(x.params.l1_ratio * x.params.alpha, (1 - x.params.l1_ratio) * x.params.alpha)
            - _class_weight_penalty(x.params.class_weight)
        ),
        ClassifierName.stacking_classifier: lambda x: 0.3,
        ClassifierName.stratified_dummy_classifier: lambda x: 1.0,
        ClassifierName.svm_classifier: lambda x: _base_kernel(x.params.kernel)
        - int(x.params.kernel == "poly") * 0.1 * (x.params.degree - 2)
        - _class_weight_penalty(x.params.class_weight)
        - _regularization_penalty(0.0, 1.0 / x.params.C),
        ClassifierName.svrg_classifier: lambda x: _base_loss_clf(x.params.loss)
        - _regularization_penalty(0.0, x.params.alpha),
        ClassifierName.uniform_dummy_classifier: lambda x: 1.0,
        ClassifierName.xgboost_classifier: (
            lambda x: 0.8
            - _max_depth_penalty(
                x.params.max_depth,
                float(1 / (1 - x.params.min_child_weight * 0.1)),
                float(1 / (1 - x.params.gamma * 0.1)),
            )
            - _n_estimators_penalty(x.params.n_estimators * 2)
            - _regularization_penalty(x.params.reg_alpha, x.params.reg_lambda)
        ),
        RegressorName.ard_regressor: lambda x: 0.7
        - _bayesian_penalty(x.params.alpha_1, x.params.alpha_2, x.params.lambda_1, x.params.lambda_2)
        - 0.01 * np.log(1 + x.params.threshold_lambda),
        RegressorName.bayesian_ridge_regressor: lambda x: 0.7
        - _bayesian_penalty(x.params.alpha_1, x.params.alpha_2, x.params.lambda_1, x.params.lambda_2),
        RegressorName.catboost_regressor: lambda x: 0.8
        - _max_depth_penalty(x.params.depth, 1.0, 1.0)
        - _n_estimators_penalty(x.params.iterations)
        - _regularization_penalty(0.0, x.params.l2_leaf_reg),
        RegressorName.cd_regressor: lambda x: _base_loss_reg("squared")
        - _regularization_penalty_general(x.params.alpha / x.params.C, x.params.penalty),
        RegressorName.decision_tree_regressor: lambda x: 0.8
        - _max_depth_penalty(
            x.params.max_depth, float(x.params.min_samples_split * n_samples), float(x.params.min_samples_leaf)
        ),
        RegressorName.elastic_net_regressor: lambda x: _base_loss_reg("squared")
        - _regularization_penalty(x.params.l1_ratio * x.params.alpha, (1 - x.params.l1_ratio) * x.params.alpha),
        RegressorName.feature_reduction_stacking_regressor: lambda x: 0.3,
        RegressorName.fista_regressor: lambda x: _base_loss_reg("squared_huber")
        - _regularization_penalty_general(x.params.alpha / x.params.C, x.params.penalty),
        RegressorName.gradient_boosting_regressor: (
            lambda x: 0.8
            - _max_depth_penalty(
                x.params.max_depth,
                float(x.params.min_samples_split * n_samples),
                float(x.params.min_samples_leaf * n_samples),
            )
            - _n_estimators_penalty(x.params.n_estimators * 2)
        ),
        RegressorName.hist_gradient_boosting_regressor: (
            lambda x: 0.8
            - _max_depth_penalty(x.params.max_depth, 1.0, 1.0)
            - _n_estimators_penalty(x.params.max_iter * 2)
            - _regularization_penalty(0.0, x.params.l2_regularization)
        ),
        RegressorName.huber_regressor: lambda x: 1.0
        - _regularization_penalty(0.0, x.params.alpha)
        - 0.1 / x.params.epsilon,
        # RegressorName.intelex_elastic_net_regressor: lambda x: base_loss_reg("squared")
        # - regularization_penalty(x.params.l1_ratio * x.params.alpha, (1 - x.params.l1_ratio) * x.params.alpha),
        # RegressorName.intelex_linear_regressor: lambda x: 1.0,
        # RegressorName.intelex_random_forest_regressor: (
        #     lambda x: 0.8
        #     - max_depth_penalty(
        #         x.params.max_depth,
        #         float(x.params.min_samples_split * n_samples),
        #         float(x.params.min_samples_leaf * n_samples),
        #     )
        #     - n_estimators_penalty(x.params.n_estimators)
        # ),
        # RegressorName.intelex_svr_regressor: lambda x: base_kernel(x.params.kernel)
        # - int(x.params.kernel == "poly") * 0.1 * (x.params.degree - 2)
        # - regularization_penalty(0.0, 1.0 / x.params.C),
        RegressorName.linear_regressor: lambda x: 1.0,
        RegressorName.linearsvr_regressor: lambda x: _base_kernel("linear") - _regularization_penalty(0.0, x.params.C),
        RegressorName.lightgbm_regressor: (
            lambda x: 0.8
            - _max_depth_penalty(x.params.max_depth, float(x.params.min_child_samples * n_samples), 1.0)
            - _n_estimators_penalty(x.params.n_estimators * 2)
            - _regularization_penalty(x.params.reg_alpha, x.params.reg_lambda)
            - 0.1 * int(x.params.boosting_type == "dart")
        ),
        RegressorName.mean_dummy_regressor: lambda x: 1.0,
        RegressorName.median_dummy_regressor: lambda x: 1.0,
        RegressorName.nlp_sequence_regressor: lambda x: _base_nlp(x.params.model) - 0.2 * x.params.epochs,
        RegressorName.passive_aggressive_regressor: (
            lambda x: _base_loss_reg(x.params.loss) - _regularization_penalty(0.0, 1.0 / x.params.C)
        ),
        RegressorName.random_forest_regressor: (
            lambda x: 0.8
            - _max_depth_penalty(
                x.params.max_depth,
                float(x.params.min_samples_split * n_samples),
                float(x.params.min_samples_leaf * n_samples),
            )
            - _n_estimators_penalty(x.params.n_estimators)
        ),
        RegressorName.sgd_regressor: (
            lambda x: _base_loss_reg(x.params.loss)
            - _regularization_penalty(x.params.l1_ratio * x.params.alpha, (1 - x.params.l1_ratio) * x.params.alpha)
        ),
        RegressorName.stacking_regressor: lambda x: 0.3,
        RegressorName.base_reduction_stacking_regressor: lambda x: 0.3,
        RegressorName.svr_regressor: lambda x: _base_kernel(x.params.kernel)
        - int(x.params.kernel == "poly") * 0.1 * (x.params.degree - 2)
        - _regularization_penalty(0.0, 1.0 / x.params.C),
        RegressorName.xgboost_regressor: (
            lambda x: 0.8
            - _max_depth_penalty(
                x.params.max_depth,
                float(1 / (1 - x.params.min_child_weight * 0.1)),
                float(1 / (1 - x.params.gamma * 0.1)),
            )
            - _n_estimators_penalty(x.params.n_estimators * 2)
            - _regularization_penalty(x.params.reg_alpha, x.params.reg_lambda)
        ),
        ForecasterName.arima_forecaster: lambda x: (
            1.0
            - 0.01 * x.params.p
            - 0.02 * x.params.P
            - 0.01 * x.params.q
            - 0.02 * x.params.Q
            - 0.02 * x.params.d**2
            - 0.04 * x.params.D**2
        ),
        ForecasterName.auto_arima_forecaster: lambda x: 0.9,
        ForecasterName.auto_ets_forecaster: lambda x: 0.95,
        ForecasterName.naive_drift_forecaster: lambda x: 1.0,
        ForecasterName.naive_last_forecaster: lambda x: 1.0,
        ForecasterName.naive_mean_forecaster: lambda x: 1.0,
        ForecasterName.nbeats_forecaster: lambda x: (
            max(
                0.0,
                0.5
                - 0.001 * x.params.expansion_coefficient_dim
                - 0.01 * np.log(x.params.layer_widths)
                - 0.02 * np.log(x.params.num_stacks)
                - 0.04 * np.log(x.params.num_layers)
                - 0.04 * np.log(x.params.num_blocks)
                - 0.01 * np.log(x.params.trend_polynomial_degree),
            )
        ),
    }

    try:
        score = scores[model.metadata.model_name](model)
    except KeyError:
        score = 1.0

    return JustifiedScore(score=score, justification=justification)


def expressiveness_score() -> JustifiedScore:
    justification = "Expressiveness: \n"
    justification += "The Expressiveness is not yet considered."
    return JustifiedScore(score=0.5, justification=justification)


def space_complexity_score(model: MetaModel, num_features: int) -> JustifiedScore:
    p = pickle.dumps(model)
    kilobytes = sys.getsizeof(p) * 1e-3
    kilobytes_per_feature = kilobytes / max(num_features, 1)
    score = np.round(np.exp(-kilobytes_per_feature / 10), decimals=1)
    wording = {
        0.0: (
            "extremely inefficient. The model is very difficult to explain. "
            "Graphical representation will be immensely convoluted."
        ),
        0.1: "very inefficient. The model is difficult to explain and may be convoluted.",
        0.2: "inefficient. The model may be difficult to explain and can appear convoluted.",
        0.3: "rather inefficient. The model uses big data structures for its world representation.",
        0.4: "acceptable. However, there are likely models that can represent the feature relations more efficiently.",
        0.5: "satisfactory. The data structure might be inefficient. Operations might be difficult to trace.",
        0.6: "adequate. The model can likely represent the features' relations well.",
        0.7: "good. With some effort the data structure is easily understood.",
        0.8: "very good. The model's data structure is easy to understand. Predictions can be retraced.",
        0.9: "excellent. The model stores the learned representation efficiently. Operations are easily traceable.",
        1.0: "perfect. The model is very efficient at representing the feature relations it has learned.",
    }
    justification = (
        "Space Complexity: \n"
        f"The {model.metadata.model_name} model has a size of {kilobytes_per_feature} kB "
        f"per feature in the dataset. This is {wording[score]}"
    )
    return JustifiedScore(score=score, justification=justification)


def consistency_score(model: MetaModel) -> JustifiedScore:
    """A measure of the consistency of the model, or its sensitivity to random effects.

    Args:
        model (MetaModel): The model to be evaluated.

    Returns:
        Tuple[float, str]: Score and justification.
    """
    justification = (
        "Consistency: \n. A measure of the consistency of the model, or its sensitivity to random effects."
        " This is computed by varying the random seed for a model if it exists. \n"
    )

    scores: Dict[Union[ClassifierName, RegressorName, ForecasterName], float] = {
        ClassifierName.adagrad_classifier: 0.9503,
        ClassifierName.base_reduction_stacking_classifier: 1.0000,
        ClassifierName.catboost_classifier: 0.9849,
        ClassifierName.cd_classifier: 0.9977,
        ClassifierName.decision_tree_classifier: 0.9821,
        ClassifierName.extra_trees_classifier: 0.9857,
        ClassifierName.feature_reduction_stacking_classifier: 1.0000,
        ClassifierName.fista_classifier: 1.0000,
        ClassifierName.gaussian_naivebayes_classifier: 1.0000,
        ClassifierName.gaussian_process_classifier: 1.0000,
        ClassifierName.gradient_boosting_classifier: 0.9804,
        ClassifierName.hist_gradient_boosting_classifier: 1.0000,
        # ClassifierName.intelex_logistic_regression_classifier: 1.0000,
        # ClassifierName.intelex_random_forest_classifier: 0.9838,
        # ClassifierName.intelex_svm_classifier: 1.0000,
        ClassifierName.linear_discriminant_analysis_classifier: 1.0000,
        ClassifierName.linearsvc_classifier: 1.0000,
        ClassifierName.lightgbm_classifier: 1.0000,
        ClassifierName.logistic_regression_classifier: 1.0000,
        ClassifierName.nearest_centroid_classifier: 1.0000,
        ClassifierName.nlp_sequence_classifier: 1.0000,
        ClassifierName.passive_aggressive_classifier: 0.8720,
        ClassifierName.perceptron_classifier: 0.8905,
        ClassifierName.prior_dummy_classifier: 1.0000,
        ClassifierName.quadratic_discriminant_analysis_classifier: 1.0000,
        ClassifierName.random_forest_classifier: 0.9838,
        ClassifierName.saga_classifier: 0.9936,
        ClassifierName.sdca_classifier: 0.9526,
        ClassifierName.sgd_classifier: 0.9144,
        ClassifierName.stacking_classifier: 1.0000,
        ClassifierName.stratified_dummy_classifier: 1.0000,
        ClassifierName.svm_classifier: 1.0000,
        ClassifierName.svrg_classifier: 1.0000,
        ClassifierName.uniform_dummy_classifier: 1.0000,
        ClassifierName.xgboost_classifier: 1.0000,
        RegressorName.ard_regressor: 1.0000,
        RegressorName.base_reduction_stacking_regressor: 1.0000,
        RegressorName.bayesian_ridge_regressor: 1.0000,
        RegressorName.catboost_regressor: 0.9937,
        RegressorName.cd_regressor: 1.0000,
        RegressorName.decision_tree_regressor: 0.9849,
        RegressorName.elastic_net_regressor: 1.0000,
        RegressorName.feature_reduction_stacking_regressor: 1.0000,
        RegressorName.fista_regressor: 1.0000,
        RegressorName.gradient_boosting_regressor: 1.0000,
        RegressorName.hist_gradient_boosting_regressor: 1.0000,
        RegressorName.huber_regressor: 1.0000,
        # RegressorName.intelex_elastic_net_regressor: 1.0000,
        # RegressorName.intelex_linear_regressor: 1.0000,
        # RegressorName.intelex_random_forest_regressor: 1.0000,
        # RegressorName.intelex_svr_regressor: 1.0000,
        RegressorName.linear_regressor: 1.0000,
        RegressorName.linearsvr_regressor: 1.0000,
        RegressorName.lightgbm_regressor: 1.0000,
        RegressorName.mean_dummy_regressor: 1.0000,
        RegressorName.median_dummy_regressor: 1.0000,
        RegressorName.nlp_sequence_regressor: 1.0000,
        RegressorName.passive_aggressive_regressor: 0.7936,
        RegressorName.random_forest_regressor: 1.0000,
        RegressorName.sgd_regressor: 0.9960,
        RegressorName.stacking_regressor: 1.0000,
        RegressorName.svr_regressor: 1.0000,
        RegressorName.xgboost_regressor: 1.0000,
        ForecasterName.arima_forecaster: 1.0000,
        ForecasterName.auto_ets_forecaster: 1.0000,
        ForecasterName.auto_arima_forecaster: 1.0000,
        ForecasterName.naive_drift_forecaster: 1.0000,
        ForecasterName.naive_last_forecaster: 1.0000,
        ForecasterName.naive_mean_forecaster: 1.0000,
        ForecasterName.nbeats_forecaster: 1.0000,
    }

    try:
        score = scores[model.metadata.model_name]
    except KeyError:
        score = 1.0

    return JustifiedScore(score=score, justification=justification)


def stability_score(model: MetaModel) -> JustifiedScore:
    """A measure of the stability of the model, or its sensitivity to perturbations in the input.

    Args:
        model (MetaModel): The model to be evaluated.

    Returns:
        Tuple[float, str]: Score and justification.
    """
    justification = (
        "Stability: \n. A measure of the stability of the model, or its sensitivity to perturbations in the input."
        " This is computed by varying the training data passed into a model. \n"
    )

    scores: Dict[Union[ClassifierName, RegressorName, ForecasterName], float] = {
        ClassifierName.adagrad_classifier: 0.9958,
        ClassifierName.base_reduction_stacking_classifier: 1.0000,
        ClassifierName.catboost_classifier: 0.9635,
        ClassifierName.cd_classifier: 0.9972,
        ClassifierName.decision_tree_classifier: 0.9242,
        ClassifierName.extra_trees_classifier: 0.9620,
        ClassifierName.feature_reduction_stacking_classifier: 1.0000,
        ClassifierName.fista_classifier: 0.9966,
        ClassifierName.gaussian_naivebayes_classifier: 0.9986,
        ClassifierName.gaussian_process_classifier: 0.9860,
        ClassifierName.gradient_boosting_classifier: 0.9387,
        ClassifierName.hist_gradient_boosting_classifier: 0.9368,
        # ClassifierName.intelex_logistic_regression_classifier: 0.9964,
        # ClassifierName.intelex_random_forest_classifier: 0.9617,
        # ClassifierName.intelex_svm_classifier: 0.9170,
        ClassifierName.linear_discriminant_analysis_classifier: 0.9943,
        ClassifierName.linearsvc_classifier: 0.9591,
        ClassifierName.lightgbm_classifier: 0.9496,
        ClassifierName.logistic_regression_classifier: 0.9964,
        ClassifierName.nearest_centroid_classifier: 1.0000,
        ClassifierName.nlp_sequence_classifier: 1.0000,
        ClassifierName.passive_aggressive_classifier: 0.9618,
        ClassifierName.perceptron_classifier: 0.7565,
        ClassifierName.prior_dummy_classifier: 1.0000,
        ClassifierName.quadratic_discriminant_analysis_classifier: 0.9439,
        ClassifierName.random_forest_classifier: 0.9617,
        ClassifierName.saga_classifier: 0.9979,
        ClassifierName.sdca_classifier: 0.9803,
        ClassifierName.sgd_classifier: 0.8089,
        ClassifierName.stacking_classifier: 1.0000,
        ClassifierName.stratified_dummy_classifier: 1.0000,
        ClassifierName.svm_classifier: 0.9170,
        ClassifierName.svrg_classifier: 1.0000,
        ClassifierName.uniform_dummy_classifier: 1.0000,
        ClassifierName.xgboost_classifier: 0.9405,
        RegressorName.ard_regressor: 0.8423,
        RegressorName.base_reduction_stacking_regressor: 1.0000,
        RegressorName.bayesian_ridge_regressor: 0.9997,
        RegressorName.catboost_regressor: 0.8995,
        RegressorName.cd_regressor: 0.9996,
        RegressorName.decision_tree_regressor: 0.9536,
        RegressorName.elastic_net_regressor: 1.0000,
        RegressorName.feature_reduction_stacking_regressor: 1.0000,
        RegressorName.fista_regressor: 0.9997,
        RegressorName.gradient_boosting_regressor: 0.9604,
        RegressorName.hist_gradient_boosting_regressor: 0.9844,
        RegressorName.huber_regressor: 0.9992,
        # RegressorName.intelex_elastic_net_regressor: 1.0000,
        # RegressorName.intelex_linear_regressor: 0.8225,
        # RegressorName.intelex_random_forest_regressor: 0.9814,
        # RegressorName.intelex_svr_regressor: 1.0000,
        RegressorName.linear_regressor: 0.8225,
        RegressorName.linearsvr_regressor: 0.9998,
        RegressorName.lightgbm_regressor: 0.9834,
        RegressorName.mean_dummy_regressor: 1.0000,
        RegressorName.median_dummy_regressor: 1.0000,
        RegressorName.nlp_sequence_regressor: 1.0000,
        RegressorName.passive_aggressive_regressor: 0.9918,
        RegressorName.random_forest_regressor: 0.9929,
        RegressorName.sgd_regressor: 1.0000,
        RegressorName.stacking_regressor: 1.0000,
        RegressorName.svr_regressor: 0.9814,
        RegressorName.xgboost_regressor: 0.9509,
        ForecasterName.arima_forecaster: 1.0000,
        ForecasterName.auto_ets_forecaster: 1.0000,
        ForecasterName.auto_arima_forecaster: 1.0000,
        ForecasterName.naive_drift_forecaster: 1.0000,
        ForecasterName.naive_last_forecaster: 1.0000,
        ForecasterName.naive_mean_forecaster: 1.0000,
        ForecasterName.nbeats_forecaster: 1.0000,
    }

    try:
        score = scores[model.metadata.model_name]
    except KeyError:
        score = 1.0

    return JustifiedScore(score=score, justification=justification)


class JustifiedExplainabilityScores(NamedTuple):
    interpretability: Union[np.float64, float]
    expressiveness: Union[np.float64, float]
    consistency: Union[np.float64, float]
    space_complexity: Union[np.float64, float]
    numerical_stability: Union[np.float64, float]
    justification: str


def explainability_score(
    model: MetaModel,
    num_features: int,
    mltask: MlTask,
) -> JustifiedExplainabilityScores:
    """Computes a score for the explainability of a model.

    This is done by computing the scores for the following criteria:
    - interpretability
    - expressiveness
    - consistency
    - space complexity
    - stability

    Args:
        model (MetaModel): The model to be evaluated.
        num_features (int): The number of features in the dataset.
        mltask (MlTask): The machine learning task.

    Returns:
        JustifiedExplainabilityScores: A named tuple containing the scores for each criterion and a justification.
    """
    interpretability, justification = interpretability_score(model=model)
    expressiveness, text = expressiveness_score()
    justification += f"\n{text}"
    consistency, text = consistency_score(model=model)
    justification += f"\n{text}"
    space_complexity, text = space_complexity_score(model=model, num_features=num_features)
    justification += f"\n{text}"
    numerical_stability, text = stability_score(model=model)
    justification += f"\n{text}"
    return JustifiedExplainabilityScores(
        interpretability=interpretability,
        expressiveness=expressiveness,
        consistency=consistency,
        space_complexity=space_complexity,
        numerical_stability=numerical_stability,
        justification=justification,
    )


def _base_loss_clf(loss: str) -> float:
    return {
        "absolute": 0.9,
        "log": 0.8,
        "hinge": 0.7,
        "smooth_hinge": 0.7,
        "squared_hinge": 0.7,
        "huber": 0.65,
        "modified_huber": 0.6,
        "perceptron": 0.7,
        "squared": 0.6,
        "squared_error": 0.6,
        "epsilon_insensitive": 0.65,
        "squared_epsilon_insensitive": 0.6,
    }[loss]


def _base_loss_reg(loss: str) -> float:
    return {
        "squared": 1.0,
        "squared_error": 1.0,
        "huber": 0.85,
        "squared_huber": 0.85,
        "squared_hinge": 0.9,
        "epsilon_insensitive": 0.85,
        "squared_epsilon_insensitive": 0.8,
    }[loss]


def _base_kernel(kernel: str) -> float:
    return {
        "linear": 0.8,
        "poly": 0.6,
        "rbf": 0.5,
        "sigmoid": 0.6,
    }[kernel]


def _base_nlp(nlp_model: str) -> float:
    return {
        "roberta-base": 0.35,
        "bert-base-uncased": 0.35,
        "bert-base-cased": 0.3,
        "distilbert-base-uncased": 0.45,
        "distilbert-base-cased": 0.4,
        "albert-base-v2": 0.4,
        "facebook/bart-base": 0.35,
        "gpt2": 0.3,
        "google/electra-base-discriminator": 0.35,
        "deepmind/language-perceiver": 0.3,
    }[nlp_model]


def _max_depth_penalty(max_depth: int, min_samples_split: float, min_samples_leaf: float) -> np.float64:
    # TODO: consider getting these bounds from the model parameter space
    max_depth_lower_bound: int = 3
    max_depth_upper_bound: int = 16
    max_depth = min(max_depth, max_depth_upper_bound)
    min_samples_split = max(1.0, min_samples_split)
    min_samples_leaf = max(1.0, min_samples_leaf)
    penalty: np.float64 = (
        0.2
        * (
            (np.log(1 + max_depth) - np.log(1 + max_depth_lower_bound))
            / (np.log(1 + max_depth_upper_bound) - np.log(1 + max_depth_lower_bound))
        )
        * (1 / (1 + np.log(min_samples_leaf)) / (1 + np.log(min_samples_split)))
    )
    return penalty


def _n_estimators_penalty(n_estimators: int) -> np.float64:
    n_estimators_lower_bound: int = 1
    n_estimators_upper_bound: int = 100
    n_estimators = min(n_estimators, n_estimators_upper_bound)
    penalty: np.float64 = 0.2 * (
        (np.log(1 + n_estimators) - np.log(1 + n_estimators_lower_bound))
        / (np.log(1 + n_estimators_upper_bound) - np.log(1 + n_estimators_lower_bound))
    )
    return penalty


def _regularization_penalty(
    regularization_lasso: float,
    regularization_ridge: float,
    regularization_group_lasso: float = 0.0,
    regularization_fused_lasso: float = 0.0,
    regularization_simplex: float = 0.0,
) -> Union[np.float64, float]:
    lasso: Union[np.float64, float] = min(10.0, np.log(1 + regularization_lasso))
    ridge: Union[np.float64, float] = min(10.0, np.log(1 + regularization_ridge))
    group_lasso: Union[np.float64, float] = min(10.0, np.log(1 + regularization_group_lasso))
    fused_lasso: Union[np.float64, float] = min(10.0, np.log(1 + regularization_fused_lasso))
    simplex: Union[np.float64, float] = min(10.0, np.log(1 + regularization_simplex))
    penalty: Union[np.float64, float] = (
        0.005 * lasso + 0.01 * ridge + 0.0085 * group_lasso + 0.012 * fused_lasso + 0.011 * simplex
    )
    return penalty


def _regularization_penalty_general(
    regularization: float, regularization_type: str, ratio: Optional[float] = None
) -> Union[np.float64, float]:
    if ratio is not None and regularization_type == "elasticnet":
        return _regularization_penalty(ratio * regularization, (1 - ratio) * regularization)
    if regularization_type == "l1":
        return _regularization_penalty(regularization, 0.0)
    if regularization_type == "l2":
        return _regularization_penalty(0.0, regularization)
    if regularization_type == "l1/l2":
        return _regularization_penalty(0.0, 0.0, regularization_group_lasso=regularization)
    if regularization_type == "tv1d":
        return _regularization_penalty(0.0, 0.0, regularization_fused_lasso=regularization)
    if regularization_type == "simplex":
        return _regularization_penalty(0.0, 0.0, regularization_simplex=regularization)
    return 0.0


def _bayesian_penalty(alpha_1: float, alpha_2: float, lambda_1: float, lambda_2: float) -> np.float64:
    penalty: np.float64 = 0.005 * (
        np.log(1 + 1e6 * alpha_1) + np.log(1 + 1e6 * alpha_2) + np.log(1 + 1e6 * lambda_1) + np.log(1 + 1e6 * lambda_2)
    )
    return penalty


def _class_weight_penalty(class_weight: Optional[str]) -> float:
    if class_weight is None:
        return 0.0
    return 0.1 if class_weight.lower() in ["balanced", "balanced_subsample", "sqrtbalanced"] else 0.0


def _feature_sampling_penalty(max_features: Union[float, str]) -> float:
    multiplier = 0.05
    if max_features == "sqrt":
        return multiplier * 0.2
    if max_features == "log2":
        return multiplier * 0.1
    return multiplier * float(max_features)


def _gaussian_process_penalty(n_restarts_optimizer: int, max_iter_predict: int) -> np.float64:
    n_restarts_optimizer_upper_bound: int = 10
    max_iter_predict_upper_bound: int = 200
    n_restarts_optimizer = min(n_restarts_optimizer, n_restarts_optimizer_upper_bound)
    max_iter_predict = min(max_iter_predict, max_iter_predict_upper_bound)
    penalty: np.float64 = 0.1 * np.log(1 + n_restarts_optimizer) / np.log(
        1 + n_restarts_optimizer_upper_bound
    ) + 0.1 * np.log(1 + max_iter_predict) / np.log(1 + max_iter_predict_upper_bound)
    return penalty
