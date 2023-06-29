import cv2
import numpy as np
import torch
from mmdet.structures import DetDataSample
from mmengine.structures import InstanceData


class FilterSegMask:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Removes smaller masks that are contained in a bigger mask
    # @timer_func
    def remove_overlapping_masks(self, predicted_mask, method="mask", containments_threshold=0.5):
        # Convert masks to binary images
        masks = [mask.cpu().numpy() for mask in predicted_mask.pred_instances.masks]
        masks_binary = [(mask > 0).astype(np.uint8) for mask in masks]

        masks_tensor = predicted_mask.pred_instances.masks
        masks_tensor = [mask.to(self.device) for mask in masks_tensor]

        # Compute bounding boxes and areas
        boxes = [cv2.boundingRect(mask) for mask in masks_binary]

        # Compute pairwise containment
        containments = np.zeros((len(masks), len(masks)))

        for i in range(len(masks)):
            box_i = boxes[i]

            for j in range(i + 1, len(masks)):
                box_j = boxes[j]

                if method == "mask":
                    containment = self._calculate_containment_mask(masks_tensor[i], masks_tensor[j])
                    containments[i, j] = containment
                    containment = self._calculate_containment_mask(masks_tensor[j], masks_tensor[i])
                    containments[j, i] = containment
                elif method == "bbox":
                    containment = self._calculate_containment_bbox(box_i, box_j)
                    containments[i, j] = containment
                    containment = self._calculate_containment_bbox(box_j, box_i)
                    containments[j, i] = containment

        # Keep only the biggest masks for overlapping pairs
        keep_mask = np.ones(len(masks), dtype=np.bool_)
        for i in range(len(masks)):
            if not keep_mask[i]:
                continue
            if np.any(containments[i] > containments_threshold):
                contained_indices = np.where(containments[i] > containments_threshold)[0]
                for j in contained_indices:
                    if np.count_nonzero(masks_binary[i]) >= np.count_nonzero(masks_binary[j]):
                        keep_mask[j] = False
                    else:
                        keep_mask[i] = False

        # Create a new DetDataSample with only selected instances
        filtered_result = DetDataSample(metainfo=predicted_mask.metainfo)
        pred_instances = InstanceData(metainfo=predicted_mask.metainfo)

        masks = [mask for i, mask in enumerate(masks) if keep_mask[i]]
        list_of_tensor_masks = [torch.from_numpy(mask) for mask in masks]
        stacked_masks = torch.stack(list_of_tensor_masks)

        updated_filtered_result = self._stacked_masks_update_data_sample(
            filtered_result, stacked_masks, pred_instances, keep_mask, predicted_mask
        )

        return updated_filtered_result

    def _stacked_masks_update_data_sample(self, filtered_result, stacked_masks, pred_instances, keep_mask, result):
        pred_instances.masks = stacked_masks
        pred_instances.bboxes = self._update_datasample_cat(result.pred_instances.bboxes.tolist(), keep_mask)
        pred_instances.scores = self._update_datasample_cat(result.pred_instances.scores.tolist(), keep_mask)
        pred_instances.kernels = self._update_datasample_cat(result.pred_instances.kernels.tolist(), keep_mask)
        pred_instances.labels = self._update_datasample_cat(result.pred_instances.labels.tolist(), keep_mask)
        pred_instances.priors = self._update_datasample_cat(result.pred_instances.priors.tolist(), keep_mask)

        filtered_result.pred_instances = pred_instances

        return filtered_result

    def _calculate_containment_bbox(self, box_a, box_b):
        xA = max(box_a[0], box_b[0])  # max x0
        yA = max(box_a[1], box_b[1])  # max y0
        xB = min(box_a[0] + box_a[2], box_b[0] + box_b[2])  # min x1
        yB = min(box_a[1] + box_a[3], box_b[1] + box_b[3])  # min y1

        box_a_area = box_a[2] * box_a[3]
        box_b_area = box_b[2] * box_b[3]

        intersection_area = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        containment = intersection_area / box_a_area if box_a_area > 0 else 0
        return containment

    def _calculate_containment_mask(self, mask_a, mask_b):
        intersection = torch.logical_and(mask_a, mask_b).sum().float()
        containment = intersection / mask_b.sum().float() if mask_b.sum() > 0 else 0
        return containment

    def _update_datasample_cat(self, cat_list, keep_mask):
        cat_keep = [cat for i, cat in enumerate(cat_list) if keep_mask[i]]
        tensor_cat_keep = torch.tensor(cat_keep)
        return tensor_cat_keep

    # @timer_func
    def filter_on_pred_threshold(self, result_pred, pred_score_threshold=0.5):
        id_list = []
        for id, pred_score in enumerate(result_pred.pred_instances.scores):
            if pred_score > pred_score_threshold:
                id_list.append(id)

        # Create a new DetDataSample with only selected instances
        new_filtered_result = DetDataSample(metainfo=result_pred.metainfo)
        new_pred_instances = InstanceData(metainfo=result_pred.metainfo)

        new_pred_instances.masks = result_pred.pred_instances.masks[id_list]
        new_pred_instances.bboxes = result_pred.pred_instances.bboxes[id_list]
        new_pred_instances.scores = result_pred.pred_instances.scores[id_list]
        new_pred_instances.kernels = result_pred.pred_instances.kernels[id_list]
        new_pred_instances.labels = result_pred.pred_instances.labels[id_list]
        new_pred_instances.priors = result_pred.pred_instances.priors[id_list]

        new_filtered_result.pred_instances = new_pred_instances
        return new_filtered_result
        return new_filtered_result
