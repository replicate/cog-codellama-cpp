export FAKE_COG_VERSION = 0.8.1

.PHONY: all
all: base python instruct

.PHONY: base
base: codellama-7b codellama-13b codellama-34b

.PHONY: python
python: codellama-7b-python codellama-13b-python codellama-34b-python

.PHONY: instruct
instruct: instruct-schema.json codellama-7b-instruct codellama-13b-instruct codellama-34b-instruct

base-schema.json:
	echo "codellama-7b.Q5_K_M.gguf" > model.txt
	cog run python3 -m cog.command.openapi_schema > base-schema.json
instruct-schema.json:
	echo "codellama-7b-instruct.Q5_K_M.gguf" > model.txt
	cog run python3 -m cog.command.openapi_schema > instruct-schema.json

.PHONY: codellama-7b
codellama-7b: base-schema.json
	echo "codellama-7b.Q5_K_M.gguf" > model.txt
	cog push --openapi-schema=base-schema.json --progress=plain r8.im/replicate-internal/codellama-7b

.PHONY: codellama-13b
codellama-13b: base-schema.json
	echo "codellama-13b.Q5_K_M.gguf" > model.txt
	cog push --openapi-schema=base-schema.json --progress=plain r8.im/replicate-internal/codellama-13b

.PHONY: codellama-34b
codellama-34b: base-schema.json
	echo "codellama-34b.Q5_K_M.gguf" > model.txt
	cog push --openapi-schema=base-schema.json --progress=plain r8.im/replicate-internal/codellama-34b


.PHONY: codellama-7b-python
codellama-7b-python: base-schema.json
	echo "codellama-7b-python.Q5_K_M.gguf" > model.txt
	cog push --openapi-schema=base-schema.json --progress=plain r8.im/replicate-internal/codellama-7b-python

.PHONY: codellama-13b-python
codellama-13b-python: base-schema.json
	echo "codellama-13b-python.Q5_K_M.gguf" > model.txt
	cog push --openapi-schema=base-schema.json --progress=plain r8.im/replicate-internal/codellama-13b-python

.PHONY: codellama-34b-python
codellama-34b-python: base-schema.json
	echo "codellama-34b-python.Q5_K_M.gguf" > model.txt
	cog push --openapi-schema=base-schema.json --progress=plain r8.im/replicate-internal/codellama-34b-python

	
.PHONY: codellama-7b-instruct
codellama-7b-instruct: instruct-schema.json
	echo "codellama-7b-instruct.Q5_K_M.gguf" > model.txt
	cog push --openapi-schema=instruct-schema.json --progress=plain r8.im/replicate-internal/codellama-7b-instruct

.PHONY: codellama-13b-instruct
codellama-13b-instruct: instruct-schema.json
	echo "codellama-13b-instruct.Q5_K_M.gguf" > model.txt
	cog push --openapi-schema=instruct-schema.json --progress=plain r8.im/replicate-internal/codellama-13b-instruct

.PHONY: codellama-34b-instruct
codellama-34b-instruct: instruct-schema.json
	echo "codellama-34b-instruct.Q5_K_S.gguf" > model.txt
	cog push --openapi-schema=instruct-schema.json --progress=plain r8.im/replicate-internal/codellama-34b-instruct
