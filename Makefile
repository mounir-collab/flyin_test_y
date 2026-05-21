MAPS_URL = https://cdn.intra.42.fr/document/document/48308/maps.tar.gz
mypy_Flags = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
Path= maps/easy/01_linear_path.txt 

run:
	@python3 Fly-in.py $(Path)

install: 
	@wget https://cdn.intra.42.fr/document/document/48308/maps.tar.gz
	@tar -xpf maps.tar.gz
	@pip install pdbpp
	@pip install  mypy

debug: 
	@python3 -m pdb  Fly-in.py maps/easy/01_linear_path.txt

clean: 
	@rm -rf __pycache__ */*__pycache__  .mypy_cache maps.tar.gz maps *maps* */*/__pycache__

lint: 
	@flake8  &&  mypy . $(mypy_Flags)
