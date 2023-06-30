import cv2
import numpy as np
import torch
from mmdet.registry import VISUALIZERS


class SegMaskHelper:
    def __init__(self):
        pass

    # Pad the masks to image size (bug in RTMDet config?)
    # @timer_func
    def align_masks_with_image(self, result, img):
        masks = list()

        img = img[..., ::-1].copy()

        for j, mask in enumerate(result.pred_instances.masks):
            numpy_mask = mask.cpu().numpy()
            mask = cv2.resize(
                numpy_mask.astype(np.uint8),
                (img.shape[1], img.shape[0]),
                interpolation=cv2.INTER_NEAREST,
            )

            # Pad the mask to match the size of the image
            padded_mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
            padded_mask[: mask.shape[0], : mask.shape[1]] = mask
            mask = padded_mask
            mask = torch.from_numpy(mask)
            masks.append(mask)

        stacked_masks = torch.stack(masks)
        result.pred_instances.masks = stacked_masks

        return result

    # Crops the images using masks and put the cropped images on a white background
    # @timer_func
    def crop_masks(self, result, img):
        cropped_imgs = list()
        polygons = list()

        for j, mask in enumerate(result.pred_instances.masks):
            np_array = mask.cpu().numpy()
            contours, _ = cv2.findContours(
                np_array.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
            )  # fix so only one contour (the largest one) is extracted
            largest_contour = max(contours, key=cv2.contourArea)

            epsilon = 0.003 * cv2.arcLength(largest_contour, True)
            approx_poly = cv2.approxPolyDP(largest_contour, epsilon, True)
            approx_poly = np.squeeze(approx_poly)
            approx_poly = approx_poly.tolist()
            polygons.append(approx_poly)

            x, y, w, h = cv2.boundingRect(largest_contour)

            # Crop masked region and put on white background
            masked_region = img[y : y + h, x : x + w]
            white_background = np.ones_like(masked_region)
            white_background.fill(255)
            masked_region_on_white = cv2.bitwise_and(
                white_background, masked_region, mask=np_array.astype(np.uint8)[y : y + h, x : x + w]
            )

            cv2.bitwise_not(white_background, white_background, mask=np_array.astype(np.uint8)[y : y + h, x : x + w])
            res = white_background + masked_region_on_white

            cropped_imgs.append(res)

        return cropped_imgs, polygons

    def visualize_result(self, result, img, model_visualizer):
        visualizer = VISUALIZERS.build(model_visualizer)
        visualizer.add_datasample("result", img, data_sample=result, draw_gt=False)

        return visualizer.get_image()

    def _translate_line_coords(self, region_mask, line_polygons):
        region_mask = region_mask.cpu().numpy()
        region_masks_binary = (region_mask > 0).astype(np.uint8)

        box = cv2.boundingRect(region_masks_binary)
        translated_line_polygons = [[[a + box[0], b + box[1]] for [a, b] in poly] for poly in line_polygons]

        return translated_line_polygons


if __name__ == "__main__":
    pass
