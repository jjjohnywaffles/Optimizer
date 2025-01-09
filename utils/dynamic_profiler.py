import cProfile
import pstats
import io

class DynamicProfiler:
    def __init__(self, script_path):
        self.script_path = script_path

    def profile_runtime(self):
        profiler = cProfile.Profile()
        profiler.enable()
        with open(self.script_path, "r") as file:
            exec(file.read(), {})
        profiler.disable()

        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs().sort_stats("cumtime")
        return stream.getvalue()

    def profile_memory(self):
        from memory_profiler import memory_usage

        def run_script():
            with open(self.script_path, "r") as file:
                exec(file.read(), {})

        mem_usage = memory_usage(run_script)
        return f"Peak memory usage: {max(mem_usage):.2f} MB"
