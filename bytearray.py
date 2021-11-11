import struct
from binascii import hexlify, unhexlify


class Bytearray:
    
	def __init__(self, data=b''):
		self.offset = 0
		self.data = data

	def hexData(self):
		return hexlify(self.data)

	def hexdump(self):
		result = [hexlify(self.data[index:index+4]).decode()
				  for index in range(0, len(self.data), 4)]
		return ' '.join(result)
		
	def writeUTF(self, data: str):
		assert type(data) == str
		encoded = self.utf8s_to_utf8m(data.encode('utf-8'))
		self.writeShort(len(encoded))
		self.data += encoded
		return self

	def writeBool(self, data: bool):
		assert type(data) == bool
		self.writeByte(data)
		return self

	def writeByte(self, data):
		# if type(data) == int
		self.data += struct.pack('>B', data)
		# else:
		# 	self.data += data
		return self

	def writeShort(self, data: int):
		assert type(data) == int
		self.data += struct.pack('>H', data)
		return self

	def writeInt(self, data: int):
		assert type(data) == int
		self.data += struct.pack('>i', data)
		return self
	
	def writeFloat(self, data):
		assert type(data) == float or type(data) == int
		self.data += struct.pack('!f', data)
		return self

	def writeLong(self, data: int):
		assert type(data) == int
		self.data += struct.pack('>q', data)
		return self
	
	def writeHex(self, data: str):
		assert type(data) == str
		self.data += unhexlify(data)
		return self

	def writeRaw(self, data):
		self.data += data
		return self

	def readUTF(self):
		length = self.readShort()
		if length > 0:
			val = self.utf8m_to_utf8s(self.data[self.offset:self.offset+length]).decode('utf-8', errors='ignore')
		else:
			val = ''
		self.offset += length
		return val

	def readBool(self):
		return self.readByte() != 0

	def readByte(self):
		val = self.data[self.offset]
		self.offset += 1
		return val

	def readShort(self):
		val = struct.unpack('>H', self.data[self.offset:self.offset+2])[0]
		self.offset += 2
		return val

	def readInt(self):
		val = struct.unpack('>i', self.data[self.offset:self.offset+4])[0]
		self.offset += 4
		return val

	def readFloat(self):
		val = struct.unpack('!f', self.data[self.offset:self.offset+4])[0]
		self.offset += 4
		return val

	def readLong(self):
		val = struct.unpack('>q', self.data[self.offset:self.offset+8])[0]
		self.offset += 8
		return val

	def readFully(self, length):
		val = self.data[self.offset:self.offset+length]
		self.offset += length
		return val

	def a(self, *args):
		if len(args) == 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
			return ((self.readByte() & 255) * (args[1] - args[0]) / 255.0) + args[0]
		elif len(args) == 0:
			return (((self.readByte() & 255) << 16) + ((self.readByte() & 255) << 8)) + (self.readByte() & 255)
		else:
			raise TypeError('Unknown argument count/type: {}'.format(args))

	def b(self, a: float, b: float):
		return ((self.readShort() & 65535) * (b - a) / 65535.0) + a

	def c(self, a: float, b: float):
		return (((((((self.readByte() & 255)
		<< 16) + ((self.readByte() & 255) << 8)) + (self.readByte() & 255))) * (b - a)) / 1.6777215E7) + a
  
    # https://gist.github.com/BarelyAliveMau5/000e7e453b6d4ebd0cb06f39bc2e7aec
	def utf8s_to_utf8m(self, string):
		new_str = []
		i = 0
		while i < len(string):
			byte1 = string[i]
			if (byte1 & 0x80) == 0:
				if byte1 == 0:
					new_str.append(0xC0)
					new_str.append(0x80)
				else:
					new_str.append(byte1)
			elif (byte1 & 0xE0) == 0xC0:
				new_str.append(byte1)
				i += 1
				new_str.append(string[i])
			elif (byte1 & 0xF0) == 0xE0:
				new_str.append(byte1)
				i += 1
				new_str.append(string[i])
				i += 1
				new_str.append(string[i])
			elif (byte1 & 0xF8) == 0xF0:
				i += 1
				byte2 = string[i]
				i += 1
				byte3 = string[i]
				i += 1
				byte4 = string[i]
				u21 = (byte1 & 0x07) << 18
				u21 += (byte2 & 0x3F) << 12
				u21 += (byte3 & 0x3F) << 6
				u21 += (byte4 & 0x3F)
				new_str.append(0xED)
				new_str.append((0xA0 + (((u21 >> 16) - 1) & 0x0F)))
				new_str.append((0x80 + ((u21 >> 10) & 0x3F)))
				new_str.append(0xED)
				new_str.append((0xB0 + ((u21 >> 6) & 0x0F)))
				new_str.append(byte4)
			i += 1
		return bytes(new_str)

	def utf8m_to_utf8s(self, string):
		new_string = []
		length = len(string)
		i = 0
		while i < length:
			byte1 = string[i]
			if (byte1 & 0x80) == 0:
				new_string.append(byte1)
			elif (byte1 & 0xE0) == 0xC0:
				i += 1
				byte2 = string[i]
				if byte1 != 0xC0 or byte2 != 0x80:
					new_string.append(byte1)
					new_string.append(byte2)
				else:
					new_string.append(0)
			elif (byte1 & 0xF0) == 0xE0:
				i += 1
				byte2 = string[i]
				i += 1
				byte3 = string[i]
				if i+3 < length and byte1 == 0xED and (byte2 & 0xF0) == 0xA0:
					byte4 = string[i+1]
					byte5 = string[i+2]
					byte6 = string[i+3]
					if byte4 == 0xED and (byte5 & 0xF0) == 0xB0:
						i += 3
						u21 = ((byte2 & 0x0F) + 1) << 16
						u21 += (byte3 & 0x3F) << 10
						u21 += (byte5 & 0x0F) << 6
						u21 += (byte6 & 0x3F)
						new_string.append(0xF0 + ((u21 >> 18) & 0x07))
						new_string.append(0x80 + ((u21 >> 12) & 0x3F))
						new_string.append(0x80 + ((u21 >> 6) & 0x3F))
						new_string.append(0x80 + (u21 & 0x3F))
						continue 
				new_string.append(byte1)
				new_string.append(byte2)
				new_string.append(byte3)
			i += 1
		return bytes(new_string)