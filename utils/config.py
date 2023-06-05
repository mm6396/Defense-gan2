# Copyright 2018 The Defense-GAN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Contains the configuration handling code and default experiment
parameters."""

import os
from absl import flags
import tensorflow as tf
import yaml

FLAGS = flags.FLAGS

type_to_define_fn = {int: flags.DEFINE_integer,
                     float: flags.DEFINE_float,
                     bool: flags.DEFINE_boolean,
                     str : flags.DEFINE_string,
                     type(None): flags.DEFINE_integer,
                     tuple: flags.DEFINE_list,
                     list: flags.DEFINE_list}

# Define cfg_path flag
flags.DEFINE_string('cfg_path', '', 'config path.')

def load_config(cfg_path, set_flag=False, verbose=False):
    """Loads the configuration files into the global flags.

    Args:
        cfg_path: The path to the config yaml file.
        set_flag: If True, does not create new flag attributes, only sets
        existing ones.
        verbose: Verbose mode.

    Returns:
        The loaded configuration dictionary.

    Raises:
        RuntimeError: If the configuration path does not exist.
    """
    if not os.path.exists(cfg_path):
        raise RuntimeError(
            "[!] Configuration path {} does not exist.".format(cfg_path))

    if os.path.isdir(cfg_path):
        cfg_path = os.path.join(cfg_path, 'cfg.yml')
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
    else:
        with open(cfg_path, 'r') as f:
            loaded_cfg = yaml.safe_load(f)

        base_dir = os.path.dirname(cfg_path)
        with open(os.path.join(base_dir, 'default.yml'), 'r') as f:
            cfg = yaml.safe_load(f)
        cfg.update(loaded_cfg)

    with open(os.path.join('experiments/cfgs', 'key_doc.yml')) as f:
        docs = yaml.safe_load(f)

    # Set cfg_path flag value
    setattr(FLAGS, 'cfg_path', cfg_path)

    for (k, v) in cfg.items():
        if set_flag:
            setattr(FLAGS, k.lower(), v)
        else:
            if hasattr(FLAGS, k.lower()):
                setattr(FLAGS, k.lower(), v)
            else:
                def_func = type_to_define_fn[type(v)]
                try:
                    def_func(k.lower(), v, docs[k])
                except KeyError:
                    'Doc for the key {} is not found in the ' \
                    'experimets/cfgs/key_doc.yml'.format(k)
                    def_func(k.lower(), v, 'No doc')
        if verbose:
            print('[#] set {} to {} type: {}'.format(k.lower(), v, str(type(v))))
    cfg['cfg_path'] = cfg_path
    return cfg