# Metashape scripts

Sandbox for metashape scripts.

# Use Metashape as external module

## Create Environment with anaconda

Download the [current .whl file](https://www.agisoft.com/downloads/installer/) and install it following [these instructions](https://agisoft.freshdesk.com/support/solutions/articles/31000148930-how-to-install-metashape-stand-alone-python-module) (using the name of the .whl file that you downloaded).

```bash
conda create -n metashape python=3.10
conda activate metashape
pip3 install Metashape-$XX.whl
pip3 install -r requirements.txt
```

## License

Metashape license: You need a license (and associated license file) for Metashape. The easiest way to get the license file (assuming you own a license) is by installing the Metashape Professional Edition GUI software (distinct from the Python module) and registering it following the prompts in the software (note you need to purchase a license first). Once you have a license file (whether a node-locked or floating license), you need to set the agisoft_LICENSE environment variable (search onilne for instructions for your OS; look for how to permanently set it) to the path to the folder containing the license file (metashape.lic).

To permanently setup agisoft_LICENSE environment variable for floating license:

```bash
sudo nano ~/.bashrc
```

add the line

```bash
export agisoft_LICENSE="port"@"address"
```

(replace port and address with your values)

```bash
source ~/.bashrc
```

check if the new environment is present:

```bash
printenv | grep agisoft
```
