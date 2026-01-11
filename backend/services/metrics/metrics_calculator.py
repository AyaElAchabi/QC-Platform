"""
Service pour calculer les métriques avancées à partir des métriques d'entraînement existantes.
Ces métriques sont dérivées sans besoin de réentraînement ou d'inférence supplémentaire.
"""
import numpy as np
from typing import Dict, List, Any, Optional


class MetricsCalculator:
    """Calcule les métriques métier et dérivées à partir des métriques de base."""

    @staticmethod
    def calculate_f1_score(precision: float, recall: float) -> float:
        """Calcule le F1-score à partir de la précision et du rappel."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    @staticmethod
    def calculate_fp_fn_from_metrics(
        precision: float,
        recall: float,
        total_predictions: int,
        total_ground_truth: int
    ) -> Dict[str, int]:
        """
        Calcule TP, FP, FN à partir de precision/recall et totaux.

        Formules:
        - TP = precision × total_predictions
        - FP = total_predictions - TP
        - FN = total_ground_truth - TP
        """
        tp = int(precision * total_predictions)
        fp = total_predictions - tp
        fn = total_ground_truth - tp

        return {
            "tp": max(0, tp),
            "fp": max(0, fp),
            "fn": max(0, fn),
        }

    @staticmethod
    def calculate_business_metrics_from_training(
        metrics_history: List[Dict[str, Any]],
        estimated_total_objects: int = 100
    ) -> Dict[str, Any]:
        """
        Calcule les métriques métier à partir de l'historique d'entraînement.

        Args:
            metrics_history: Liste des métriques par epoch
            estimated_total_objects: Estimation du nombre d'objets dans le dataset de validation

        Returns:
            Dict contenant les métriques globales et par classe (simulées)
        """
        if not metrics_history:
            return {
                "global": {
                    "total_tp": 0,
                    "total_fp": 0,
                    "total_fn": 0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1": 0.0,
                },
                "per_class": {}
            }

        # Prendre les métriques du dernier epoch
        last_metrics = metrics_history[-1]
        precision = last_metrics.get("precision", 0.0)
        recall = last_metrics.get("recall", 0.0)

        # Estimer le nombre de prédictions et ground truth
        # Note: Ces valeurs sont estimées. Pour des valeurs exactes, il faudrait
        # exécuter l'inférence sur le dataset de validation
        estimated_predictions = int(estimated_total_objects * (precision + recall) / 2)

        # Calculer TP, FP, FN
        counts = MetricsCalculator.calculate_fp_fn_from_metrics(
            precision=precision,
            recall=recall,
            total_predictions=estimated_predictions,
            total_ground_truth=estimated_total_objects
        )

        # Calculer F1
        f1 = MetricsCalculator.calculate_f1_score(precision, recall)

        return {
            "global": {
                "total_tp": counts["tp"],
                "total_fp": counts["fp"],
                "total_fn": counts["fn"],
                "precision": precision,
                "recall": recall,
                "f1": f1,
            },
            "per_class": {
                # Note: YOLOv8 ne fournit pas les métriques par classe dans les métriques de base
                # Ces données nécessiteraient une inférence complète sur le dataset de validation
                # Pour l'instant, on retourne un dict vide
            }
        }

    @staticmethod
    def simulate_calibration_data(
        precision: float,
        recall: float,
        num_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Simule des données de calibration basées sur precision/recall.

        Note: Pour des données de calibration réelles, il faut exécuter l'inférence
        et collecter les scores de confiance. Cette fonction fournit une estimation.

        Args:
            precision: Précision du modèle
            recall: Rappel du modèle
            num_bins: Nombre de bins pour la calibration

        Returns:
            Dict contenant bins, accuracy_per_bin, confidence_per_bin, count_per_bin, ece
        """
        bins = np.linspace(0, 1, num_bins + 1)[:-1]  # [0.0, 0.1, 0.2, ..., 0.9]

        # Simuler une distribution de confiance
        # Les modèles bien calibrés ont généralement plus de prédictions à haute confiance
        confidence_distribution = np.random.beta(a=5, b=2, size=1000)  # Biais vers haute confiance

        # Calculer les statistiques par bin
        accuracy_per_bin = []
        confidence_per_bin = []
        count_per_bin = []

        ece_sum = 0.0
        total_samples = len(confidence_distribution)

        for i, bin_start in enumerate(bins):
            bin_end = bins[i + 1] if i < len(bins) - 1 else 1.0

            # Trouver les prédictions dans ce bin
            in_bin = (confidence_distribution >= bin_start) & (confidence_distribution < bin_end)
            count = np.sum(in_bin)

            count_per_bin.append(int(count))

            if count > 0:
                # Confiance moyenne dans ce bin
                avg_confidence = float(np.mean(confidence_distribution[in_bin]))
                confidence_per_bin.append(avg_confidence)

                # Simuler l'accuracy en fonction de la précision du modèle
                # Plus la confiance est élevée, plus l'accuracy devrait être proche de la précision
                # Ajouter un peu de bruit pour simuler la réalité
                noise = np.random.normal(0, 0.05)
                accuracy = min(1.0, max(0.0, precision * avg_confidence + noise))
                accuracy_per_bin.append(accuracy)

                # Contribution au ECE
                ece_sum += (count / total_samples) * abs(accuracy - avg_confidence)
            else:
                confidence_per_bin.append(None)
                accuracy_per_bin.append(None)

        # ECE (Expected Calibration Error)
        ece = ece_sum

        return {
            "bins": bins.tolist(),
            "accuracy_per_bin": accuracy_per_bin,
            "confidence_per_bin": confidence_per_bin,
            "count_per_bin": count_per_bin,
            "ece": ece,
        }

    @staticmethod
    def simulate_confusion_matrix(
        precision: float,
        recall: float,
        class_names: List[str],
        estimated_objects_per_class: int = 50
    ) -> Dict[str, Any]:
        """
        Simule une matrice de confusion basée sur precision/recall.

        Note: Pour une matrice réelle, il faut exécuter l'inférence.

        Args:
            precision: Précision globale
            recall: Rappel global
            class_names: Liste des noms de classes
            estimated_objects_per_class: Nombre estimé d'objets par classe

        Returns:
            Dict contenant tp_per_class, fp_per_class, fn_per_class, totaux
        """
        tp_per_class = {}
        fp_per_class = {}
        fn_per_class = {}

        total_tp = 0
        total_fp = 0
        total_fn = 0

        for class_name in class_names:
            # Varier légèrement les métriques par classe (simulé)
            class_precision = precision * np.random.uniform(0.85, 1.15)
            class_recall = recall * np.random.uniform(0.85, 1.15)

            # Limiter entre 0 et 1
            class_precision = min(1.0, max(0.0, class_precision))
            class_recall = min(1.0, max(0.0, class_recall))

            # Calculer TP, FP, FN pour cette classe
            estimated_predictions = int(estimated_objects_per_class * (class_precision + class_recall) / 2)
            counts = MetricsCalculator.calculate_fp_fn_from_metrics(
                precision=class_precision,
                recall=class_recall,
                total_predictions=estimated_predictions,
                total_ground_truth=estimated_objects_per_class
            )

            tp_per_class[class_name] = counts["tp"]
            fp_per_class[class_name] = counts["fp"]
            fn_per_class[class_name] = counts["fn"]

            total_tp += counts["tp"]
            total_fp += counts["fp"]
            total_fn += counts["fn"]

        return {
            "tp_per_class": tp_per_class,
            "fp_per_class": fp_per_class,
            "fn_per_class": fn_per_class,
            "total_tp": total_tp,
            "total_fp": total_fp,
            "total_fn": total_fn,
            "iou_threshold": 0.5,  # Seuil IoU utilisé
        }

    @staticmethod
    def simulate_iou_distribution(map50: float, map50_95: float) -> Dict[str, Any]:
        """
        Simule la distribution des IoU à partir des mAP.

        Args:
            map50: mAP @ IoU 0.5
            map50_95: mAP @ IoU 0.5:0.95

        Returns:
            Dict avec values, mean, std, min, max
        """
        # Simuler une distribution d'IoU
        # Plus les mAP sont élevés, plus les IoU sont généralement élevés
        mean_iou = (map50 + map50_95) / 2
        std_iou = 0.15  # Écart-type typique

        # Générer des valeurs d'IoU simulées
        num_samples = 200
        iou_values = np.random.normal(mean_iou, std_iou, num_samples)
        iou_values = np.clip(iou_values, 0.0, 1.0)  # Limiter entre 0 et 1

        return {
            "values": iou_values.tolist(),
            "mean": float(np.mean(iou_values)),
            "std": float(np.std(iou_values)),
            "min": float(np.min(iou_values)),
            "max": float(np.max(iou_values)),
        }

    @staticmethod
    def calculate_extended_metrics(
        metrics_history: List[Dict[str, Any]],
        class_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calcule toutes les métriques étendues à partir de l'historique d'entraînement.

        Args:
            metrics_history: Liste des métriques par epoch
            class_names: Liste optionnelle des noms de classes

        Returns:
            Dict contenant toutes les métriques avancées
        """
        if not metrics_history:
            return {}

        # Prendre les métriques du dernier epoch
        last_metrics = metrics_history[-1]
        precision = last_metrics.get("precision", 0.0)
        recall = last_metrics.get("recall", 0.0)
        map50 = last_metrics.get("map50", 0.0)
        map50_95 = last_metrics.get("map50_95", 0.0)

        # Métriques métier (FP, FN, F1)
        business_metrics = MetricsCalculator.calculate_business_metrics_from_training(
            metrics_history=metrics_history
        )

        # AUROC simulé (basé sur mAP)
        # Note: Pour AUROC réel, il faut les scores de confiance et labels vrais
        auroc = (map50 + map50_95) / 2  # Approximation simple

        # Calibration simulée
        calibration = MetricsCalculator.simulate_calibration_data(
            precision=precision,
            recall=recall
        )

        # Distribution IoU
        iou_distribution = MetricsCalculator.simulate_iou_distribution(
            map50=map50,
            map50_95=map50_95
        )

        # Matrice de confusion (si classes fournies)
        confusion_matrix = None
        if class_names:
            confusion_matrix = MetricsCalculator.simulate_confusion_matrix(
                precision=precision,
                recall=recall,
                class_names=class_names
            )

        return {
            "business_metrics": business_metrics,
            "auroc": auroc,
            "calibration": calibration,
            "iou_distribution": iou_distribution,
            "confusion_matrix": confusion_matrix,
        }
