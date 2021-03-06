import torch
from torch import nn
from modules import Conv_2d, Conv_emb


class AudioModel(nn.Module):
	def __init__(self):
		super(AudioModel, self).__init__()

		# CNN module for spectrograms
		self.spec_bn = nn.BatchNorm2d(1)
		self.layer1 = Conv_2d(1, 128, pooling=2)
		self.layer2 = Conv_2d(128, 128, pooling=2)
		self.layer3 = Conv_2d(128, 256, pooling=2)
		self.layer4 = Conv_2d(256, 256, pooling=2)
		self.layer5 = Conv_2d(256, 256, pooling=2)
		self.layer6 = Conv_2d(256, 256, pooling=2)
		self.layer7 = Conv_2d(256, 512, pooling=2)
		self.layer8 = Conv_emb(512, 256)

		# FC module for word embedding
		self.fc1 = nn.Linear(300, 512)
		self.bn1 = nn.BatchNorm1d(512)
		self.fc2 = nn.Linear(512, 256)

		self.relu = nn.ReLU()
		self.dropout = nn.Dropout(0.5)

	def spec_to_embedding(self, spec):
		out = spec.unsqueeze(1)
		out = self.spec_bn(out)

		# CNN
		out = self.layer1(out)
		out = self.layer2(out)
		out = self.layer3(out)
		out = self.layer4(out)
		out = self.layer5(out)
		out = self.layer6(out)
		out = self.layer7(out)
		out = self.layer8(out)
		out = out.squeeze(2)
		out = nn.MaxPool1d(out.size(-1))(out)
		out = out.view(out.size(0), -1)
		return out

	def word_to_embedding(self, emb):
		out = self.fc1(emb)
		out = self.bn1(out)
		out = self.relu(out)
		out = self.dropout(out)
		out = self.fc2(out)
		return out

	def forward(self, tag, spec, cf):
		tag_emb = self.word_to_embedding(tag)
		song_emb = self.spec_to_embedding(spec)
		return tag_emb, song_emb


class CFModel(nn.Module):
	def __init__(self):
		super(CFModel, self).__init__()

		# FC module for collaborative filtering embedding
		self.cf_fc1 = nn.Linear(200, 512)
		self.cf_bn1 = nn.BatchNorm1d(512)
		self.cf_fc2 = nn.Linear(512, 256)

		# FC module for word embedding
		self.fc1 = nn.Linear(300, 512)
		self.bn1 = nn.BatchNorm1d(512)
		self.fc2 = nn.Linear(512, 256)

		self.relu = nn.ReLU()
		self.dropout = nn.Dropout(0.5)

	def cf_to_embedding(self, cf):
		out = self.cf_fc1(cf)
		out = self.cf_bn1(out)
		out = self.relu(out)
		out = self.dropout(out)
		out = self.cf_fc2(out)
		return out

	def word_to_embedding(self, emb):
		out = self.fc1(emb)
		out = self.bn1(out)
		out = self.relu(out)
		out = self.dropout(out)
		out = self.fc2(out)
		return out

	def forward(self, tag, spec, cf):
		tag_emb = self.word_to_embedding(tag)
		song_emb = self.cf_to_embedding(cf)
		return tag_emb, song_emb


class HybridModel(nn.Module):
	def __init__(self):
		super(HybridModel, self).__init__()

		# CNN module for spectrograms
		self.spec_bn = nn.BatchNorm2d(1)
		self.layer1 = Conv_2d(1, 128, pooling=2)
		self.layer2 = Conv_2d(128, 128, pooling=2)
		self.layer3 = Conv_2d(128, 256, pooling=2)
		self.layer4 = Conv_2d(256, 256, pooling=2)
		self.layer5 = Conv_2d(256, 256, pooling=2)
		self.layer6 = Conv_2d(256, 256, pooling=2)
		self.layer7 = Conv_2d(256, 512, pooling=2)
		self.layer8 = Conv_emb(512, 200)

		# FC module for collaborative filtering embedding
#		self.cf_fc1 = nn.Linear(200, 512)
#		self.cf_bn1 = nn.BatchNorm1d(512)
#		self.cf_fc2 = nn.Linear(512, 256)

		# FC module for concatenated embedding
		self.cat_fc1 = nn.Linear(400, 512)
		self.cat_bn1 = nn.BatchNorm1d(512)
		self.cat_fc2 = nn.Linear(512, 256)

		# FC module for word embedding
		self.fc1 = nn.Linear(300, 512)
		self.bn1 = nn.BatchNorm1d(512)
		self.fc2 = nn.Linear(512, 256)

		self.relu = nn.ReLU()
		self.dropout = nn.Dropout(0.5)

	def spec_to_embedding(self, spec):
		out = spec.unsqueeze(1)
		out = self.spec_bn(out)

		# CNN
		out = self.layer1(out)
		out = self.layer2(out)
		out = self.layer3(out)
		out = self.layer4(out)
		out = self.layer5(out)
		out = self.layer6(out)
		out = self.layer7(out)
		out = self.layer8(out)
		out = out.squeeze(2)
		out = nn.MaxPool1d(out.size(-1))(out)
		out = out.view(out.size(0), -1)
		return out

	def cf_to_embedding(self, cf):
		out = self.cf_fc1(cf)
		out = self.cf_bn1(out)
		out = self.relu(out)
		out = self.dropout(out)
		out = self.cf_fc2(out)
		return out

	def cat_to_embedding(self, cat):
		out = self.cat_fc1(cat)
		out = self.cat_bn1(out)
		out = self.relu(out)
		out = self.dropout(out)
		out = self.cat_fc2(out)
		return out

	def song_to_embedding(self, spec, cf):
		# spec to embedding
		out_spec = self.spec_to_embedding(spec)

		# cf to embedding
#		out_cf = self.cf_to_embedding(cf)

		# concatenate
		out = torch.cat([out_spec, cf], dim=-1)

		# fully connected
		out = self.cat_to_embedding(out)
		return out

	def word_to_embedding(self, emb):
		out = self.fc1(emb)
		out = self.bn1(out)
		out = self.relu(out)
		out = self.dropout(out)
		out = self.fc2(out)
		return out

	def forward(self, tag, spec, cf):
		tag_emb = self.word_to_embedding(tag)
		song_emb = self.song_to_embedding(spec, cf)
		return tag_emb, song_emb


