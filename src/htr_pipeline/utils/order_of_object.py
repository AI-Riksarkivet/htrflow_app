import numpy as np
import pandas as pd


class OrderObject:
    def __init__(self):
        pass

    def order_lines(self, line_image, line_spacing_factor=0.5):
        bounding_boxes = line_image.pred_instances.bboxes.tolist()
        center_points = [(box[1] + box[3]) / 2 for box in bounding_boxes]
        horizontal_positions = [(box[0] + box[2]) / 2 for box in bounding_boxes]

        # Calculate the threshold distance
        threshold_distance = self._calculate_threshold_distance(bounding_boxes, line_spacing_factor)

        # Sort the indices based on vertical center points and horizontal positions
        indices = list(range(len(bounding_boxes)))
        indices.sort(
            key=lambda i: (
                center_points[i] // threshold_distance,
                horizontal_positions[i],
            )
        )

        # Order text lines
        return indices

    def _calculate_threshold_distance(self, bounding_boxes, line_spacing_factor=0.5):
        # Calculate the average height of the text lines
        total_height = sum(box[3] - box[1] for box in bounding_boxes)
        average_height = total_height / len(bounding_boxes)

        # Calculate the threshold distance, Set a factor for the threshold distance (adjust as needed)
        threshold_distance = average_height * line_spacing_factor

        # Return the threshold distance
        return threshold_distance

    def order_regions_marginalia(self, region_image, margin_ratio=0.2, histogram_bins=50, histogram_dip_ratio=0.5):
        bounding_boxes = region_image.pred_instances.bboxes.tolist()
        img_width = region_image.metainfo["ori_shape"][1]

        regions = [[i, x[0], x[1], x[0] + x[2], x[1] + x[3]] for i, x in enumerate(bounding_boxes)]

        # Create a pandas DataFrame from the regions
        df = pd.DataFrame(regions, columns=["region_id", "x_min", "y_min", "x_max", "y_max"])

        # Calculate the centroids of the bounding boxes
        df["centroid_x"] = (df["x_min"] + df["x_max"]) / 2
        df["centroid_y"] = (df["y_min"] + df["y_max"]) / 2

        # Calculate a histogram of the x-coordinates of the centroids
        histogram, bin_edges = np.histogram(df["centroid_x"], bins=histogram_bins)

        # Determine if there's a significant dip in the histogram, which would suggest a two-page layout
        is_two_pages = np.min(histogram) < np.max(histogram) * histogram_dip_ratio

        if is_two_pages:
            # Determine which page each region is on
            page_width = int(img_width / 2)
            df["page"] = (df["centroid_x"] > page_width).astype(int)

            # Determine if the region is in the margin
            margin_width = page_width * margin_ratio
            df["is_margin"] = ((df["page"] == 0) & (df["centroid_x"] < margin_width)) | (
                (df["page"] == 1) & (df["centroid_x"] > img_width - margin_width)
            )
        else:
            df["page"] = 0
            df["is_margin"] = (df["centroid_x"] < img_width * margin_ratio) | (
                df["centroid_x"] > img_width - page_width * margin_ratio
            )

        # Define a custom sorting function
        sort_regions = lambda row: (
            row["page"],
            row["is_margin"],
            row["centroid_y"],
            row["centroid_x"],
        )

        # Sort the DataFrame using the custom function
        df["sort_key"] = df.apply(sort_regions, axis=1)
        df = df.sort_values("sort_key")

        # Return the ordered regions
        return df["region_id"].tolist()


if __name__ == "__main__":
    pass
