# Copyright (c) 2017-2021 Jeorme Douay <jerome@far-out.biz>
# All rights reserved.

import polars as pl
import logging
from .trigger import Trigger


class Delta(Trigger):
    """
    Generate Table before and after shifting
    All the columns supplied in the data for process will be used.
    At the beginning of the shift, the columns will be added '_pre',
    at the end of the shift '_post'.
    Associates each pre-trigger with the next post-trigger based on offset time and calculates time difference.
    Handles cases where post-triggers may be missing for some pre-triggers.
    """

    def __init__(self):
        super().__init__()
        self.pre_trigger = ""
        self.pre_up = True
        self.post_trigger = ""
        self.post_up = True

    def set_trigger_pre(self, name, up=True):
        self.pre_trigger = name
        self.pre_up = up

    def set_trigger_post(self, name, up=True):
        self.post_trigger = name
        self.post_up = up

    def evaluate(self, data):
        """
        Evaluate the data to associate each pre-trigger with the next post-trigger and calculate time difference.
        Matches each pre-trigger with the first post-trigger that occurs after it based on offset time.
        Includes pre-triggers without matching post-triggers, with null values for post columns.

        :param data: Polars DataFrame containing the trigger signals
        :return: Polars DataFrame with merged pre/post triggers and time differences
        """
        return self.deltas(data, self.pre_trigger, self.pre_up, self.post_trigger, self.post_up)
    
    def deltas(self, data, pre_trigger, pre_up, post_trigger, post_up):
        pre_triggers= self.triggers(data, pre_trigger, pre_up)
        post_triggers= self.triggers(data, post_trigger, post_up)
        
        # Initialize result DataFrame
        result = pl.DataFrame()

        # Check if pre_triggers is empty
        if pre_triggers.is_empty():
            logging.debug("No pre-triggers found in data")
            return result

        # Ensure offsets are sorted
        pre_triggers = pre_triggers.sort("offset")
        post_triggers = post_triggers.sort("offset") if not post_triggers.is_empty() else post_triggers

        # Add suffixes to distinguish pre and post columns
        pre_triggers = pre_triggers.select([
            pl.col(col).alias(f"{col}_pre") if col != "offset" else pl.col("offset").alias("offset_pre")
            for col in pre_triggers.columns
        ])

        if not post_triggers.is_empty():
            post_triggers = post_triggers.select([
                pl.col(col).alias(f"{col}_post") if col != "offset" else pl.col("offset").alias("offset_post")
                for col in post_triggers.columns
            ])

        # If no post-triggers, return pre-triggers with null post columns
        if post_triggers.is_empty():
            logging.debug("No post-triggers found; returning pre-triggers with null post columns")
            post_columns = {f"{col}_post": pl.lit(None) for col in pre_triggers.columns if col != "offset_pre"}
            result = pre_triggers.with_columns(**post_columns, time_diff=pl.lit(None))
            return result

        # Use as-of join to match each pre-trigger with the first post-trigger where offset_post >= offset_pre
        result = pre_triggers.join_asof(
            post_triggers,
            left_on="offset_pre",
            right_on="offset_post",
            strategy="forward"  # Match with the first post-trigger where offset_post >= offset_pre
        )

        # Calculate time difference where post-trigger exists
        result = result.with_columns(
            pl.when(pl.col("offset_post").is_not_null())
            .then(pl.col("offset_post") - pl.col("offset_pre"))
            .otherwise(pl.lit(None))
            .alias("time_diff")
        )

        # Log results
        paired_count = result.filter(pl.col("offset_post").is_not_null()).height
        unpaired_count = result.filter(pl.col("offset_post").is_null()).height
        logging.debug(f"Found {paired_count} paired pre/post trigger events, {unpaired_count} unpaired pre-triggers")

        return result
