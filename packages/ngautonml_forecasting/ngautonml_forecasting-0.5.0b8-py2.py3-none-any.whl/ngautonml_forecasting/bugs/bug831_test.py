'''Column unique_id incorrectly turns into an index in neuralforecast.'''
# https://github.com/Nixtla/neuralforecast/issues/831
# pylint: disable=duplicate-code

from neuralforecast import NeuralForecast  # type: ignore[import]
from neuralforecast.models import NBEATS  # type: ignore[import]
from neuralforecast.utils import AirPassengersDF  # type: ignore[import]


def test_neuralforecast_bug1() -> None:
    '''Tests neuralforecast bug #831'''
    df = AirPassengersDF
    train_df = df[df.ds <= '1959-12-31']
    horizon = 12
    nf = NeuralForecast(
        models=[NBEATS(input_size=2 * horizon, h=horizon, max_steps=50)],
        freq='M')
    nf.fit(df=train_df)
    got = nf.predict()
    # example code at https://github.com/Nixtla/neuralforecast runs reset_index() here
    # We expect unique_id to be among the columns normally. Why is it an index?
    assert set(got.columns) == {'unique_id', 'ds', 'NBEATS'}
