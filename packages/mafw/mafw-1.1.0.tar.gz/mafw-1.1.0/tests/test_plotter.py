from pathlib import Path
from typing import Any, Collection
from unittest.mock import ANY

import matplotlib.pyplot as plt
import pytest
from peewee import FloatField, TextField
from playhouse.db_url import connect

from mafw.db.db_configurations import default_conf
from mafw.db.db_model import MAFwBaseModel, database_proxy
from mafw.db.std_tables import PlotterOutput
from mafw.decorators import processor_depends_on_optional, single_loop
from mafw.enumerators import ProcessorExitStatus
from mafw.mafw_errors import PlotterMixinNotInitialized
from mafw.processor_library.plotter import (
    CatPlot,
    DisPlot,
    FromDatasetDataRetriever,
    GenericPlotter,
    RelPlot,
    SQLDataRetriever,
)
from mafw.tools.pandas_tools import group_and_aggregate_data_frame

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import seaborn as sns
except ImportError:
    sns = None


pandas_available = pytest.mark.skipif(pd is None, reason='pandas must be available to run this test')
seaborn_available = pytest.mark.skipif(sns is None, reason='seaborn must be available to run this test')


@seaborn_available
def test_backend(caplog):
    pytest.importorskip('tkinter')
    dataframe = sns.load_dataset('penguins')
    plt.switch_backend('Agg')
    sns.relplot(dataframe, x='flipper_length_mm', y='bill_length_mm')
    try:
        plt.switch_backend('TkAgg')
        sns.relplot(dataframe, x='flipper_length_mm', y='bill_length_mm')
    except ImportError:
        pytest.xfail('Missing backend.')

    @single_loop
    class BackendPlotter(GenericPlotter):
        pass

    bp = BackendPlotter(matplotlib_backend='TkAgg')
    assert bp.matplotlib_backend == 'TkAgg'
    bp.start()

    bp.matplotlib_backend = 'Agg'
    bp.start()

    bp.matplotlib_backend = 'Unknown'
    caplog.clear()
    with pytest.raises(ModuleNotFoundError):
        bp.start()

    assert len(caplog.record_tuples) == 1
    assert caplog.record_tuples[0][1] == 50
    assert 'Unknown is not a valid plt backend' in caplog.record_tuples[0][2]


@pandas_available
def test_check_pandas():
    assert pd is not None


@pytest.fixture
def penguin():
    class Penguin(MAFwBaseModel):
        species = TextField(null=True)
        island = TextField(null=True)
        bill_length = FloatField(null=True)
        bill_depth = FloatField(null=True)
        flipper_length = FloatField(null=True)
        body_mass = FloatField(null=True)
        sex = TextField(null=True)

    return Penguin


@pandas_available
def test_super_call_patch_data_frame():
    from mafw.decorators import processor_depends_on_optional, single_loop
    from mafw.mafw_errors import MissingSuperCall
    from mafw.processor_library.plotter import GenericPlotter, SQLDataRetriever

    @processor_depends_on_optional(module_name='pandas')
    @single_loop
    class GoodPlotter(GenericPlotter):
        def patch_data_frame(self) -> None:
            super().patch_data_frame()
            len(self.data_frame)

    GoodPlotter()

    @processor_depends_on_optional(module_name='pandas')
    @single_loop
    class MixedGoodPlotter(SQLDataRetriever, GenericPlotter):
        def patch_data_frame(self) -> None:
            super().patch_data_frame()
            len(self.data_frame)

    MixedGoodPlotter()

    @processor_depends_on_optional(module_name='pandas')
    @single_loop
    class BadPlotter(GenericPlotter):
        def patch_data_frame(self) -> None:
            len(self.data_frame)

    with pytest.warns(MissingSuperCall, match='patch_data_frame'):
        BadPlotter()

    @processor_depends_on_optional(module_name='pandas')
    @single_loop
    class MixedBadPlotter(SQLDataRetriever, GenericPlotter):
        def patch_data_frame(self) -> None:
            len(self.data_frame)

    with pytest.warns(MissingSuperCall, match='patch_data_frame'):
        MixedBadPlotter()


