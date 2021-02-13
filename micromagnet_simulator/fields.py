import numpy as np

class field_generic():
	def __init__(self):
		self.unit = 'T'
		self._field = None
		self._d_field = None

	@property
	def unit_conv(self):
		if self.unit == 'T':
			return 1
		elif self.unit == 'mT':
			return 1e3
		elif self.unit == 'GHz':
			return 28.5714
		elif self.unit == 'MHz':
			return 28.5714*1e3
		else:
			raise ValueError('Invalid unit supplied.')
		
	@property
	def Bx(self):
		idx = [0]*self.ndim + [0]
		for i in self.active_idx:
			idx[i] = slice(None)
		return self.field[tuple(idx)]*self.unit_conv

	@property
	def By(self):
		idx = [0]*self.ndim + [1]
		for i in self.active_idx:
			idx[i] = slice(None)
		return self.field[tuple(idx)]*self.unit_conv

	@property
	def Bz(self):
		idx = [0]*self.ndim + [2]
		for i in self.active_idx:
			idx[i] = slice(None)
		return self.field[tuple(idx)]*self.unit_conv

	@property
	def Btot(self):
		idx = [0]*self.ndim
		for i in self.active_idx:
			idx[i] = slice(None)
		return np.linalg.norm(self.field,axis=3)[tuple(idx)]*self.unit_conv

	def B(self, direction):
		if len(direction) == 1:
			return getattr(self, 'B{}'.format(direction))
		else:
			B = np.zeros(self.Bx.shape)

			for i in range(len(direction)):
				B += getattr(self, 'B{}'.format(list(direction)[i]))**2

			return np.sqrt(B)

	def dB(self, field_direction, movement_direction):
		field_direction = list(field_direction)
		movement_direction = list(movement_direction)

		if len(field_direction) == 1 and len(movement_direction) == 1:
			idx = [list('xyz').index(movement_direction[0])]+self.ndim*[0]+[list('xyz').index(field_direction[0])]
			for i in self.active_idx:
				idx[i+1] = slice(None)

			return self.d_field[tuple(idx)]*self.unit_conv
		else:
			field = 0 
			for i in list(movement_direction):
				for j in list(field_direction):
					idx = [list('xyz').index(i),0,0,0,list('xyz').index(j)]
					for k in self.active_idx:
						idx[k+1] = slice(None)

					field += self.d_field[tuple(idx)]**2
					
			return np.sqrt(field)*self.unit_conv

	@property
	def ndim(self):
		return 3

	@property
	def active_idx(self):
		return np.where(np.array(self.field[:,:,:,0].shape)>1)[0]

class field(field_generic):
	def __init__(self, collection, views, unit='T'):
		super().__init__()
		self.coll = collection.coll
		self.views = views

		pos = np.zeros([self.x.size, self.y.size, self.z.size,3])

		for i in range(self.x.size):
			for j in range(self.y.size):
				for k in range(self.z.size):
					pos[i,j,k] = [self.x[i], self.y[j], self.z[k]]

		self.positions = pos*1e-6
		self.unit = unit

	@property
	def field(self):
		if self._field is None:
			self._field = 1e-3*self.coll.getB(self.positions.reshape([int(self.positions.size/3),3])).reshape(self.positions.shape)
		return self._field

	@property
	def d_field(self):
		'''
		unit : T/nm
		Bx/x By/x Bz/x
		Bx/y By/y Bz/y
		Bx/z By/z Bz/z
		'''
		if self._d_field is None:
			h =0.5 #nm
			self._d_field = np.empty([3]+list(self.field.shape))

			for i in range(3):
				movement_operator = [0,0,0]
				movement_operator[i] = -h*1e-6
				self.coll.move(movement_operator)
				
				field_off = 1e-3*self.coll.getB(self.positions.reshape([int(self.positions.size/3),3])).reshape(self.positions.shape)
				
				movement_operator[i] = h*1e-6
				self.coll.move(movement_operator)
				
				self._d_field[i] = (field_off - self.field)/h

		return self._d_field

	@property
	def x(self):
		return np.linspace(self.views[0][0], self.views[0][1], self.views[0][2])

	@property
	def y(self):
		return np.linspace(self.views[1][0], self.views[1][1], self.views[1][2])

	@property
	def z(self):
		return np.linspace(self.views[2][0], self.views[2][1], self.views[2][2])

	@property
	def shape(self):
		return tuple(np.array(self.field.shape)[self.active_idx])

	@property
	def dim(self):
		return len(self.shape)

class field_qubits(field_generic):
	def __init__(self, MM_properties, setpoints):
		super().__init__()
		self.setpoints = setpoints
		self.MM_properties = MM_properties
		self._field = None
		self._d_field = None

	@property
	def field(self):
		if self._field is None:
			self._field = np.zeros([self.size, len(self.MM_properties.flat[0].dot_positions), 3])
			for i in range(self.MM_properties.size):
				 self._field[i]= 1e-3*self.MM_properties.flat[i].magnet_collection.coll.getB(
				 	self.MM_properties.flat[i].magnet_collection.qubit_positions)

			shape = (*self.shape, len(self.MM_properties.flat[0].dot_positions), 3)

			self._field = self._field.reshape(shape)

		return self._field

	@property
	def d_field(self):
		'''
		unit : T/nm
		Bx/x By/x Bz/x
		Bx/y By/y Bz/y
		Bx/z By/z Bz/z
		'''
		if self._d_field is None:
			h =0.5 #nm
			self._d_field = np.empty([3]+list(self.field.shape))

			for i in range(3):
				movement_operator = [0,0,0]
				movement_operator[i] = -h*1e-6
				self.MM_properties.move(movement_operator)
				
				field_off = np.zeros([self.size, len(self.MM_properties.flat[0].dot_positions), 3])
				for MM in range(self.MM_properties.size):
					 field_off[MM]= 1e-3*self.MM_properties.flat[MM].magnet_collection.coll.getB(
					 	self.MM_properties.flat[MM].magnet_collection.qubit_positions)
				
				shape = (*self.shape, len(self.MM_properties.flat[0].dot_positions), 3)
				field_off = field_off.reshape(shape)

				movement_operator[i] = h*1e-6
				self.MM_properties.move(movement_operator)
				
				self._d_field[i] = (field_off - self.field)/h

		return self._d_field

	@property
	def shape(self):
		return self.setpoints.shape

	@property
	def ndim(self):
		return len(self.shape) + 1
	
	@property
	def size(self):
		size = 1
		for i in self.shape:
			size*=i

		return size

	@property
	def active_idx(self):
		return np.arange(self.ndim, dtype=np.int)
