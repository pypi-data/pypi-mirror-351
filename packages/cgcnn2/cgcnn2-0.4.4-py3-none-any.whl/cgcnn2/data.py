import atexit
import csv
import functools
import json
import os
import random
import shutil
import tempfile
import warnings

import numpy as np
import pandas as pd
import torch
from pymatgen.core.structure import Structure
from torch.utils.data import Dataset


def collate_pool(dataset_list):
    """
    Collate a list of data and return a batch for predicting crystal
    properties.

    Args:
        dataset_list (list of tuples): List of tuples for each data point.
          Each tuple contains:
          - atom_fea (torch.Tensor): shape (n_i, atom_fea_len)
            Atom features for each atom in the crystal
          - nbr_fea (torch.Tensor): shape (n_i, M, nbr_fea_len)
            Bond features for each atom's M neighbors
          - nbr_fea_idx (torch.LongTensor): shape (n_i, M)
            Indices of M neighbors of each atom
          - target (torch.Tensor): shape (1, )
            Target value for prediction
          - cif_id (str or int)
            Unique ID for the crystal


    Returns:
        N = sum(n_i); N0 = sum(i)

        batch_atom_fea: torch.Tensor shape (N, orig_atom_fea_len)
        Atom features from atom type
        batch_nbr_fea: torch.Tensor shape (N, M, nbr_fea_len)
        Bond features of each atom's M neighbors
        batch_nbr_fea_idx: torch.LongTensor shape (N, M)
        Indices of M neighbors of each atom
        crystal_atom_idx: list of torch.LongTensor of length N0
        Mapping from the crystal idx to atom idx
        target: torch.Tensor shape (N, 1)
        Target value for prediction
        batch_cif_ids: list
    """
    batch_atom_fea, batch_nbr_fea, batch_nbr_fea_idx = [], [], []
    crystal_atom_idx, batch_target = [], []
    batch_cif_ids = []
    base_idx = 0
    for i, ((atom_fea, nbr_fea, nbr_fea_idx), target, cif_id) in enumerate(
        dataset_list
    ):
        n_i = atom_fea.shape[0]  # number of atoms for this crystal
        batch_atom_fea.append(atom_fea)
        batch_nbr_fea.append(nbr_fea)
        batch_nbr_fea_idx.append(nbr_fea_idx + base_idx)
        new_idx = torch.LongTensor(np.arange(n_i) + base_idx)
        crystal_atom_idx.append(new_idx)
        batch_target.append(target)
        batch_cif_ids.append(cif_id)
        base_idx += n_i
    return (
        (
            torch.cat(batch_atom_fea, dim=0),
            torch.cat(batch_nbr_fea, dim=0),
            torch.cat(batch_nbr_fea_idx, dim=0),
            crystal_atom_idx,
        ),
        torch.stack(batch_target, dim=0),
        batch_cif_ids,
    )


class GaussianDistance(object):
    """
    Expands the distance by Gaussian basis.

    Unit: angstrom
    """

    def __init__(self, dmin, dmax, step, var=None):
        """
        Args:
            dmin (float): Minimum interatomic distance
            dmax (float): Maximum interatomic distance
            step (float): Step size for the Gaussian filter
        """
        assert dmin < dmax
        assert dmax - dmin > step
        self.filter = np.arange(dmin, dmax + step, step)
        if var is None:
            var = step
        self.var = var

    def expand(self, distances):
        """
        Apply Gaussian distance filter to a numpy distance array

        Args:
            distances (np.ndarray): A distance matrix of any shape

        Returns:
            expanded_distance: shape (n+1)-d array
              Expanded distance matrix with the last dimension of length
              len(self.filter)
        """
        return np.exp(-((distances[..., np.newaxis] - self.filter) ** 2) / self.var**2)


