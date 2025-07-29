import os

class Files:
	@staticmethod
	def get_file_size(file_path: str) -> int:
		return os.path.getsize(file_path)

	@staticmethod
	def exists(file_path: str) -> bool:
		return os.path.exists(file_path)

	@classmethod
	def create(cls, file_path: str | list[str]) -> bool:
		if isinstance(file_path, list):
			for path in file_path:
				cls.create(path)
			return

		if '.' not in file_path:
			if not cls.exists(file_path):
				os.makedirs(file_path)
			return
		paths = file_path.split('/')
		if len(paths) > 1:
			for i in range(len(paths) - 1):
				path = '/'.join(paths[: i + 1])
				if not cls.exists(path):
					os.makedirs(path)
					return True
		if not cls.exists(file_path):
			with open(file_path, 'w') as file:
				file.write('')
				return True
		return False

	@staticmethod
	def read(file_path: str) -> str:
		with open(file_path, 'r+') as file:
			return file.read()

	@staticmethod
	def write(file_path: str, content: str) -> bool:
		with open(file_path, 'w') as file:
			file.write(content)
			return True
		return False

	@staticmethod
	def append(file_path: str, content: str) -> bool:
		with open(file_path, 'a') as file:
			file.write(content)
			return True
		return False

	@staticmethod
	def delete(file_path: str) -> bool:
		if os.path.exists(file_path):
			os.remove(file_path)
			return True
		return False