@pandas_available
def test_plotter_without_database(caplog):
    from mafw.decorators import single_loop
    from mafw.processor_library.plotter import GenericPlotter

    caplog.set_level(30)
    caplog.clear()

    @single_loop
    class NoDBPlotter(GenericPlotter):
        pass

    NoDBPlotter().execute()
    # we expect two warnings, one from the check on output existence, and one from the update output
    assert len(caplog.record_tuples) == 2
    for r in caplog.record_tuples:
        if r[1] == 30:
            assert 'No database connection available' in r[2]
    caplog.clear()

    ndb = NoDBPlotter()
    ndb.filter_register.new_only = False
    ndb.execute()
    # we expect one warning only from the update output
    assert len(caplog.record_tuples) == 1
    for r in caplog.record_tuples:
        if r[1] == 30:
            assert 'No database connection available' in r[2]


@seaborn_available
@pandas_available
def test_mixing_generic_with_sql(datadir, tmp_path, penguin):
    from mafw.decorators import processor_depends_on_optional, single_loop
    from mafw.mafw_errors import PlotterMixinNotInitialized
    from mafw.processor import ActiveParameter
    from mafw.processor_library.plotter import GenericPlotter, SQLDataRetriever

    Penguin: type[MAFwBaseModel] = penguin

    table_name = Penguin._meta.table_name

    cols = ['island', 'species']

    db_file = datadir / Path(r'plotter.db')

    database_conf = default_conf['sqlite']
    database_conf['URL'] = 'sqlite:///' + str(db_file)

    test_df = sns.load_dataset('penguins')

    class PatchedSQLDataRetriever(SQLDataRetriever):
        def patch_data_frame(self) -> None:
            super().patch_data_frame()
            self.data_frame['CAP_ISLAND'] = self.data_frame['island'].str.upper()

    @processor_depends_on_optional(module_name='pandas')
    @single_loop
    class DataPlotter(PatchedSQLDataRetriever, GenericPlotter):
        param1 = ActiveParameter('param1', default='Test parameter')
        value = ActiveParameter('value', default=12.0)
        data_length = ActiveParameter('data_length', default=0)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.table_name = table_name
            self.required_columns = cols
            self.divider = 10

        def patch_data_frame(self) -> None:
            super().patch_data_frame()
            self.data_frame['CAP_SPECIES'] = self.data_frame['species'].str.upper()

        # the Plotter base has an overloaded process.
        # implement a fake plot to test if it works.
        def plot(self) -> None:
            self.value /= self.divider
            self.data_length = len(self.data_frame.index)

        def save(self) -> None:
            output_file = tmp_path / Path('test.png')
            with open(output_file, 'wt') as f:
                f.write('created by processor')
            self.output_filename_list.append(output_file)

    param1 = 'Another value'
    value = 120.0
    divider = 12

    sql_plotter = DataPlotter(param1=param1, value=value, database_conf=database_conf)

    # setting local processor attribute
    sql_plotter.divider = divider

    # asserting value of mixin attribute initialised in the processor init
    assert sql_plotter.table_name == table_name

    # asserting the value of mixin attribute initialised in the processor init.
    assert sql_plotter.required_columns == cols

    # asserting the value of processor active parameter
    assert sql_plotter.param1 == param1

    # asserting value of processor attribute
    assert sql_plotter.divider == divider

    # asserting initial value of processor attribute
    assert sql_plotter.value == value

    # asserting the initial value of data_length
    assert sql_plotter.data_length == 0

    sql_plotter.execute()
    # assert processor execution was successful
    assert sql_plotter.processor_exit_status == ProcessorExitStatus.Successful

    # assert processor execute was ok
    assert sql_plotter.value == value / divider

    # asserting the real value of data_length
    assert sql_plotter.data_length == len(test_df.index)

    # asserting that the patch data frame implemented into the mixed processor worked
    assert all(sql_plotter.data_frame['CAP_SPECIES'] == test_df['species'].str.upper())

    # asserting that the patch data frame implemented into the derived mixin worked
    assert all(sql_plotter.data_frame['CAP_ISLAND'] == test_df['island'].str.upper())

    # check that the output file was created
    assert (tmp_path / Path('test.png')).exists()

    # remove the file and get ready to repeat the execution
    (tmp_path / Path('test.png')).unlink(missing_ok=True)
    sql_plotter.execute()

    # check that the output file is created
    assert (tmp_path / Path('test.png')).exists()

    # now change the output file
    (tmp_path / Path('test.png')).unlink(missing_ok=True)
    with open(tmp_path / Path('test.png'), 'wt') as f:
        f.write('manually created')

    # run the processor again
    sql_plotter.execute()

    # assert that the output file is existing
    (tmp_path / Path('test.png')).exists()

    # open it and check that is the one created by the processor
    with open(tmp_path / Path('test.png')) as f:
        content = f.read()
    assert 'manually created' not in content
    assert 'created by processor' in content

    # run the processor once again
    # this time the processor is actually doing nothing
    sql_plotter.execute()
    # assert that the output file is existing
    (tmp_path / Path('test.png')).exists()

    @processor_depends_on_optional(module_name='pandas')
    @single_loop
    class NoInitPlotter(PatchedSQLDataRetriever, GenericPlotter):
        param1 = ActiveParameter('param1', default='Test parameter')
        value = ActiveParameter('value', default=12.0)
        data_length = ActiveParameter('data_length', default=0)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.divider = 10

        def patch_data_frame(self) -> None:
            super().patch_data_frame()
            self.data_frame['CAP_SPECIES'] = self.data_frame['species'].str.upper()

        # the Plotter base has an overloaded process.
        # implement a fake plot to test if it works.
        def plot(self) -> None:
            self.value /= self.divider
            self.data_length = len(self.data_frame.index)

    # it must raise an exception
    with pytest.raises(PlotterMixinNotInitialized):
        NoInitPlotter(database_conf=database_conf).execute()

    # it must raise an exception
    with pytest.raises(PlotterMixinNotInitialized):
        NoInitPlotter(database_conf=database_conf, table_name='penguin').execute()

    # again
    with pytest.raises(PlotterMixinNotInitialized):
        NoInitPlotter(required_cols='island', database_conf=database_conf).execute()

    # it should run w/o exception
    nip = NoInitPlotter(
        database_conf=database_conf, table_name='penguin', required_cols=['island', 'species'], where_clause='1'
    )
    nip.execute()

    # it should run w/o exception
    nip = NoInitPlotter(database_conf=database_conf)
    nip.table_name = 'penguin'
    nip.required_columns = ['island', 'species']
    nip.where_clause = ''
    nip.execute()

    # it should run w/o exception
    nip = NoInitPlotter(database_conf=database_conf)
    nip.table_name = 'penguin'
    nip.required_columns = ['island', 'species']
    nip.where_clause = 'where 1'
    nip.execute()


