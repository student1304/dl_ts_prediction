import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import datetime
import json
import pandas as pd

plt.rcParams["font.family"] = "Times New Roman"


def _plot(*args, **kwargs):
    plt.close('all')
    plt.plot(*args, **kwargs)
    plt.legend(loc="best")
    plt.show()
    return


def plot_results(true, predicted, name=None, **kwargs):
    """
    # kwargs can be any/all of followings
        # fillstyle:
        # marker:
        # linestyle:
        # markersize:
        # color:
    """

    regplot_using_searborn(true, predicted, name)
    fig, axis = plt.subplots()
    set_fig_dim(fig, 12, 8)
    axis.plot(true, **kwargs, color='b', label='True')
    axis.plot(predicted, **kwargs, color='r', label='predicted')
    axis.legend(loc="best", fontsize=22, markerscale=4)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    if name is not None:
        plt.savefig(name, dpi=300, bbox_inches='tight')
    plt.show()

    return


def regplot_using_searborn(true, pred, name):
    # https://seaborn.pydata.org/generated/seaborn.regplot.html
    plt.close('all')
    sns.regplot(x=true, y=pred, color="g")
    plt.xlabel('Observed', fontsize=14)
    plt.ylabel('Predicted', fontsize=14)

    if name is not None:
        plt.savefig(name + '_reg', dpi=300, bbox_inches='tight')
    plt.show()


def plot_loss(history: dict, name=None):


    plt.clf()
    plt.close('all')
    fig = plt.figure()
    plt.style.use('ggplot')
    i = 1

    epochs = range(1, len(history['loss']) + 1)
    axis_cache = {}

    for key, val in history.items():

        m_name = key.split('_')[1] if '_' in key else key

        if m_name in list(axis_cache.keys()):
            axis = axis_cache[m_name]
            axis.plot(epochs, val, color=[0.96707953, 0.46268314, 0.45772886], label= 'Validation ' + m_name)
            axis.legend()
        else:
            axis = fig.add_subplot(2, 2, i)
            axis.plot(epochs, val, color=[0.13778617, 0.06228198, 0.33547859], label= 'Training ' + key)
            axis.legend()
            axis_cache[key] = axis
            i += 1

    if name is not None:
        plt.savefig(name, dpi=300, bbox_inches='tight')
    plt.show()

    return


def set_fig_dim(fig, width, height):
    fig.set_figwidth(width)
    fig.set_figheight(height)


def plot_train_test_pred(y, obs, tr_idx, test_idx):
    yf_tr = np.full(len(y), np.nan)
    yf_test = np.full(len(y), np.nan)
    yf_tr[tr_idx.reshape(-1, )] = y[tr_idx.reshape(-1, )].reshape(-1, )
    yf_test[test_idx.reshape(-1, )] = y[test_idx.reshape(-1, )].reshape(-1, )

    fig, axis = plt.subplots()
    set_fig_dim(fig, 14, 8)
    axis.plot(obs, '-', label='True')
    axis.plot(yf_tr, '.', label='predicted train')
    axis.plot(yf_test, '.', label='predicted test')
    axis.legend(loc="best", fontsize=18, markerscale=4)

    plt.show()


def maybe_create_path(prefix=None, path=None):
    if path is None:
        save_dir = dateandtime_now()
        model_dir = os.path.join(os.getcwd(), "results")

        if prefix:
            model_dir = os.path.join(model_dir, prefix)

        save_dir = os.path.join(model_dir, save_dir)
    else:
        save_dir = path

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    act_dir = os.path.join(save_dir, 'activations')
    if not os.path.exists(act_dir):
        os.makedirs(act_dir)

    weigth_dir = os.path.join(save_dir, 'weights')
    if not os.path.exists(weigth_dir):
        os.makedirs(weigth_dir)

    return save_dir, act_dir, weigth_dir


def dateandtime_now():
    jetzt = datetime.datetime.now()
    jahre = str(jetzt.year)
    month = str(jetzt.month)
    if len(month) < 2:
        month = '0' + month
    tag = str(jetzt.day)
    if len(tag) < 2:
        tag = '0' + tag
    datum = jahre + month + tag

    stunde = str(jetzt.hour)
    if len(stunde) < 2:
        stunde = '0' + stunde
    minute = str(jetzt.minute)
    if len(minute) < 2:
        minute = '0' + minute

    return datum + '_' + stunde + str(minute)


def save_config_file(path, config=None, errors=None, indices=None, name=''):

    sort_keys = True
    if errors is not None:
        suffix = dateandtime_now()
        fpath = path + "/errors_" + name +  suffix + ".json"
        data = errors
    elif config is not None:
        fpath = path + "/config.json"
        data = config
        sort_keys = False
    elif indices is not None:
        fpath = path + "/indices.json"
        data = indices
    else:
        raise ValueError("")

    with open(fpath, 'w') as fp:
        json.dump(data, fp, sort_keys=sort_keys, indent=4)

    return


