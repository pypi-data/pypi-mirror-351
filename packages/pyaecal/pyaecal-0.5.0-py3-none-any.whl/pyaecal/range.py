import polars as pl
import logging
from .delta import Delta


class Range(Delta):
    """
    Extract data between pre- and post-triggers based on offset times.
    Returns a list of DataFrames, each containing data points for one range
    between a pre-trigger and its corresponding post-trigger, in order of detection.
    """

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__module__)
        self.log.setLevel(logging.INFO)

    def evaluate(self, data, include_unpaired=False):
        """
        Extract data between pre- and post-triggers, returning one DataFrame per range.

        :param data: Polars DataFrame containing the trigger signals and an 'offset' column
        :param include_unpaired: If True, include data from unpaired pre-triggers to the end of the data
        :return: List of Polars DataFrames, each containing data points for one trigger range
        """

        return self.ranges(data, self.pre_trigger, self.pre_up, self.post_trigger, self.post_up)

    def ranges(self, data, pre_trigger, pre_up, post_trigger, post_up):
        # Get paired pre- and post-triggers using Delta's __delta method
        delta_df = self.deltas(data, pre_trigger, pre_up, post_trigger, post_up)

        if delta_df.is_empty():
            self.log.debug("No trigger pairs found")
            return []

        # Initialize list to store DataFrames for each range
        ranges = []

        # Ensure data is sorted by offset
        data = data.sort("offset")

        # Iterate through each row in delta_df to extract ranges
        for row in delta_df.iter_rows(named=True):
            offset_pre = row["offset_pre"]
            offset_post = row["offset_post"]

            if offset_pre is None:
                continue
            if offset_post is None:
                continue

            # Paired trigger: extract data where offset is between offset_pre and offset_post
            range_df = data.filter(
                (pl.col("offset") >= offset_pre) & (pl.col("offset") <= offset_post)
            )
            if not range_df.is_empty():
                ranges.append(range_df)

        # Log results
        if not ranges:
            self.log.debug("No data ranges extracted")
        else:
            self.log.debug(f"Extracted {len(ranges)} data ranges")

        return ranges