class AtomInitializer(object):
    """
    Base class for initializing the vector representation for atoms.

    Use one `AtomInitializer` per dataset.
    """

    def __init__(self, atom_types):
        self.atom_types = set(atom_types)
        self._embedding = {}

    def get_atom_fea(self, atom_type):
        assert atom_type in self.atom_types
        return self._embedding[atom_type]

    def load_state_dict(self, state_dict):
        self._embedding = state_dict
        self.atom_types = set(self._embedding.keys())
        self._decodedict = {
            idx: atom_type for atom_type, idx in self._embedding.items()
        }

    def state_dict(self):
        return self._embedding

    def decode(self, idx):
        if not hasattr(self, "_decodedict"):
            self._decodedict = {
                idx: atom_type for atom_type, idx in self._embedding.items()
            }
        return self._decodedict[idx]


class AtomCustomJSONInitializer(AtomInitializer):
    """
    Initialize atom feature vectors using a JSON file, which is a python
    dictionary mapping from element number to a list representing the
    feature vector of the element.

    Args:
        elem_embedding_file (str): The path to the .json file
    """

    def __init__(self, elem_embedding_file):
        with open(elem_embedding_file) as f:
            elem_embedding = json.load(f)
        elem_embedding = {int(key): value for key, value in elem_embedding.items()}
        atom_types = set(elem_embedding.keys())
        super(AtomCustomJSONInitializer, self).__init__(atom_types)
        for key, value in elem_embedding.items():
            self._embedding[key] = np.array(value, dtype=float)


class CIFData(Dataset):
    """
    The CIFData dataset is a wrapper for a dataset where the crystal structures
    are stored in the form of CIF files.

    id_prop.csv: a CSV file with two columns. The first column recodes a
    unique ID for each crystal, and the second column recodes the value of
    target property.

    atom_init.json: a JSON file that stores the initialization vector for each
    element.

    ID.cif: a CIF file that recodes the crystal structure, where ID is the
    unique ID for the crystal.

    Args:
        root_dir (str): The path to the root directory of the dataset
        max_num_nbr (int): The maximum number of neighbors while constructing the crystal graph
        radius (float): The cutoff radius for searching neighbors
        dmin (float): The minimum distance for constructing GaussianDistance
        step (float): The step size for constructing GaussianDistance
        random_seed (int): Random seed for shuffling the dataset

    Returns:
        atom_fea: torch.Tensor shape (n_i, atom_fea_len)
        nbr_fea: torch.Tensor shape (n_i, M, nbr_fea_len)
        nbr_fea_idx: torch.LongTensor shape (n_i, M)
        target: torch.Tensor shape (1, )
        cif_id: str or int
    """

    def __init__(
        self, root_dir, max_num_nbr=12, radius=8, dmin=0, step=0.2, random_seed=123
    ):
        self.root_dir = root_dir
        self.max_num_nbr, self.radius = max_num_nbr, radius
        assert os.path.exists(root_dir), "root_dir does not exist!"
        id_prop_file = os.path.join(self.root_dir, "id_prop.csv")
        assert os.path.exists(id_prop_file), "id_prop.csv does not exist!"
        with open(id_prop_file) as f:
            reader = csv.reader(f)
            self.id_prop_data = [row for row in reader]
        random.seed(random_seed)
        atom_init_file = os.path.join(self.root_dir, "atom_init.json")
        assert os.path.exists(atom_init_file), "atom_init.json does not exist!"
        self.ari = AtomCustomJSONInitializer(atom_init_file)
        self.gdf = GaussianDistance(dmin=dmin, dmax=self.radius, step=step)

    def __len__(self):
        return len(self.id_prop_data)

    @functools.lru_cache(maxsize=None)  # Cache loaded structures
    def __getitem__(self, idx):
        cif_id, target = self.id_prop_data[idx]
        crystal = Structure.from_file(os.path.join(self.root_dir, cif_id + ".cif"))
        atom_fea = np.vstack(
            [
                self.ari.get_atom_fea(crystal[i].specie.number)
                for i in range(len(crystal))
            ]
        )
        atom_fea = torch.Tensor(atom_fea)
        all_nbrs = crystal.get_all_neighbors(self.radius, include_index=True)
        all_nbrs = [sorted(nbrs, key=lambda x: x[1]) for nbrs in all_nbrs]
        nbr_fea_idx, nbr_fea = [], []
        for nbr in all_nbrs:
            if len(nbr) < self.max_num_nbr:
                warnings.warn(
                    "{} not find enough neighbors to build graph. "
                    "If it happens frequently, consider increase "
                    "radius.".format(cif_id),
                    stacklevel=2,
                )
                nbr_fea_idx.append(
                    list(map(lambda x: x[2], nbr)) + [0] * (self.max_num_nbr - len(nbr))
                )
                nbr_fea.append(
                    list(map(lambda x: x[1], nbr))
                    + [self.radius + 1.0] * (self.max_num_nbr - len(nbr))
                )
            else:
                nbr_fea_idx.append(list(map(lambda x: x[2], nbr[: self.max_num_nbr])))
                nbr_fea.append(list(map(lambda x: x[1], nbr[: self.max_num_nbr])))
        nbr_fea_idx, nbr_fea = np.array(nbr_fea_idx), np.array(nbr_fea)
        nbr_fea = self.gdf.expand(nbr_fea)
        atom_fea = torch.Tensor(atom_fea)
        nbr_fea = torch.Tensor(nbr_fea)
        nbr_fea_idx = torch.LongTensor(nbr_fea_idx)
        target = torch.Tensor([float(target)])
        return (atom_fea, nbr_fea, nbr_fea_idx), target, cif_id