def skopt_plots(search_result, pref=''):

    from skopt.plots import plot_evaluations, plot_objective, plot_convergence

    _ = plot_evaluations(search_result)
    plt.savefig(pref + '_evaluations', dpi=400, bbox_inches='tight')
    plt.show()

    _ = plot_objective(search_result)
    plt.savefig(pref + '_objective', dpi=400, bbox_inches='tight')
    plt.show()

    _ = plot_convergence(search_result)
    plt.savefig(pref + '_convergence', dpi=400, bbox_inches='tight')
    plt.show()


def check_min_loss(epoch_losses, _epoch, _msg:str, _save_fg:bool, to_save=None):
    epoch_loss_array = epoch_losses[:-1]

    current_epoch_loss = epoch_losses[-1]

    if len(epoch_loss_array) > 0:
        min_loss = np.min(epoch_loss_array)
    else:
        min_loss = current_epoch_loss

    if np.less(current_epoch_loss, min_loss):
        _msg = _msg + "    {:10.5f} ".format(current_epoch_loss)

        if to_save is not None:
            _save_fg = True
    else:
        _msg = _msg + "              "

    return _msg, _save_fg


def make_model(**kwargs):
    """
    This functions fills the default arguments needed to run all the models. All the input arguments can be overwritten
    by providing their name.
    :return
      nn_config: `dict`, contais parameters to build and train the neural network such as `layers`
      data_config: `dict`, contains parameters for data preparation/pre-processing/post-processing etc.
      intervals:  `tuple` tuple of tuples whiere each tuple consits of two integers, marking the start and end of
                   interval. An interval here means chunk/rows from the input file/dataframe to be skipped when
                   when preparing data/batches for NN. This happens when we have for example some missing values at some
                   time in our data. For further usage see `docs/using_intervals`.
    """
    nn_config = dict()

    nn_config['layers'] = {
        "Dense_0": {'config': {'units': 64, 'activation': 'relu'}},
        "Dropout_0": {'config':  {'rate': 0.3}},
        "Dense_1": {'config':  {'units': 32, 'activation': 'relu'}},
        "Dropout_1": {'config':  {'rate': 0.3}},
        "Dense_2": {'config':  {'units': 16, 'activation': 'relu'}},
        "Dense_3": {'config':  {'units': 1}}
                                 }

    nn_config['enc_config'] = {'n_h': 20,  # length of hidden state m
                                'n_s': 20,  # length of hidden state m
                                'm': 20,  # length of hidden state m
                                'enc_lstm1_act': None,
                                'enc_lstm2_act': None,
                                }
    nn_config['dec_config'] = {
        'p': 30,
        'n_hde0': 30,
        'n_sde0': 30
    }

    nn_config['composite'] = False  # for auto-encoders

    nn_config['lr'] = 0.0001
    nn_config['optimizer'] = 'adam'
    nn_config['loss'] = 'mse'
    nn_config['epochs'] = 14
    nn_config['min_val_loss'] = 0.0001
    nn_config['patience'] = 100

    nn_config['subsequences'] = 3  # used for cnn_lst structure

    nn_config['HARHN_config'] = {'n_conv_lyrs': 3,
                                  'enc_units': 64,
                                  'dec_units': 64}

    nn_config['nbeats_options'] = {
        'backcast_length': 15 if 'lookback' not in kwargs else int(kwargs['lookback']),
        'forecast_length': 1,
        'stack_types': ('generic', 'generic'),
        'nb_blocks_per_stack': 2,
        'thetas_dim': (4, 4),
        'share_weights_in_stack': True,
        'hidden_layer_units': 62
    }

    data_config = dict()
    data_config['lookback'] = 15
    data_config['batch_size'] = 32
    data_config['val_fraction'] = 0.2  # fraction of data to be used for validation
    data_config['val_data'] = None # If this is not string and not None, this will overwite `val_fraction`
    data_config['steps_per_epoch'] = None
    data_config['test_fraction'] = 0.2
    data_config['CACHEDATA'] = True
    data_config['ignore_nans'] = False  # if True, and if target values contain Nans, those samples will not be ignored
    data_config['use_predicted_output'] = True  # if true, model will use previous predictions as input
    data_config['metrics'] = None  # can be string or list of strings such as 'mse', 'kge', 'nse', 'pbias'

    # input features in data_frame
    dpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    _df = pd.read_csv(os.path.join(dpath, "nasdaq100_padding.csv"))
    in_cols = list(_df.columns)
    in_cols.remove("NDX")
    data_config['inputs'] = in_cols
    # column in dataframe to bse used as output/target
    data_config['outputs'] = ["NDX"]

    nn_config['dense_config'] = {1: {'units':1}}

    for key, val in kwargs.items():
        if key in data_config:
            data_config[key] = val
        if key in nn_config:
            nn_config[key] = val

    total_intervals = (
        (0, 146,),
        (145, 386,),
        (385, 628,),
        (625, 821,),
        (821, 1110),
        (1110, 1447))

    return data_config, nn_config, total_intervals

def get_index(idx_array, fmt='%Y%m%d%H%M'):
    """ converts a numpy 1d array into pandas DatetimeIndex type."""

    if not isinstance(idx_array, np.ndarray):
        raise TypeError

    return pd.to_datetime(idx_array.astype(str), format=fmt)