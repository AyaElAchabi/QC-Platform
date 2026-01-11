"""
Metrics Service - Comprehensive metrics for object detection models
Includes: Confusion Matrix, FP/FN, Precision/Recall, AUROC, ECE, Calibration Curves
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict


class MetricsService:
    """Service pour calculer les métriques complètes de détection d'objets"""
    
    def __init__(self):
        self.default_iou_threshold = 0.5
        self.ece_bins = 10
    
    # ==================== IoU Calculation ====================
    
    def compute_iou(self, box1: List[float], box2: List[float]) -> float:
        """
        Calculer l'IoU entre deux bounding boxes.
        Format: [x1, y1, x2, y2]
        """
        x1_inter = max(box1[0], box2[0])
        y1_inter = max(box1[1], box2[1])
        x2_inter = min(box1[2], box2[2])
        y2_inter = min(box1[3], box2[3])
        
        inter_area = max(0, x2_inter - x1_inter) * max(0, y2_inter - y1_inter)
        
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union_area = box1_area + box2_area - inter_area
        
        if union_area == 0:
            return 0.0
        
        return inter_area / union_area
    
    def compute_iou_matrix(
        self,
        pred_boxes: List[List[float]],
        gt_boxes: List[List[float]]
    ) -> np.ndarray:
        """
        Calculer la matrice IoU entre prédictions et ground truth.
        """
        n_pred = len(pred_boxes)
        n_gt = len(gt_boxes)
        
        if n_pred == 0 or n_gt == 0:
            return np.zeros((n_pred, n_gt))
        
        iou_matrix = np.zeros((n_pred, n_gt))
        
        for i, pred in enumerate(pred_boxes):
            for j, gt in enumerate(gt_boxes):
                iou_matrix[i, j] = self.compute_iou(pred, gt)
        
        return iou_matrix
    
    # ==================== Confusion Matrix ====================
    
    def compute_confusion_matrix(
        self,
        predictions: List[Dict],
        ground_truths: List[Dict],
        class_names: List[str],
        iou_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Calculer la matrice de confusion pour la détection d'objets.
        
        Args:
            predictions: Liste de {"bbox": [...], "class_name": str, "confidence": float}
            ground_truths: Liste de {"bbox": [...], "class_name": str}
            class_names: Liste des noms de classes
            iou_threshold: Seuil IoU pour considérer une correspondance
            
        Returns:
            Dict avec TP, FP, FN par classe et totaux
        """
        n_classes = len(class_names)
        
        # Initialiser les compteurs par classe
        tp_per_class = {c: 0 for c in class_names}
        fp_per_class = {c: 0 for c in class_names}
        fn_per_class = {c: 0 for c in class_names}
        
        # Pour chaque classe, matcher prédictions et GT
        for class_name in class_names:
            # Filtrer par classe
            class_preds = [p for p in predictions if p.get("class_name") == class_name]
            class_gts = [g for g in ground_truths if g.get("class_name") == class_name]
            
            # Trier prédictions par confiance décroissante
            class_preds = sorted(class_preds, key=lambda x: x.get("confidence", 0), reverse=True)
            
            # Tracker les GT déjà matchées
            gt_matched = [False] * len(class_gts)
            
            for pred in class_preds:
                pred_box = pred.get("bbox", [])
                best_iou = 0
                best_gt_idx = -1
                
                for gt_idx, gt in enumerate(class_gts):
                    if gt_matched[gt_idx]:
                        continue
                    
                    gt_box = gt.get("bbox", [])
                    iou = self.compute_iou(pred_box, gt_box)
                    
                    if iou > best_iou:
                        best_iou = iou
                        best_gt_idx = gt_idx
                
                if best_iou >= iou_threshold and best_gt_idx >= 0:
                    tp_per_class[class_name] += 1
                    gt_matched[best_gt_idx] = True
                else:
                    fp_per_class[class_name] += 1
            
            # FN = GT non matchées
            fn_per_class[class_name] = sum(1 for m in gt_matched if not m)
        
        # Totaux
        total_tp = sum(tp_per_class.values())
        total_fp = sum(fp_per_class.values())
        total_fn = sum(fn_per_class.values())
        
        return {
            "tp_per_class": tp_per_class,
            "fp_per_class": fp_per_class,
            "fn_per_class": fn_per_class,
            "total_tp": total_tp,
            "total_fp": total_fp,
            "total_fn": total_fn,
            "iou_threshold": iou_threshold
        }
    
    # ==================== Business Metrics ====================
    
    def compute_business_metrics(
        self,
        confusion_data: Dict[str, Any],
        class_names: List[str]
    ) -> Dict[str, Any]:
        """
        Calculer les métriques métier à partir de la matrice de confusion.
        """
        tp_per_class = confusion_data["tp_per_class"]
        fp_per_class = confusion_data["fp_per_class"]
        fn_per_class = confusion_data["fn_per_class"]
        
        metrics_per_class = {}
        
        for class_name in class_names:
            tp = tp_per_class.get(class_name, 0)
            fp = fp_per_class.get(class_name, 0)
            fn = fn_per_class.get(class_name, 0)
            
            # Precision = TP / (TP + FP)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            
            # Recall = TP / (TP + FN)
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            
            # F1 = 2 * (P * R) / (P + R)
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            metrics_per_class[class_name] = {
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4)
            }
        
        # Métriques globales
        total_tp = confusion_data["total_tp"]
        total_fp = confusion_data["total_fp"]
        total_fn = confusion_data["total_fn"]
        
        global_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        global_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        global_f1 = 2 * (global_precision * global_recall) / (global_precision + global_recall) if (global_precision + global_recall) > 0 else 0.0
        
        return {
            "per_class": metrics_per_class,
            "global": {
                "total_tp": total_tp,
                "total_fp": total_fp,
                "total_fn": total_fn,
                "precision": round(global_precision, 4),
                "recall": round(global_recall, 4),
                "f1": round(global_f1, 4)
            }
        }
    
    # ==================== AUROC ====================
    
    def compute_auroc(
        self,
        confidences: List[float],
        labels: List[int]  # 1 = TP, 0 = FP
    ) -> float:
        """
        Calculer l'AUROC (Area Under ROC Curve).
        Mesure la capacité du modèle à distinguer les vrais positifs des faux positifs.
        """
        if len(confidences) == 0 or len(labels) == 0:
            return 0.0
        
        if len(confidences) != len(labels):
            raise ValueError("confidences et labels doivent avoir la même longueur")
        
        # Nombre de positifs et négatifs
        n_pos = sum(labels)
        n_neg = len(labels) - n_pos
        
        if n_pos == 0 or n_neg == 0:
            return 0.5  # Pas de discrimination possible
        
        # Trier par confiance décroissante
        sorted_indices = np.argsort(confidences)[::-1]
        sorted_labels = np.array(labels)[sorted_indices]
        
        # Calculer TPR et FPR pour chaque seuil
        tpr_list = []
        fpr_list = []
        
        tp = 0
        fp = 0
        
        for label in sorted_labels:
            if label == 1:
                tp += 1
            else:
                fp += 1
            
            tpr_list.append(tp / n_pos)
            fpr_list.append(fp / n_neg)
        
        # Ajouter le point (0, 0)
        tpr_list = [0.0] + tpr_list
        fpr_list = [0.0] + fpr_list
        
        # Calculer l'aire sous la courbe (méthode des trapèzes)
        auroc = 0.0
        for i in range(1, len(fpr_list)):
            auroc += (fpr_list[i] - fpr_list[i-1]) * (tpr_list[i] + tpr_list[i-1]) / 2
        
        return round(float(auroc), 4)
    
    # ==================== Calibration (ECE) ====================
    
    def compute_ece(
        self,
        confidences: List[float],
        accuracies: List[int],  # 1 = correct, 0 = incorrect
        n_bins: int = 10
    ) -> float:
        """
        Calculer l'Expected Calibration Error (ECE).
        
        ECE mesure l'écart entre la confiance prédite et la précision réelle.
        Un modèle bien calibré a un ECE proche de 0.
        """
        if len(confidences) == 0:
            return 0.0
        
        confidences = np.array(confidences)
        accuracies = np.array(accuracies)
        
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        total_samples = len(confidences)
        
        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]
            
            # Trouver les échantillons dans ce bin
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            n_in_bin = np.sum(in_bin)
            
            if n_in_bin > 0:
                avg_confidence = np.mean(confidences[in_bin])
                avg_accuracy = np.mean(accuracies[in_bin])
                
                # Contribution au ECE
                ece += (n_in_bin / total_samples) * abs(avg_accuracy - avg_confidence)
        
        return round(float(ece), 4)
    
    def compute_calibration_curve(
        self,
        confidences: List[float],
        accuracies: List[int],
        n_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Calculer les données pour la courbe de calibration (reliability diagram).
        """
        if len(confidences) == 0:
            return {
                "bins": [],
                "accuracy_per_bin": [],
                "confidence_per_bin": [],
                "count_per_bin": [],
                "ece": 0.0
            }
        
        confidences = np.array(confidences)
        accuracies = np.array(accuracies)
        
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        
        bins = []
        accuracy_per_bin = []
        confidence_per_bin = []
        count_per_bin = []
        
        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]
            bin_center = (bin_lower + bin_upper) / 2
            
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            n_in_bin = np.sum(in_bin)
            
            bins.append(round(bin_center, 2))
            count_per_bin.append(int(n_in_bin))
            
            if n_in_bin > 0:
                accuracy_per_bin.append(round(float(np.mean(accuracies[in_bin])), 4))
                confidence_per_bin.append(round(float(np.mean(confidences[in_bin])), 4))
            else:
                accuracy_per_bin.append(None)
                confidence_per_bin.append(None)
        
        ece = self.compute_ece(confidences.tolist(), accuracies.tolist(), n_bins)
        
        return {
            "bins": bins,
            "accuracy_per_bin": accuracy_per_bin,
            "confidence_per_bin": confidence_per_bin,
            "count_per_bin": count_per_bin,
            "ece": ece
        }
    
    # ==================== Complete Metrics Pipeline ====================
    
    def compute_all_metrics(
        self,
        predictions: List[Dict],
        ground_truths: List[Dict],
        class_names: List[str],
        iou_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Pipeline complet pour calculer toutes les métriques.
        
        Args:
            predictions: Liste de {"bbox": [...], "class_name": str, "confidence": float}
            ground_truths: Liste de {"bbox": [...], "class_name": str}
            class_names: Liste des noms de classes
            
        Returns:
            Dict avec toutes les métriques
        """
        # 1. Matrice de confusion
        confusion_data = self.compute_confusion_matrix(
            predictions, ground_truths, class_names, iou_threshold
        )
        
        # 2. Métriques métier
        business_metrics = self.compute_business_metrics(confusion_data, class_names)
        
        # 3. Préparer les données pour AUROC et calibration
        # Matcher chaque prédiction avec son résultat (TP=1, FP=0)
        confidences = []
        labels = []  # 1 = TP, 0 = FP
        
        for class_name in class_names:
            class_preds = [p for p in predictions if p.get("class_name") == class_name]
            class_gts = [g for g in ground_truths if g.get("class_name") == class_name]
            
            class_preds = sorted(class_preds, key=lambda x: x.get("confidence", 0), reverse=True)
            gt_matched = [False] * len(class_gts)
            
            for pred in class_preds:
                conf = pred.get("confidence", 0)
                pred_box = pred.get("bbox", [])
                
                best_iou = 0
                best_gt_idx = -1
                
                for gt_idx, gt in enumerate(class_gts):
                    if gt_matched[gt_idx]:
                        continue
                    gt_box = gt.get("bbox", [])
                    iou = self.compute_iou(pred_box, gt_box)
                    if iou > best_iou:
                        best_iou = iou
                        best_gt_idx = gt_idx
                
                confidences.append(conf)
                if best_iou >= iou_threshold and best_gt_idx >= 0:
                    labels.append(1)
                    gt_matched[best_gt_idx] = True
                else:
                    labels.append(0)
        
        # 4. AUROC
        auroc = self.compute_auroc(confidences, labels) if len(confidences) > 0 else 0.0
        
        # 5. Calibration
        calibration = self.compute_calibration_curve(confidences, labels)
        
        # 6. IoU distribution
        iou_values = []
        for pred in predictions:
            pred_box = pred.get("bbox", [])
            pred_class = pred.get("class_name", "")
            
            matching_gts = [g for g in ground_truths if g.get("class_name") == pred_class]
            if matching_gts:
                max_iou = max(self.compute_iou(pred_box, g.get("bbox", [])) for g in matching_gts)
                iou_values.append(round(max_iou, 4))
        
        return {
            "confusion_matrix": confusion_data,
            "business_metrics": business_metrics,
            "auroc": auroc,
            "calibration": calibration,
            "iou_distribution": {
                "values": iou_values,
                "mean": round(float(np.mean(iou_values)), 4) if iou_values else 0.0,
                "std": round(float(np.std(iou_values)), 4) if iou_values else 0.0,
                "min": round(float(np.min(iou_values)), 4) if iou_values else 0.0,
                "max": round(float(np.max(iou_values)), 4) if iou_values else 0.0
            },
            "summary": {
                "total_predictions": len(predictions),
                "total_ground_truths": len(ground_truths),
                "iou_threshold": iou_threshold,
                "n_classes": len(class_names)
            }
        }


# Instance singleton
metrics_service = MetricsService()
