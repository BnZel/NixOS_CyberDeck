with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell rec {
  name = "impurePythonEnv";
  venvDir = "./.venv";
  buildInputs = [
    # A Python interpreter including the 'venv' module is required to bootstrap
    # the environment.
    pythonPackages.python

    # This execute some shell code to initialize a venv in $venvDir before
    # dropping into the shell
    pythonPackages.venvShellHook

    # Those are dependencies that we would like to use from nixpkgs, which will
    # add them to PYTHONPATH and thus make them accessible from within the venv.
    pythonPackages.numpy
    pythonPackages.requests
    pythonPackages.pyftdi
  
    # In this particular example, in order to compile any binary extensions they may
    # require, the Python modules listed in the hypothetical requirements.txt need
    # the following packages to be installed locally:
    libusb1
   ];

  # Run this command, only after creating the virtual environment
#  postVenvCreation = ''
#    unset SOURCE_DATE_EPOCH
#    pip install -r requirements.txt
#  '';

 packages = [ pkgs.screen pkgs.gcc pkgs.gnumake pkgs.pkg-config pkgs.openssl ];

# For linking OpenCV libraries
 LD_LIBRARY_PATH = lib.makeLibraryPath [ pkgs.stdenv.cc.cc ];

 shellHook = ''
   alias c="clear"
   alias h="history -c"
   alias la="ls -la"
   
   source .venv/bin/activate
   which python3
   python3 sanity_test.py
  # python3 blink_test.py
   ls /dev/ttyUSB*
   ls /dev/video*
 '';


  # Now we can execute any commands within the virtual environment.
  # This is optional and can be left out to run pip manually.
  postShellHook = ''
    # allow pip to install wheels
    unset SOURCE_DATE_EPOCH
    BLINKA_FT232H=1
  '';

}
