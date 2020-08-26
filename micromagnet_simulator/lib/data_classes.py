from dataclasses import dataclass
import numpy as np

@dataclass
class micromagnet_spec:
	x_pos : float
	y_pos : np.ndarray
	z_pos : np.ndarray
	magnetx : float
	magnety : float
	magnetz : float
	Dx : float
	Dy : float
	Dz : float 
	Br : float

	def __iter__(self):
		self.iterator_items = ["Br", "x_pos", "y_pos", "z_pos", "Dx", "Dy", "Dz", "magnetx", "magnety", "magnetz"]
		self.idx = 0
		return self

	def __next__(self):
		if self.idx < len(self.iterator_items):
			item = getattr(self, self.iterator_items[self.idx])
			self.idx += 1
			return item
		else:
			raise StopIteration