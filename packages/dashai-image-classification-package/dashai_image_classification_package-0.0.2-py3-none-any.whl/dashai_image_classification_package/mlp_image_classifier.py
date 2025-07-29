import datasets
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data
from DashAI.back.core.schema_fields import (
    BaseSchema,
    float_field,
    int_field,
    list_field,
    schema_field,
)
from DashAI.back.models.base_model import BaseModel
from torch.utils.data import DataLoader
from torchvision import transforms


class MLPImageClassifierSchema(BaseSchema):
    """
    Schema for MLP Image Classifier configuration parameters.

    Attributes:
        epochs (int): Number of training epochs. Must be >= 1.
        learning_rate (float): Learning rate for model training.
        hidden_dims (list[int]): List of dimensions for hidden layers.
    """
    epochs: schema_field(
        int_field(ge=1),
        placeholder=10,
        description=(
            "The number of epochs to train the model. An epoch is a full "
            "iteration over the training data. It must be an integer greater "
            "or equal than 1"
        ),
    )  # type: ignore

    learning_rate: schema_field(
        float_field(),
        placeholder=0.001,
        description=(
            "Training learning rate"
        ),
    )  # type: ignore

    hidden_dims: schema_field(
        list_field(int_field(ge=1), min_items=1),
        placeholder=[128, 64],
        description=(
            "The hidden layers and their dimensions. Please specify the "
            "number of units of each layer separated by commas."
        ),
    )  # type: ignore


class ImageDataset(torch.utils.data.Dataset):
    """
    Custom dataset class for handling image data.

    This class processes images from a HuggingFace dataset and applies necessary
    transformations for model training.
    """
    def __init__(self, dataset: datasets.Dataset):
        self.dataset = dataset
        self.transforms = transforms.Compose(
            [
                transforms.Resize((30, 30)),
                transforms.ToTensor(),
            ]
        )

        column_names = list(self.dataset.features.keys())
        self.image_col_name = column_names[0]
        if len(column_names) > 1:
            self.label_col_name = column_names[1]
        else:
            self.label_col_name = None
        self.tensor_shape = self.transforms(
            self.dataset[0][self.image_col_name]
        ).shape

    def num_classes(self):
        """
        Returns the number of unique classes in the dataset.

        Returns:
            int: Number of unique classes if labels exist, 0 otherwise.
        """
        if self.label_col_name is None:
            return 0
        label_column = self.dataset[self.label_col_name]
        return len(set(label_column))

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        """
        Returns a single data point from the dataset.

        Args:
            idx (int): Index of the data point to retrieve.

        Returns:
            tuple or tensor: (image, label) if labels exist, otherwise just
            image.
        """
        if self.label_col_name is None:
            image = self.dataset[idx][self.image_col_name]
            image = self.transforms(image)
            return image
        image = self.dataset[idx][self.image_col_name]
        image = self.transforms(image)
        label = self.dataset[idx][self.label_col_name]
        return image, label


class MLP(nn.Module):
    """
    Multi-Layer Perceptron neural network for image classification.

    This class implements a feed-forward neural network with configurable
    hidden layers and ReLU activation.
    """
    def __init__(self, input_dim, output_dim, hidden_dims):
        super().__init__()
        self.hidden_layers = nn.ModuleList()
        previous_dim = input_dim

        for hidden_dim in hidden_dims:
            self.hidden_layers.append(nn.Linear(previous_dim, hidden_dim))
            previous_dim = hidden_dim

        self.output_layer = nn.Linear(previous_dim, output_dim)
        self.relu = nn.ReLU()

    def forward(self, input: torch.Tensor):
        """
        Forward pass through the network.

        Args:
            input (torch.Tensor): Input tensor of shape (batch_size, channels, height, width)

        Returns:
            torch.Tensor: Output tensor of shape (batch_size, num_classes)
        """
        batch_size = input.shape[0]
        x = input.view(batch_size, -1)

        for layer in self.hidden_layers:
            x = self.relu(layer(x))

        x = self.output_layer(x)
        return x