class CIFData_NoTarget(Dataset):
    """
    The CIFData_NoTarget dataset is a wrapper for a dataset where the crystal
    structures are stored in the form of CIF files.

    atom_init.json: a JSON file that stores the initialization vector for each
    element.

    ID.cif: a CIF file that recodes the crystal structure, where ID is the
    unique ID for the crystal.

    Args:
        root_dir (str): The path to the root directory of the dataset
        max_num_nbr (int): The maximum number of neighbors while constructing the crystal graph
        radius (float): The cutoff radius for searching neighbors
        dmin (float): The minimum distance for constructing GaussianDistance
        step (float): The step size for constructing GaussianDistance
        random_seed (int): Random seed for shuffling the dataset

    Returns:
        atom_fea: torch.Tensor shape (n_i, atom_fea_len)
        nbr_fea: torch.Tensor shape (n_i, M, nbr_fea_len)
        nbr_fea_idx: torch.LongTensor shape (n_i, M)
        target: torch.Tensor shape (1, )
        cif_id: str or int
    """

    def __init__(
        self, root_dir, max_num_nbr=12, radius=8, dmin=0, step=0.2, random_seed=123
    ):
        self.root_dir = root_dir
        self.max_num_nbr, self.radius = max_num_nbr, radius
        assert os.path.exists(root_dir), "root_dir does not exist!"
        id_prop_data = []
        for file in os.listdir(root_dir):
            if file.endswith(".cif"):
                id_prop_data.append(file[:-4])
        id_prop_data = [(cif_id, 0) for cif_id in id_prop_data]
        id_prop_data.sort(key=lambda x: x[0])
        self.id_prop_data = id_prop_data
        random.seed(random_seed)
        atom_init_file = os.path.join(self.root_dir, "atom_init.json")
        assert os.path.exists(atom_init_file), "atom_init.json does not exist!"
        self.ari = AtomCustomJSONInitializer(atom_init_file)
        self.gdf = GaussianDistance(dmin=dmin, dmax=self.radius, step=step)

    def __len__(self):
        return len(self.id_prop_data)

    @functools.lru_cache(maxsize=1024)  # Cache loaded structures
    def __getitem__(self, idx):
        cif_id, target = self.id_prop_data[idx]
        crystal = Structure.from_file(os.path.join(self.root_dir, cif_id + ".cif"))
        atom_fea = np.vstack(
            [
                self.ari.get_atom_fea(crystal[i].specie.number)
                for i in range(len(crystal))
            ]
        )
        atom_fea = torch.Tensor(atom_fea)
        all_nbrs = crystal.get_all_neighbors(self.radius, include_index=True)
        all_nbrs = [sorted(nbrs, key=lambda x: x[1]) for nbrs in all_nbrs]
        nbr_fea_idx, nbr_fea = [], []
        for nbr in all_nbrs:
            if len(nbr) < self.max_num_nbr:
                warnings.warn(
                    "{} not find enough neighbors to build graph. "
                    "If it happens frequently, consider increase "
                    "radius.".format(cif_id),
                    stacklevel=2,
                )
                nbr_fea_idx.append(
                    list(map(lambda x: x[2], nbr)) + [0] * (self.max_num_nbr - len(nbr))
                )
                nbr_fea.append(
                    list(map(lambda x: x[1], nbr))
                    + [self.radius + 1.0] * (self.max_num_nbr - len(nbr))
                )
            else:
                nbr_fea_idx.append(list(map(lambda x: x[2], nbr[: self.max_num_nbr])))
                nbr_fea.append(list(map(lambda x: x[1], nbr[: self.max_num_nbr])))
        nbr_fea_idx, nbr_fea = np.array(nbr_fea_idx), np.array(nbr_fea)
        nbr_fea = self.gdf.expand(nbr_fea)
        atom_fea = torch.Tensor(atom_fea)
        nbr_fea = torch.Tensor(nbr_fea)
        nbr_fea_idx = torch.LongTensor(nbr_fea_idx)
        target = torch.Tensor([float(target)])
        return (atom_fea, nbr_fea, nbr_fea_idx), target, cif_id


