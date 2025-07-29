import torch
import torch.nn as nn
import torch.nn.functional as F


class CenterDetector(nn.Module):

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv3d(1, 16, kernel_size=3, padding=1, padding_mode='replicate')
        self.conv11 = nn.Conv3d(in_channels=16, out_channels=32, kernel_size=3, padding=1, padding_mode='replicate')
        self.ds1 = nn.MaxPool3d(3)

        self.conv2 = nn.Conv3d(in_channels=32, out_channels=64, kernel_size=3, padding=1, padding_mode='replicate')
        self.conv21 = nn.Conv3d(in_channels=64, out_channels=128, kernel_size=3, padding=1, padding_mode='replicate')
        self.ds2 = nn.MaxPool3d(3)

        self.conv31 = nn.Conv3d(in_channels=128, out_channels=1, kernel_size=1)

        self.l1 = nn.Linear(in_features=3483, out_features=512)
        self.l2 = nn.Linear(in_features=512, out_features=30)
        self.l3 = nn.Linear(in_features=30, out_features=3)

    def forward(self, X, eval=True):
        y = nn.ReLU(inplace=True)(self.conv1(X))
        y = nn.ReLU(inplace=True)(self.conv11(y))
        if eval:
            y = nn.Dropout(p=0.3)(y)
        y = self.ds1(y)

        # print(y.shape)
        y = nn.ReLU(inplace=True)(self.conv2(y))
        y = nn.ReLU(inplace=True)(self.conv21(y))
        if eval:
            y = nn.Dropout(p=0.2)(y)
        y = self.ds2(y)
        y1 = nn.Flatten()(y)

        y = nn.ReLU(inplace=True)(self.conv31(y))
        if eval:
            y = nn.Dropout(p=0.1)(y)
        y = nn.Flatten()(y)
        y = torch.cat((y, y1), 1)
        # dec level
        y = nn.ReLU(inplace=True)(self.l1(y))
        y = nn.ReLU()(self.l2(y))
        y = nn.Sigmoid()(self.l3(y))
        return y


class CenterAndPCANet(nn.Module):
    def __init__(self, number_of_components):
        """
        input is a number of pca components we predicting
        """
        super(CenterAndPCANet, self).__init__()
        self.conv1 = nn.Conv3d(in_channels=1, out_channels=32, kernel_size=3, padding=1, padding_mode='replicate')
        self.conv2 = nn.Conv3d(in_channels=32, out_channels=64, kernel_size=3, padding=1, padding_mode='replicate')

        self.conv3 = nn.Conv3d(in_channels=64, out_channels=128, kernel_size=3, padding=1, padding_mode='replicate')
        self.fl = nn.Flatten()
        self.fc1 = nn.Linear(128 * 8 * 8 * 8, 512)
        self.fc2 = nn.Linear(512, number_of_components + 3)  # output layer for center and PCA components

    def forward(self, x, train=True):
        # print(x.shape)
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        if train:
            x = nn.Dropout(p=0.3)(x)
        # x = torch.dropout(x,p=0.3)
        x = torch.max_pool3d(x, 2, padding=0)

        x = torch.relu(self.conv3(x))
        # print(x.shape)
        x = self.fl(x)
        # print(x.shape)
        x = torch.relu(self.fc1(x))
        x = torch.sigmoid(self.fc2(x))
        # print(x)
        return x


class TransformerShiftPredictor(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_heads, num_layers, mesh_dim: int):
        super(TransformerShiftPredictor, self).__init__()
        self.embedding = nn.Linear(input_dim, hidden_dim)
        # self.transformer = nn.GRU(input_dim, hidden_dim, batch_first=True) # GRU
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(hidden_dim, num_heads, batch_first=True),
            num_layers
        )

        self.mesh_embedding_dim = nn.Linear(mesh_dim, 64)
        self.mesh_embedding_dim2 = nn.Linear(64, 64)

        self.out_transformer = nn.Linear(hidden_dim, hidden_dim)
        self.fc1 = nn.Linear(hidden_dim + 64, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 3)

    def forward(self, signals, mesh_pcas):
        x = signals
        # _, h_n = self.transformer(x) # GRU
        # out = self.out_transformer(h_n) # GRU
        x = torch.tanh(self.embedding(x))
        vals = self.transformer(x)
        out = self.out_transformer(torch.relu(vals))
        out = torch.mean(vals, axis=0)

        # print(vals.shape,out.shape)
        out = out.unsqueeze(0)
        embedded_mesh = F.relu(self.mesh_embedding_dim(mesh_pcas))
        embedded_mesh = F.relu(self.mesh_embedding_dim2(embedded_mesh))

        fused_features = torch.cat((out, embedded_mesh), dim=1)

        x = torch.relu(self.fc1(fused_features))
        x = torch.sigmoid(self.fc2(x))

        return x

class TransformerClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_heads, num_layers):
        super(TransformerClassifier, self).__init__()
        self.embedding = nn.Linear(input_dim, hidden_dim)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(hidden_dim, num_heads),
            num_layers
        )
        self.fc = nn.Linear(hidden_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        x = self.embedding(x)
        #x = x.permute(1, 0, 2)  # Convert to (seq_len, batch_size, input_dim)
        mask = torch.ones(x.shape[0], x.shape[0]).to(x.device)  # Create a square mask
        out = self.transformer(x, mask)
        #print(out)
        out = self.fc(out)
        out = self.fc2(out)
        return torch.sigmoid(out)

