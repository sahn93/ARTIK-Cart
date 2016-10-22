## Dependencies

```
echo "enable_uart=1" | sudo tee -a /boot/config.txt
echo "dtoverlay=pi3-disable-bt" | sudo tee -a /boot/config.txt
sudo reboot
sudo apt-get install python-dev
pip install -r requirements.txt
git submodule init
git submodule update
cd RTIMULib2/Linux/python
python setup.py build
sudo python setup.py install
```

## How to run

```
python main.py
```