def train_force_ratio(total_set, force_set, train_ratio, random_seed: int = 0):
    """
    Set up a training dataset with a forced training set,
    and keep the same input splitting ratio of the training set.

    Args:
        total_set (str): The path to the total set
        force_set (str): The path to the forced training set
        train_ratio (float): The ratio of the training set
        random_seed (int): The random seed for the split
    Returns:
        train_dataset: CIFData
            The training dataset
        valid_test_dataset: CIFData
            The validation set
    """
    random.seed(random_seed)

    # create a new temporary directory for the training set
    temp_train_dir = tempfile.mkdtemp()
    temp_valid_test_dir = tempfile.mkdtemp()

    shutil.copy(f"{total_set}/atom_init.json", temp_train_dir)
    shutil.copy(f"{total_set}/atom_init.json", temp_valid_test_dir)

    # Register cleanup functions
    atexit.register(lambda: shutil.rmtree(temp_train_dir, ignore_errors=True))
    atexit.register(lambda: shutil.rmtree(temp_valid_test_dir, ignore_errors=True))

    # concatenate the two csv files in the temp_train_dir
    train_force_csv = pd.read_csv(f"{force_set}/id_prop.csv", header=None)
    split_csv = pd.read_csv(f"{total_set}/id_prop.csv", header=None)
    total_csv = pd.concat([train_force_csv, split_csv])

    train_force_cif_files = [f for f in os.listdir(force_set) if f.endswith(".cif")]
    total_cif_files = [f for f in os.listdir(total_set) if f.endswith(".cif")]

    for file in train_force_cif_files:
        shutil.copy(
            os.path.join(force_set, file),
            os.path.join(temp_train_dir, file),
        )

    train_force_size = len(train_force_cif_files)
    total_size = len(total_cif_files)
    train_size = int(round(total_size * train_ratio))
    train_split_size = int(max(train_size - train_force_size, 0))

    if train_split_size > 0:
        train_split_cif_files = random.sample(total_cif_files, train_split_size)
        valid_test_cif_files = [
            f for f in total_cif_files if f not in train_split_cif_files
        ]
        valid_test_cif_ids = [f[:-4] for f in valid_test_cif_files]

        for file in train_split_cif_files:
            shutil.copy(
                os.path.join(total_set, file),
                os.path.join(temp_train_dir, file),
            )

        for file in valid_test_cif_files:
            shutil.copy(
                os.path.join(total_set, file),
                os.path.join(temp_valid_test_dir, file),
            )

        train_csv = total_csv[~total_csv[total_csv.columns[0]].isin(valid_test_cif_ids)]
        train_csv.to_csv(f"{temp_train_dir}/id_prop.csv", index=False, header=False)

        valid_test_csv = total_csv[
            total_csv[total_csv.columns[0]].isin(valid_test_cif_ids)
        ]
        valid_test_csv.to_csv(
            f"{temp_valid_test_dir}/id_prop.csv", index=False, header=False
        )

        train_dataset = CIFData(temp_train_dir)
        valid_test_dataset = CIFData(temp_valid_test_dir)

        return train_dataset, valid_test_dataset

    else:
        raise ValueError(
            f"Forced training set is larger than expected training set. Expected: {train_size}, Forced: {train_force_size}"
        )


