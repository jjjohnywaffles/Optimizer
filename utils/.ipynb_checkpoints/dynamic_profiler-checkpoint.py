import cProfile
import pstats
import io

class DynamicProfiler:
    """
    A class to perform dynamic profiling of Python scripts, focusing on:
      - Execution runtime profiling using `cProfile`.
      - Peak memory usage profiling using `memory_profiler`.
    """

    def __init__(self, script_path):
        """
        Initialize the profiler with the path to the Python script to be analyzed.

        Args:
            script_path (str): The file path of the script to profile.
        """
        self.script_path = script_path

    def profile_runtime(self):
        """
        Profile the runtime performance of the script using `cProfile`.

        The profiling captures:
          - The cumulative execution time of functions.
          - A breakdown of where time is spent during execution.

        Returns:
            str: A formatted string containing the profiling results, sorted by cumulative time.
        """
        # Initialize the cProfile profiler
        profiler = cProfile.Profile()

        # Enable the profiler and execute the script
        profiler.enable()
        with open(self.script_path, "r") as file:
            exec(file.read(), {})  # Execute the script in a controlled environment
        profiler.disable()

        # Collect profiling statistics into a stream
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs().sort_stats("cumtime")  # Sort stats by cumulative time
        return stream.getvalue()  # Return the formatted profiling data as a string

    def profile_memory(self):
        """
        Profile the memory usage of the script using `memory_profiler`.

        This function tracks the peak memory consumption of the script during execution.

        Returns:
            str: A formatted string indicating the peak memory usage in megabytes (MB).
        """
        from memory_profiler import memory_usage

        # Define a wrapper function to execute the script for memory profiling
        def run_script():
            with open(self.script_path, "r") as file:
                exec(file.read(), {})  # Execute the script in a controlled environment

        # Measure memory usage during script execution
        mem_usage = memory_usage(run_script)

        # Return the peak memory usage as a formatted string
        return f"Peak memory usage: {max(mem_usage):.2f} MB"
