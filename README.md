# Metashape scripts

Sandbox for metashape scripts.

## Use Metashape as external module

### Create Environment with anaconda

Download the [current .whl file](https://www.agisoft.com/downloads/installer/) and install it following [these instructions](https://agisoft.freshdesk.com/support/solutions/articles/31000148930-how-to-install-metashape-stand-alone-python-module) (using the name of the .whl file that you downloaded).

```bash
conda create -n metashape python=3.10
conda activate metashape
pip3 install Metashape-"XX".whl
pip3 install -r requirements.txt
```

### License

Metashape license: You need a license (and associated license file) for Metashape. The easiest way to get the license file, is by installing the Metashape Professional Edition GUI software (distinct from the Python module) and registering it following the prompts in the software (you need to purchase a license first). Once you have a license file (whether a node-locked or floating license), you need to set the agisoft_LICENSE environment variable (search onilne for instructions for your OS; look for how to permanently set it) to the path to the folder containing the license file (metashape.lic).

With Linux (Ubuntu 22.04), to permanently setup agisoft_LICENSE environment variable for floating license, modify your .bashrc file:

```bash
sudo nano ~/.bashrc
```

add the line (replace port and address with your values)

```bash
export agisoft_LICENSE="port"@"address"
```

```bash
source ~/.bashrc
```

Check if the new environmental variable is present:

```bash
printenv | grep agisoft
```

### Install external modules in Metashape built-in pyhton environment

Follow the official guide [https://agisoft.freshdesk.com/support/solutions/articles/31000136860-how-to-install-external-python-module-to-metashape-professional-package](https://agisoft.freshdesk.com/support/solutions/articles/31000136860-how-to-install-external-python-module-to-metashape-professional-package)

For Linux:

```bash
./metashape-pro/python/bin/python3.8 -m pip install "python_module_name"
```

### Issues

##### Reach Python Consol

In Metashape app, if Reach Python Console does not work and gives the following error

```bash
Failed to import qtconsole.inprocess: libffi.so.6: cannot open shared object file: No such file or directory
Construction of rich console failed - using simple console
```

You need to manually install libffi6 with

```bash
wget https://mirrors.kernel.org/ubuntu/pool/main/libf/libffi/libffi6_3.2.1-8_amd64.deb
sudo apt install ./libffi6_3.2.1-8_amd64.deb
```
