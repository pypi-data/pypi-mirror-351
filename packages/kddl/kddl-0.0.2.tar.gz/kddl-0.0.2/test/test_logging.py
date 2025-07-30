import pytest
import kddl._logging as lgg
import time
import logging
import polars as pl
import polars.testing


def test_Timer():
    """Tests a Timer to insure that:

    1. stop() can be called without start()
    2. calling any of elapsed(), total_elapsed() or rolling_duration()
       before start() raises an exception.
    3. rolling duration is incremented correctly:
       3.1. after create_and_start() it is 0
       3.2. after one call it is the elapsed time
       3.3. after two calls it is (1-w)(first_call) + w(second_call)

    """
    # 1. stop() can be called without start()
    t = lgg.Timer()
    t.stop()

    # 2. before start() exceptions.
    # 2.1 elapsed()
    t = lgg.Timer()
    with pytest.raises(ValueError):
        t.elapsed()
    # 2.2 total_elapsed()
    t = lgg.Timer()
    with pytest.raises(ValueError):
        t.total_elapsed()
    # 2.3 rolling_duration()
    t = lgg.Timer()
    with pytest.raises(ValueError):
        t.rolling_duration()

    # 3. rolling duration
    # 3.1 after create_and_start() it is 0
    t = lgg.Timer.create_and_start()
    assert t.rolling_duration() == pytest.approx(0, abs=1e-6)

    # 3.2 after one call it is the elapsed time
    t = lgg.Timer.create_and_start()
    time.sleep(0.5)
    t.restart()
    assert t.rolling_duration() == pytest.approx(0.5, abs=1e-2)

    # 3.3 after two calls it is (1-w)(first_call) + w(second_call)
    time.sleep(0.01)
    t.restart()
    assert t.rolling_duration() == pytest.approx(
        0.01 * t.w + 0.5 * (1 - t.w), abs=1e-3
    )


def test_get_outdir(tmp_path_factory, caplog):
    """
    Tests that:
       1. Missing directories are skipped when picking next version number.
       2. If base directory doesn't exist, it is created.
       3. A warning is issued when creating a version value >= 1000.
            3.1 When there are actually all versions 0->999.
            3.2 Even when there are hardly any folders, say just one: 999.
    """
    # 1. Missing directories are skipped when picking next version number.
    # Setup
    # Create a sub-directory structure like:
    #   ./exp/1/7/cnn/0
    #   ./exp/1/7/cnn/1
    #   ./exp/1/7/cnn/3
    tmp_path = tmp_path_factory.mktemp("exp")
    tmp_path.joinpath("1/7/cnn/0").mkdir(parents=True)
    tmp_path.joinpath("1/7/cnn/1").mkdir(parents=True)
    tmp_path.joinpath("1/7/cnn/3").mkdir(parents=True)
    # Test
    outdir = lgg.get_outdir(tmp_path, ["1", "7", "cnn"])
    assert outdir == tmp_path.joinpath("1/7/cnn/4")
    assert outdir.exists()

    # 2. If base directory doesn't exist, it is created.
    # Setup
    tmp_path = tmp_path_factory.mktemp("out")
    # Test
    base_dir = tmp_path / "out"
    outdir = lgg.get_outdir(base_dir, ["1", "2", "3"])
    assert base_dir.exists()
    assert base_dir.joinpath("1/2/3/0").exists()

    # 3. A warning is issued when creating a version value > 1000.
    # 3.1 When there are actually all versions 0->999.
    with caplog.at_level(logging.WARNING):
        # Setup
        tmp_path = tmp_path_factory.mktemp("exp3")
        for _ in range(1000):
            lgg.get_outdir(tmp_path, ["1", "7", "cnn"])
        assert not caplog.records
        lgg.get_outdir(tmp_path, ["1", "7", "cnn"])
        # Test
        assert caplog.records, "Reached outdir version 1000."
    # 4.2 When there is a gap until 999.
    with caplog.at_level(logging.WARNING):
        # Setup
        caplog.clear()
        assert not caplog.records, "If this fails, I don't understand caplog."
        tmp_path = tmp_path_factory.mktemp("exp4")
        tmp_path.joinpath("1/7/cnn/999").mkdir(parents=True)
        assert not caplog.records
        # Test
        lgg.get_outdir(tmp_path, ["1", "7", "cnn"])
        assert caplog.records, "Reached outdir version 1000."


def test_MetricTracker(tmp_path):
    """Tests that:
    1. Recording doesn't raise an error and a dataframe can be created.
        1.1 The MetricTracker records by epoch.
        1.1 The MetricTracker records by epoch and step.
    """
    # Setup
    mt1 = lgg.MetricTracker(tmp_path)
    mt2 = lgg.MetricTracker(tmp_path)
    # fmt: off
    metrics = [
        (0, 1, lgg.Metric("loss", 7, increasing=False, checkpointed=True), True),
        (0, 10, lgg.Metric("loss", 8, increasing=False, checkpointed=True), False),
        (0, 100, lgg.Metric("loss", 6, increasing=False, checkpointed=True), True),
        (1, 1, lgg.Metric("loss", 5.2, increasing=False, checkpointed=True), True),
        (1, 10, lgg.Metric("loss", 6.2, increasing=False, checkpointed=True), False),
    ]
    # fmt: on
    expected_df1 = pl.DataFrame(
        [[0, None, 7], [1, None, 5.2]],
        schema=pl.Schema(
            {"epoch": pl.UInt32, "step": pl.UInt64, "loss": pl.Float64}
        ),
        orient="row",
    )
    expected_df2 = pl.DataFrame(
        [[0, 1, 7], [0, 10, 8], [0, 100, 6], [1, 1, 5.2], [1, 10, 6.2]],
        schema=pl.Schema(
            {"epoch": pl.UInt32, "step": pl.UInt64, "loss": pl.Float64}
        ),
        orient="row",
    )

    # Test
    # 1.
    prev_epoch = -1
    for epoch, step, metric, is_better in metrics:
        if epoch != prev_epoch:
            new_best1 = mt1.on_epoch_end([metric], epoch)
            prev_epoch = epoch
            if is_better:
                assert len(new_best1)
        new_best2 = mt2.new_metrics([metric], epoch, step)
        if is_better:
            assert len(new_best2)

    df1 = mt1.history_as_dataframe()
    df2 = mt2.history_as_dataframe()
    pl.testing.assert_frame_equal(df1, expected_df1)
    pl.testing.assert_frame_equal(df2, expected_df2)