@pandas_available
def test_mixing_generic_with_hdf(datadir, tmp_path, caplog):
    from mafw.processor_library.plotter import GenericPlotter, HDFDataRetriever
    from mafw.tools.pandas_tools import slice_data_frame

    input_file = datadir / Path('plotter.h5')
    input_df = pd.read_hdf(input_file, key='penguins')

    slicing_dict = {'sex': 'Male'}

    sliced_df = slice_data_frame(input_df, slicing_dict)

    test_file = Path('test_hdf.h5')

    @single_loop
    class HDFPlotter(HDFDataRetriever, GenericPlotter):
        def save(self) -> None:
            output_file = tmp_path / test_file
            self.data_frame.to_hdf(output_file, key='penguins')
            self.output_filename_list.append(output_file)

    hdf = HDFPlotter(slicing_dict=slicing_dict, hdf_filename=input_file, key='penguins')
    hdf.execute()

    # assert if the output file has been created
    assert (tmp_path / test_file).exists()
    # assert that the output dataframe is the sliced one
    gen_sliced_df = pd.read_hdf(tmp_path / test_file, key='penguins')
    assert sliced_df.equals(gen_sliced_df)
    (tmp_path / test_file).unlink()

    grouping_cols = ['species', 'island', 'sex']
    aggregate_functions = ['mean', 'std']

    # reuse the same processor instance. add the aggregation functions, but no grouping column
    # we do not expect the aggregation to take place, so the output should be the same as
    # the previous one
    hdf.aggregation_functions = aggregate_functions
    hdf.execute()
    # assert if the output file has been created
    assert (tmp_path / test_file).exists()
    # assert that the output dataframe is the sliced one
    gen_sliced_df = pd.read_hdf(tmp_path / test_file, key='penguins')
    assert sliced_df.equals(gen_sliced_df)
    (tmp_path / test_file).unlink()

    # now add also the grouping cols
    hdf.grouping_columns = grouping_cols
    hdf.execute()
    # assert if the output file has been created
    assert (tmp_path / test_file).exists()
    agg_df = group_and_aggregate_data_frame(sliced_df, grouping_cols, aggregate_functions)
    gen_agg_df = pd.read_hdf(tmp_path / test_file, key='penguins')
    assert agg_df.equals(gen_agg_df)

    # testing without filename nor key in the constructor
    hdf = HDFPlotter()
    with pytest.raises(PlotterMixinNotInitialized):
        hdf.execute()

    # testing with a not exiting filename
    caplog.clear()
    caplog.set_level(30)  # warning
    with pytest.raises(PlotterMixinNotInitialized):
        hdf.hdf_filename = Path('not_existing.h5')
        hdf.execute()
    assert 'not_existing.h5 is not a valid HDF file' in caplog.text

    # testing with a good file, but without key
    with pytest.raises(PlotterMixinNotInitialized):
        hdf.hdf_filename = input_file
        hdf.execute()


