import logging
import os
from queue import Queue
import threading
from .extract import Extract

class Function(Extract):
    """
    Base class to define function in module
    Based on Extract, it supports all the extract methods.
    It is necessary to set the files or directory to process before calling the process method.
    Evaluate method should be overwritten for data evaluation related to the function being developed.
    """

    def __init__(self, dataset=dict()):
        self.dataset = dataset
        super().__init__()
        self.module = self.__class__.__module__
        self.evals = Queue()
        
        # Thread for extracting data (populates self.data)
        self.extract_thread = threading.Thread(target=self._run_extract)
        self.extract_thread.daemon = True
        self.extract_thread.start()
        
        # Thread for evaluating data (populates self.evals)
        self.eval_thread = threading.Thread(target=self.run)
        self.eval_thread.daemon = True

    def _run_extract(self):
        """
        Run Extract's run method to process files and populate self.data.
        """
        super().run()  # Call Extract.run

    def process(self):
        """
        Retrieve the necessary information from the measurement files using the file queue.

        :return: dict containing files processed results
        """
        res = dict()

        # Ensure threads are running
        if not self.extract_thread.is_alive():
            self.extract_thread = threading.Thread(target=self._run_extract)
            self.extract_thread.daemon = True
            self.extract_thread.start()
        
        if not self.eval_thread.is_alive():
            self.eval_thread = threading.Thread(target=self.run)
            self.eval_thread.daemon = True
            self.eval_thread.start()

        # Wait for all files to be processed and evaluated
        self.files.join()
        self.data.join()

        # Collect results from the evals queue
        while not self.evals.empty():
            filename, eval_result = self.evals.get()
            self.evals.task_done()
            if eval_result is not None:
                res[filename] = eval_result
            else:
                logging.debug(f"No evaluation data for {filename}")

        return res

    def evaluate(self, data):
        """
        Using the data retrieved from the measurement file, generate calibration.
        This method should be overwritten by the derivative class.

        :return: evaluation data
        """
        return data

    def start(self):
        """
        Initialize the processing pipeline and return queues for monitoring.

        :return: tuple of (files queue, evals queue)
        """
        # Start the extract thread if not running
        if not self.extract_thread.is_alive():
            self.extract_thread = threading.Thread(target=self._run_extract)
            self.extract_thread.daemon = True
            self.extract_thread.start()

        # Start the eval thread if not running
        if not self.eval_thread.is_alive():
            self.eval_thread = threading.Thread(target=self.run)
            self.eval_thread.daemon = True
            self.eval_thread.start()

        return self.files, self.evals

    def run(self):
        """
        Process items from the data queue, evaluate them, and store results in evals queue.
        """
        while True:
            try:
                filename, data = self.data.get()
                if data.is_empty():
                    logging.debug(f"No data found for {filename}")
                    self.data.task_done()
                    continue

                result = self.evaluate(data)
                self.evals.put((filename, result))
                self.data.task_done()
            except Queue.Empty:
                if self.files.empty():
                    break  # Exit if no more files are being processed
                continue

    def __next__(self):
        """
        Iterate over evaluated results from the evals queue.
        """
        if self.evals.empty():
            raise StopIteration
        data = self.evals.get()
        self.evals.task_done()
        return data

    def lab(self):
        """
        Write the labels and parameters in a lab file
        """
        with open(f"{self.module}.lab", "w", encoding="utf-8") as f:
            f.write("[RAMCELL]\n")
            for index, row in self.channels.iterrows():
                f.write(f"{row['channel']}\n")
            f.write("\n")

            if self.dataset:
                f.write("[LABEL]\n")
                for key in self.dataset.keys():
                    f.write(f"{key}\n")