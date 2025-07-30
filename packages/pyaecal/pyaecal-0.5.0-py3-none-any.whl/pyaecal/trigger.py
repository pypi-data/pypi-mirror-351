from .function import Function
import polars as pl
import logging

class Trigger(Function):
    def __init__(self):
        super().__init__()
        self.signals = []
        self.trigger_name = ""
        self.up = True

    def set_trigger(self, name, up=True):
        self.trigger = name
        self.up = up

    def evaluate(self, data):
        """
        Evaluate the data to return two DataFrames:
        - One for points where trigger_pre changes according to pre_up (if set).
        - One for points where trigger_post changes according to post_up (if set).

        :param data: Polars DataFrame containing the trigger signals
        :return: Tuple of (pre_triggers_df, post_triggers_df) where each is a Polars DataFrame
        """
        if data is None:
            return None
        return self.triggers(data, self.trigger_name, self.up)

    def __change(self, name, data):
        """
        Compute the change (difference) in the signal to detect transitions.

        :param name: Name of the signal column
        :param data: Polars DataFrame
        :return: DataFrame with an additional column for the signal change
        """
        # Compute the difference to detect changes
        data = data.with_columns(
            #(pl.col(name).shift(-1) - pl.col(name)).alias(f"{name}_mod")
            pl.col(name).cast(pl.Int32).sub(pl.col(name).shift(1).cast(pl.Int32)).alias(f"{name}_mod"),
            #(pl.col(name).shift(1) -pl.col(name)).cast(pl.Int32).alias(f"{name}_mod")
        )
        # Remove rows with NaN in the _mod column
        data = data.filter(pl.col(f"{name}_mod").is_not_null())
        return data
    
    def triggers(self, data, trigger, up):
        result = pl.DataFrame()

        # Process trigger_pre if set
        if trigger:
            if trigger not in data.columns:
                logging.error(f"Trigger signal {trigger} not found in data")
            else:
                data = self.__change(trigger, data)
                if up:
                    condition = (
                        pl.col(f"{trigger}_mod") > 0
                    )
                else:
                    condition = (
                        pl.col(f"{trigger}_mod") < 0
                    )
                result = data.filter(condition)
                result = result.drop([f"{trigger}_mod"])
                if result.is_empty():
                    logging.debug(f"No points found for trigger_pre ({trigger})")

        if not trigger:
            logging.debug("No triggers set")
        
        return result
