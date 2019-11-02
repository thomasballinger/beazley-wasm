
# David Beazley's Web Assembly Virtual Machine

This repo follows the talk David Beazley gave at PyCon India in 2019.

https://www.youtube.com/watch?v=r-A78RgMhZU

Commits have timestamps so you can try to follow along, or just read the finished thing at the latest commit. I really do recommend watching the talk!

I've included the compiled program.wasm file from https://github.com/aochagavia/rocket_wasm so you don't need to install rust to follow along.

To run this code, you'll need numpy and pygame. Homebrew-installed Python 3.7 and 3.8 seem not to work with Pygame on Mojave - I recommend installing Python 3.6 from the official Python site and using that executable installing pygame, like `python3.6 -m pip install numpy pygame`. The pygame installation is optional however - it's just something to hook up the inputs and outputs to. The meat of this project is the virtual machine!
