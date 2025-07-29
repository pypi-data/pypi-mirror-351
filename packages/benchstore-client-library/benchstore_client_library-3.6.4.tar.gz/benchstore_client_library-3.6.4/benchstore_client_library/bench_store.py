import json
import datetime


class BenchmarkResult:
    def __init__(self, test_name, execution_time, environment, metrics, tags=None):
        self.test_name = test_name
        self.execution_time = execution_time
        self.environment = environment
        self.metrics = metrics
        self.tags = tags or []
        self.timestamp = datetime.datetime.now()

    def to_json(self):
        return json.dumps({
            "test_name": self.test_name,
            "execution_time": self.execution_time,
            "environment": self.environment,
            "metrics": self.metrics,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat()
        })


class BenchmarkStore:
    def __init__(self):
        self.storage = []

    def add_result(self, benchmark_result):
        self.storage.append(benchmark_result)

    def search_results(self, test_name=None, environment=None, tag=None):
        results = self.storage
        if test_name:
            results = [r for r in results if r.test_name == test_name]
        if environment:
            results = [r for r in results if r.environment == environment]
        if tag:
            results = [r for r in results if tag in r.tags]
        return results

    def aggregate_metrics(self, metric_name):
        metrics = [r.metrics[metric_name]
                   for r in self.storage if metric_name in r.metrics]
        if metrics:
            return sum(metrics) / len(metrics)
        return None


# Helper Classes and Functions

def save_results_to_file(results, filename):
    with open(filename, 'w') as f:
        json.dump([result.to_json() for result in results], f)


def load_results_from_file(filename):
    with open(filename, 'r') as f:
        results_data = json.load(f)
        return [json.loads(result_json) for result_json in results_data]


class BenchmarkAnalyzer:
    @staticmethod
    def filter_recent_results(results, days=7):
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        return [result for result in results if datetime.datetime.fromisoformat(result['timestamp']) >= cutoff_date]

    @staticmethod
    def summarize_results(results):
        summary = {}
        for result in results:
            for metric, value in result['metrics'].items():
                summary.setdefault(metric, []).append(value)
        return {metric: sum(values)/len(values) for metric, values in summary.items()}