class MLPImageClassifier(BaseModel):
    """
    MLP-based image classifier implementation.

    This class implements a complete image classification pipeline using
    a Multi-Layer Perceptron neural network.
    """
    SCHEMA = MLPImageClassifierSchema
    COMPATIBLE_COMPONENTS = ["ImageClassificationTask"]

    def __init__(self, epochs: int = 10, hidden_dims=None, **kwargs):
        """
        Initializes the MLP Image Classifier.

        Args:
            epochs (int): Number of training epochs
            hidden_dims (list[int]): Dimensions of hidden layers
            **kwargs: Additional keyword arguments
        """
        if hidden_dims is None:
            hidden_dims = [128, 64]
        self.epochs = epochs
        self.hidden_dims = hidden_dims
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model = None

    def fit(self, x: datasets.Dataset, y: datasets.Dataset):
        """
        Trains the model on the provided dataset.

        Args:
            x (datasets.Dataset): Input dataset containing images
            y (datasets.Dataset): Target dataset containing labels
        """
        dataset = datasets.Dataset.from_dict(
            {
                "image": x["image"],
                "label": y["label"],
            }
        )
        image_dataset = ImageDataset(dataset)
        self.input_dim = (
            image_dataset.tensor_shape[0]
            * image_dataset.tensor_shape[1]
            * image_dataset.tensor_shape[2]
        )
        self.output_dim = image_dataset.num_classes()
        train_loader = DataLoader(image_dataset, batch_size=32, shuffle=True)
        self.model = MLP(
            self.input_dim,
            self.output_dim,
            self.hidden_dims
        ).to(self.device)
        self.criteria = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.005)
        self.model = self._train_model(
            train_loader,
            self.epochs,
            self.criteria,
            self.optimizer,
            self.device,
        )

    def predict(self, x: datasets.Dataset):
        """
        Makes predictions on the input dataset.

        Args:
            x (datasets.Dataset): Input dataset containing images

        Returns:
            list: List of predicted probabilities for each class
        """
        image_dataset = ImageDataset(x)
        test_loader = DataLoader(image_dataset, batch_size=32, shuffle=False)
        self.model.eval()
        probs_predicted = []
        with torch.no_grad():
            for images in test_loader:
                images = images.to(self.device)
                output_probs: torch.Tensor = self.model(images)
                probs_predicted += output_probs.tolist()
        return probs_predicted

    def save(self, filename: str) -> None:
        """
        Saves the complete model checkpoint.

        Args:
            filename (str): Path where to save the checkpoint
        """
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epochs': self.epochs,
            'hidden_dims': self.hidden_dims,
            'input_dim': self.input_dim,
            'output_dim': self.output_dim,
            'device': self.device,
        }
        torch.save(checkpoint, filename)

    @classmethod
    def load(cls, filename: str):
        """
        Loads a complete model checkpoint.

        Args:
            filename (str): Path to the checkpoint file

        Returns:
            MLPImageClassifier: Instance of the classifier with loaded weights
        """
        checkpoint = torch.load(filename, map_location=torch.device("cpu"))
        model = MLP(
            checkpoint['input_dim'],
            checkpoint['output_dim'],
            checkpoint['hidden_dims']
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer = optim.Adam(model.parameters())
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        instance = cls(
            epochs=checkpoint['epochs'],
            hidden_dims=checkpoint['hidden_dims'],
            device=checkpoint['device'],
        )
        instance.model = model
        instance.optimizer = optimizer
        instance.input_dim = checkpoint['input_dim']
        instance.output_dim = checkpoint['output_dim']
        return instance

    def _train_model(
        self,
        train_loader: DataLoader,
        epochs: int,
        criterion: nn.Module,
        optimizer: optim.Optimizer,
        device: torch.device,
    ):
        """
        Internal method to train the model.

        Args:
            train_loader (DataLoader): DataLoader for training data
            epochs (int): Number of training epochs
            criterion (nn.Module): Loss function
            optimizer (optim.Optimizer): Optimizer for model parameters
            device (torch.device): Device to run training on (CPU/GPU)

        Returns:
            nn.Module: Trained model
        """
        self.model.train()
        for _ in range(epochs):
            for images, labels in train_loader:
                images, labels = images.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
        return self.model