@pandas_available
@seaborn_available
def test_mixing_generic_with_dataset(tmp_path):
    valid_dataset_name = 'iris'
    invalid_dataset_name = 'invalid_iris'

    test_output_file = tmp_path / Path('iris.h5')
    input_df = sns.load_dataset(valid_dataset_name)

    @single_loop
    class DataSetPlotter(FromDatasetDataRetriever, GenericPlotter):
        def __init__(self, output_file: str | Path | None = None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.output_file = Path(output_file) if output_file is not None else Path()

        def save(self):
            self.data_frame.to_hdf(self.output_file, key=self.dataset_name)
            self.output_filename_list.append(self.output_file)

    # test with a valid dataset name
    dsp = DataSetPlotter(dataset_name=valid_dataset_name, output_file=test_output_file)
    assert dsp._attributes_valid()
    dsp.execute()
    assert test_output_file.exists()
    gen_df = pd.read_hdf(test_output_file, key=valid_dataset_name)
    assert input_df.equals(gen_df)
    test_output_file.unlink()

    # test without a dataset name
    dsp = DataSetPlotter(output_file=test_output_file)
    assert not dsp._attributes_valid()
    assert dsp.dataset_name == ''
    with pytest.raises(PlotterMixinNotInitialized):
        dsp.execute()
    assert not test_output_file.exists()

    # set an invalid dataset and do the test
    dsp.dataset_name = invalid_dataset_name
    assert not dsp._attributes_valid()
    with pytest.raises(PlotterMixinNotInitialized):
        dsp.execute()
    assert not test_output_file.exists()

    # set a valid dataset and do the test
    dsp.dataset_name = valid_dataset_name
    assert dsp._attributes_valid()
    dsp.execute()
    assert test_output_file.exists()


@pandas_available
@seaborn_available
def test_direct_plot(tmp_path, mocker):
    output_file = tmp_path / Path('relplot.png')

    @single_loop
    @processor_depends_on_optional(module_name='seaborn')
    class SelfDefinedPlotter(FromDatasetDataRetriever, GenericPlotter):
        def __init__(self, output_png: str | Path | None = None, *args, **kwargs):
            super().__init__(dataset_name='penguins', *args, **kwargs)
            self.output_png = Path(output_png) if output_png is not None else Path()

        def plot(self):
            self.facet_grid = sns.relplot(data=self.data_frame, x='flipper_length_mm', y='bill_length_mm', col='sex')
            self.facet_grid.set_axis_labels('Flipper length (mm)', 'Bill length (mm)')

        def save(self) -> None:
            self.facet_grid.figure.savefig(self.output_png)
            self.output_filename_list.append(self.output_png)

    plot_patch = mocker.patch.object(sns, 'relplot', wraps=sns.relplot)
    sdp = SelfDefinedPlotter(output_png=output_file)
    sdp.execute()
    # assert creation of the output file
    assert output_file.exists()
    plot_patch.assert_called_once_with(data=ANY, x='flipper_length_mm', y='bill_length_mm', col='sex')


def adapt_defaults_kwargs(input_kwargs: dict, default_kwargs: dict, expandable_args: list = []) -> dict:
    adapted_kwargs = default_kwargs.copy()

    # expand all expandable in in the input keywords
    for expandable_key in expandable_args:
        if expandable_key in input_kwargs and input_kwargs[expandable_key] is not None:
            for key in input_kwargs[expandable_key]:
                adapted_kwargs[key] = input_kwargs[expandable_key][key]

    # replace the default values with the actual ones.
    for key in default_kwargs:
        if key in input_kwargs:
            adapted_kwargs[key] = input_kwargs[key]

    return adapted_kwargs


@pytest.fixture
def relplot_default_args():
    args = {
        'data': ANY,
        'x': None,
        'y': None,
        'hue': None,
        'row': None,
        'col': None,
        'palette': None,
        'kind': 'scatter',
        'legend': 'auto',
        'facet_kws': None,
    }
    return args


@pandas_available
@seaborn_available
@pytest.mark.parametrize(
    'plotter_param_dict',
    [
        dict(x='flipper_length_mm', y='bill_length_mm', col='sex', hue='species'),
        dict(
            x='flipper_length_mm',
            y='bill_length_mm',
            col='sex',
            hue='species',
            plot_kws={'aspect': 2},
            facet_kws={'legend_out': True},
            palette='pastel',
            legend=True,
        ),
    ],
)
def test_relplot_mixin_param(plotter_param_dict, relplot_default_args, tmp_path, mocker):
    plot_patch = mocker.patch.object(sns, 'relplot', wraps=sns.relplot)

    @single_loop
    @processor_depends_on_optional(module_name='pandas;seaborn')
    class DataSetRelPlotPlotter(FromDatasetDataRetriever, RelPlot, GenericPlotter):
        def __init__(self, output_png: str | Path | None = None, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.output_png = Path(output_png) if output_png is not None else Path()

        def save(self) -> None:
            self.facet_grid.figure.savefig(self.output_png)
            self.output_filename_list.append(self.output_png)

    output_file = tmp_path / Path('relplot_from_dataset.png')
    dsrp = DataSetRelPlotPlotter(output_file, dataset_name='penguins', **plotter_param_dict)
    dsrp.execute()
    assert output_file.exists()

    adapted_kwargs = adapt_defaults_kwargs(plotter_param_dict, relplot_default_args, ['plot_kws'])
    plot_patch.assert_called_once_with(**adapted_kwargs)


@pytest.fixture
def displot_default_args():
    args = {
        'data': ANY,
        'x': None,
        'y': None,
        'hue': None,
        'row': None,
        'col': None,
        'palette': None,
        'kind': 'hist',
        'legend': True,
        'rug': False,
        'rug_kws': None,
        'facet_kws': None,
    }
    return args


@pandas_available
@seaborn_available
@pytest.mark.parametrize(
    'plotter_param_dict',
    [
        dict(x='flipper_length_mm', kind='kde'),
        dict(x='bill_length_mm', kind='hist', rug=True, rug_kws={'clip_on': False}, plot_kws={'kde': True}),
    ],
)
def test_displot_mixin_param(plotter_param_dict, displot_default_args, tmp_path, mocker):
    plot_patch = mocker.patch.object(sns, 'displot', wraps=sns.displot)

    @single_loop
    @processor_depends_on_optional(module_name='pandas;seaborn')
    class DataSetDisPlotPlotter(FromDatasetDataRetriever, DisPlot, GenericPlotter):
        def __init__(self, output_png: str | Path | None = None, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.output_png = Path(output_png) if output_png is not None else Path()

        def save(self) -> None:
            self.facet_grid.figure.savefig(self.output_png)
            self.output_filename_list.append(self.output_png)

    output_file = tmp_path / Path('displot_from_dataset.png')
    dsrp = DataSetDisPlotPlotter(output_file, dataset_name='penguins', **plotter_param_dict)
    dsrp.execute()
    assert output_file.exists()

    adapted_kwargs = adapt_defaults_kwargs(plotter_param_dict, displot_default_args, ['plot_kws'])
    plot_patch.assert_called_once_with(**adapted_kwargs)


@pytest.fixture
def catplot_default_args():
    args = {
        'data': ANY,
        'x': None,
        'y': None,
        'hue': None,
        'row': None,
        'col': None,
        'palette': None,
        'kind': 'strip',
        'legend': 'auto',
        'native_scale': False,
        'facet_kws': None,
    }
    return args


@pandas_available
@seaborn_available
@pytest.mark.parametrize(
    'plotter_param_dict',
    [
        dict(x='age', y='class'),
        dict(x='age', y='class', hue='sex', kind='boxen', plot_kws=dict(legend_out=False)),
        dict(
            x='age',
            y='class',
            hue='sex',
            kind='violin',
            plot_kws=dict(bw_adjust=0.5, cut=0, split=True),
            facet_kws=dict(despine=False),
        ),
    ],
)
def test_catplot_mixin_param(plotter_param_dict, catplot_default_args, tmp_path, mocker):
    plot_patch = mocker.patch.object(sns, 'catplot', wraps=sns.catplot)

    @single_loop
    @processor_depends_on_optional(module_name='pandas;seaborn')
    class DataSetCatPlotPlotter(FromDatasetDataRetriever, CatPlot, GenericPlotter):
        def __init__(self, output_png: str | Path | None = None, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.output_png = Path(output_png) if output_png is not None else Path()

        def save(self) -> None:
            self.facet_grid.figure.savefig(self.output_png)
            self.output_filename_list.append(self.output_png)

    output_file = tmp_path / Path('catplot_from_dataset.png')
    dsrp = DataSetCatPlotPlotter(output_file, dataset_name='titanic', **plotter_param_dict)
    dsrp.execute()
    assert output_file.exists()

    adapted_kwargs = adapt_defaults_kwargs(plotter_param_dict, catplot_default_args, ['plot_kws'])
    plot_patch.assert_called_once_with(**adapted_kwargs)


def test_loop_plotter(tmp_path):
    @processor_depends_on_optional(module_name='pandas;seaborn')
    class LoopPlotter(FromDatasetDataRetriever, DisPlot, GenericPlotter):
        def __init__(self, base_folder: str | Path | None = None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.dataset_name = 'iris'
            self.hue = 'species'
            self.kind = 'kde'
            self.base_output_folder = Path(base_folder) if base_folder is not None else Path()
            self.base_filename = self.dataset_name
            self.output_filename = Path()

        def get_items(self) -> Collection[Any]:
            return ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']

        def in_loop_customization(self) -> None:
            self.x = self.item
            self.output_filename = self.base_output_folder / Path(self.base_filename + '_' + self.item + '.png')

        def customize_plot(self) -> None:
            self.facet_grid.figure.suptitle(f'Distribution for {self.item}')

        def save(self) -> None:
            self.facet_grid.figure.savefig(self.output_filename)
            self.output_filename_list.append(self.output_filename)

    lp = LoopPlotter(base_folder=tmp_path)
    lp.execute()
    assert len(lp.output_filename_list) == len(lp.get_items())
    assert all(f.exists() for f in lp.output_filename_list)


@pandas_available
@seaborn_available
def test_plotter_output(datadir, penguin, tmp_path):
    Penguin: type[MAFwBaseModel] = penguin

    db_file = datadir / Path(r'plotter.db')
    database_conf = default_conf['sqlite']
    database_conf['URL'] = 'sqlite:///' + str(db_file)

    @processor_depends_on_optional(module_name='seaborn')
    @single_loop
    class MyPlotter(SQLDataRetriever, RelPlot, GenericPlotter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.table_name = Penguin._meta.table_name
            self.required_columns = ['island', 'species', 'sex', 'bill_length', 'bill_depth']
            self.x = 'bill_length'
            self.y = 'bill_depth'
            self.col = 'island'
            self.hue = 'sex'
            self.output_generated = False

        def save(self) -> None:
            output_file = tmp_path / Path('penguin.png')
            self.facet_grid.figure.savefig(output_file)
            self.output_filename_list.append(output_file)
            self.output_generated = True

    plotter = MyPlotter(database_conf=database_conf)
    plotter.execute()

    # check that the output file exists
    assert (tmp_path / Path('penguin.png')).exists()
    # and that the plotter was actually processed till the end.
    assert plotter.output_generated

    database = connect(database_conf['URL'], pragmas=database_conf['pragmas'])
    database_proxy.initialize(database)
    database.connect(reuse_if_open=True)

    # check that the PlotterOutput table exists and that there is MyPlotter
    assert 'plotter_output' in database.get_tables()

    # check that the PlotterOutput has 1 entry.
    assert PlotterOutput.select().count() == 1
    assert PlotterOutput.select().where(PlotterOutput.plotter_name == 'MyPlotter').count() == 1

    plotter = MyPlotter(database_conf=database_conf)
    plotter.execute()

    # the plotter should not have been processed because the output already exists.
    assert not plotter.output_generated

    # remove the output file and re execute
    (tmp_path / Path('penguin.png')).unlink()
    plotter.execute()

    # check that the output file exists
    assert (tmp_path / Path('penguin.png')).exists()
    # and that the plotter was actually processed till the end.
    assert plotter.output_generated

    # remove the entry from the plotter output
    PlotterOutput.delete().where(PlotterOutput.plotter_name == 'MyPlotter').execute()
    assert PlotterOutput.select().where(PlotterOutput.plotter_name == 'MyPlotter').count() == 0
    plotter = MyPlotter(database_conf=database_conf)
    plotter.execute()

    # check that the output file exists
    assert (tmp_path / Path('penguin.png')).exists()
    # and that the plotter was actually processed till the end.
    assert plotter.output_generated
    # assert that the plotter output is populated
    assert PlotterOutput.select().where(PlotterOutput.plotter_name == 'MyPlotter').count() == 1
