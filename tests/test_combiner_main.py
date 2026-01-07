from app.combiner import main


class DummyFuture:
    def __init__(self, result):
        self._result = result

    def result(self):
        return self._result


class DummyExecutor:
    def __init__(self, *args, **kwargs):
        self.futures = []

    def submit(self, fn, arg):
        # IMPORTANT: actually call the function
        result = fn(arg)
        future = DummyFuture(result)
        self.futures.append(future)
        return future

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_main_creates_output_dir_and_processes(tmp_path, mocker):
    (tmp_path / "album1").mkdir()
    (tmp_path / "album2").mkdir()

    # Patch concurrency + progress bar
    mocker.patch("app.combiner.ProcessPoolExecutor", return_value=DummyExecutor())
    mocker.patch("app.combiner.as_completed", lambda x: x)
    mocker.patch("app.combiner.tqdm", lambda x, **k: x)

    process_mock = mocker.patch("app.combiner.process_album", return_value="Success")

    main(str(tmp_path))

    # Output directory created
    assert (tmp_path / "merged_tracks").exists()
    # called twice
    assert process_mock.call_count == 2
