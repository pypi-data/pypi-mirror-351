import unittest
import torch
from uois_datasets import get_dataset

class TestUOISDatasets(unittest.TestCase):
    def test_dataset_initialization(self):
        datasets = ['ocid', 'osd', 'robot_pushing', 'iteach_humanplay']
        for dataset_name in datasets:
            dataset = get_dataset(dataset_name, image_set="train", data_path="/path/to/data")
            self.assertIsInstance(dataset, torch.utils.data.Dataset)
            self.assertEqual(dataset._name, f"{dataset_name}_object_train")

if __name__ == '__main__':
    unittest.main()