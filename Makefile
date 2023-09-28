.PHONY: all
all: base python instruct

.PHONY: base
base: codellama-7b codellama-13b codellama-34b

.PHONY: python
python: codellama-7b-python codellama-13b-python codellama-34b-python

.PHONY: instruct
instruct: codellama-7b-instruct codellama-13b-instruct codellama-34b-instruct


.PHONY: codellama-7b
codellama-7b:
	echo "codellama-7b.Q5_K_M.gguf" > model.txt
	cog push r8.im/replicate-internal/codellama-7b

.PHONY: codellama-13b
codellama-13b:
	echo "codellama-13b.Q5_K_M.gguf" > model.txt
	cog push r8.im/replicate-internal/codellama-13b

.PHONY: codellama-34b
codellama-34b:
	echo "codellama-34b.Q5_K_M.gguf" > model.txt
	cog push r8.im/replicate-internal/codellama-34b


.PHONY: codellama-7b-instruct
codellama-7b-instruct:
	echo "codellama-7b-instruct.Q5_K_M.gguf" > model.txt
	cog push r8.im/replicate-internal/codellama-7b-instruct

.PHONY: codellama-13b-instruct
codellama-13b-instruct:
	echo "codellama-13b-instruct.Q5_K_M.gguf" > model.txt
	cog push r8.im/replicate-internal/codellama-13b-instruct

.PHONY: codellama-34b-instruct
codellama-34b-instruct:
	echo "codellama-34b-instruct.Q5_K_S.gguf" > model.txt
	cog push r8.im/replicate-internal/codellama-34b-instruct


.PHONY: codellama-7b-python
codellama-7b-python:
	echo "codellama-7b-python.Q5_K_M.gguf" > model.txt
	cog push r8.im/replicate-internal/codellama-7b-python

.PHONY: codellama-13b-python
codellama-13b-python:
	echo "codellama-13b-python.Q5_K_M.gguf" > model.txt
	cog push r8.im/replicate-internal/codellama-13b-python

.PHONY: codellama-34b-python
codellama-34b-python:
	echo "codellama-34b-python.Q5_K_M.gguf" > model.txt
	cog push r8.im/replicate-internal/codellama-34b-python