def train_force_set(
    total_set: str, force_set: str, train_ratio: float, random_seed: int = 0
):
    """
    Split a *full* data directory into train/valid+test **and** make sure every
    structure in `force_set` ends up in the training subset *without*
    shrinking the random portion to keep the original ratio.

    Args:
        total_set (str): Directory that contains the full candidate pool
        force_set (str): Directory whose *.cif files must be included in training
        train_ratio (float): Fraction of `total_set` that should be assigned to the training split before the forced set is added.
            E.g. 0.8 ⇒ 80 % of `total_set` + 100 % of `force_set`.
        random_seed (int): Random seed for shuffling the dataset
    Returns:
        train_dataset (CIFData): The training dataset
        valid_test_dataset (CIFData): The validation and test dataset
    """
    random.seed(random_seed)

    # Validate inputs
    if not os.path.exists(total_set):
        raise ValueError(f"Total set directory does not exist: {total_set}")
    if not os.path.exists(force_set):
        raise ValueError(f"Force set directory does not exist: {force_set}")

    # Create temporary directories
    temp_train_dir = tempfile.mkdtemp()
    temp_valid_test_dir = tempfile.mkdtemp()

    # Register cleanup functions
    atexit.register(lambda: shutil.rmtree(temp_train_dir, ignore_errors=True))
    atexit.register(lambda: shutil.rmtree(temp_valid_test_dir, ignore_errors=True))

    shutil.copy(f"{total_set}/atom_init.json", temp_train_dir)
    shutil.copy(f"{total_set}/atom_init.json", temp_valid_test_dir)

    force_csv = pd.read_csv(f"{force_set}/id_prop.csv", header=None)
    total_csv = pd.read_csv(f"{total_set}/id_prop.csv", header=None)
    merged_csv = pd.concat([force_csv, total_csv]).drop_duplicates()

    force_cifs = [f for f in os.listdir(force_set) if f.endswith(".cif")]
    total_cifs = [f for f in os.listdir(total_set) if f.endswith(".cif")]

    for fname in force_cifs:
        shutil.copy(os.path.join(force_set, fname), os.path.join(temp_train_dir, fname))

    total_size = len(total_cifs)
    train_random_size = int(round(total_size * train_ratio))

    # Ensure no overlap between force and total sets to prevent data leakage
    force_ids = {f[:-4] for f in force_cifs}
    total_ids = {f[:-4] for f in total_cifs}
    overlap = force_ids.intersection(total_ids)
    if overlap:
        warnings.warn(
            f"Found {len(overlap)} overlapping files between force set and total set. "
            f"These will only appear in training set to prevent data leakage."
        )

    pool_cifs = [f for f in total_cifs if f[:-4] not in force_ids]

    random_train_cifs = random.sample(pool_cifs, min(train_random_size, len(pool_cifs)))
    valid_test_cifs = [f for f in pool_cifs if f not in random_train_cifs]

    for fname in random_train_cifs:
        shutil.copy(os.path.join(total_set, fname), os.path.join(temp_train_dir, fname))

    for fname in valid_test_cifs:
        shutil.copy(
            os.path.join(total_set, fname), os.path.join(temp_valid_test_dir, fname)
        )

    valid_test_ids = [f[:-4] for f in valid_test_cifs]

    merged_csv.loc[~merged_csv[0].isin(valid_test_ids)].to_csv(
        f"{temp_train_dir}/id_prop.csv", index=False, header=False
    )

    merged_csv.loc[merged_csv[0].isin(valid_test_ids)].to_csv(
        f"{temp_valid_test_dir}/id_prop.csv", index=False, header=False
    )

    train_dataset = CIFData(temp_train_dir)
    valid_test_dataset = CIFData(temp_valid_test_dir)

    return train_dataset, valid_test_dataset
