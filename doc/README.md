 - Install Metashape as an External Module
Download the last version of the module from <https://www.agisoft.com/downloads/installer/>, create a virtual environment with python 3.8 (e.g., with Anaconda)
```bash
conda create -n metashape python=3.8.11
python3 -m pip install Metashape-xxx.whl
pip install numpy easydict
```


 - Install external modules in Metashape

```bash
./metashape-pro/python/bin/python3.8 -m pip install $python_module_name
```

<https://agisoft.freshdesk.com/support/solutions/articles/31000136860-how-to-install-external-python-module-to-metashape-professional-package>

```bash
wget https://mirrors.kernel.org/ubuntu/pool/main/libf/libffi/libffi6_3.2.1-8_amd64.deb
sudo apt install libffi6_3.2.1-8_amd64.deb
```


```bash
wget https://mirrors.kernel.org/ubuntu/pool/main/libf/libffi/libffi6_3.2.1-8_amd64.deb
sudo apt install libffi6_3.2.1-8_amd64.deb
```
