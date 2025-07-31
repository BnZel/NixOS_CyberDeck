# Edit this configuration file to define what should be installed on
# your system. Help is available in the configuration.nix(5) man page, on
# https://search.nixos.org/options and in the NixOS manual (`nixos-help`).

{ config, lib, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  # Use the systemd-boot EFI boot loader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  boot.kernelPackages = pkgs.linuxPackages_latest;

   networking.hostName = "hostname"; # Define your hostname.
  # Pick only one of the below networking options.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.
   networking.networkmanager.enable = true;  # Easiest to use and most distros use this by default.


  # Set your time zone.
   time.timeZone = "America/Toronto";

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

   nix.settings.experimental-features = [ "nix-command" "flakes"];

  # Select internationalisation properties.
  # i18n.defaultLocale = "en_US.UTF-8";
  # console = {
  #   font = "Lat2-Terminus16";
  #   keyMap = "us";
  #   useXkbConfig = true; # use xkb.options in tty.
  # };

  # Enable the X11 windowing system.
  # services.xserver.enable = true;
  # Configure keymap in X11
  # services.xserver.xkb.layout = "us";
  # services.xserver.xkb.options = "eurosign:e,caps:escape";

  # Enable CUPS to print documents.
  # services.printing.enable = true;

  # Enable sound.
  # hardware.pulseaudio.enable = true;
  # OR
  # services.pipewire = {
  #   enable = true;
  #   pulse.enable = true;
  # };

  # Enable touchpad support (enabled default in most desktopManager).
  # services.libinput.enable = true;

  services.cockpit = {
    enable = true;
    port = 9090;
    settings = {
      WebService = {
        AllowUnencrypted = true;
      };
    };
  };


  # Define a user account. Don't forget to set a password with ‘passwd’.
   users.users.username = {
     isNormalUser = true;
     password = "password";
     extraGroups = [ "networkmanager" "wheel" ]; # Enable ‘sudo’ for the user.
     shell = pkgs.zsh;
     packages = with pkgs; [];
  };
 
  environment.etc."modprobe.d/iwlwifi.conf".text = ''
    options iwlwifi 11n_disable=1
    options iwlwifi power_save=0
  '';

  # List packages installed in system profile. To search, run:
  # $ nix search wget
   environment.systemPackages = with pkgs; [
  #   vim # Do not forget to add an editor to edit configuration.nix! The Nano editor is also installed by default.
     wget
     htop
     fastfetch
     zsh
     oh-my-zsh
     git
     linux-firmware
     linux-wifi-hotspot
     tmux
     busybox
     cockpit
     libusb1
   ];
  
  # udev rules
  services.udev.extraRules = ''
  SUBSYSTEM=="usb",
  ATTR{idVendor}=="0403",
  ATTR{idProduct}=="6001",
  GROUP="plugdev", MODE="0666"
  SUBSYSTEM=="usb",
  ATTR{idVendor}=="0403",
  ATTR{idProduct}=="6011",
  GROUP="plugdev", MODE="0666"
  SUBSYSTEM=="usb",
  ATTR{idVendor}=="0403",
  ATTR{idProduct}=="6010",
  GROUP="plugdev", MODE="0666"
  SUBSYSTEM="usb",
  ATTR{idVendor}=="0403",
  ATTR{idProduct}=="6014",
  GROUP="plugdev", MODE="0666"
  SUBSYSTEM=="usb",
  ATTR{idVendor}=="0403",
  ATTR{idProduct}=="6015",
  GROUP="plugdev", MODE="0666"
  '';

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };
  programs.zsh.enable = true;  


  # List services that you want to enable:

  # Enable the OpenSSH daemon.
   services.openssh.enable = true;

   services.openssh.settings = {
	PasswordAuthentication = false;
   };


  # Open ports in the firewall.
   networking.firewall.allowedTCPPorts = [ 9090 1234 80 443];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

  # Hardcode USB tethering - Android
  # networking.interfaces.enp0s20u2u1u4.useDHCP = false;

  # Copy the NixOS configuration file and link it from the resulting system
  # (/run/current-system/configuration.nix). This is useful in case you
  # accidentally delete configuration.nix.
  # system.copySystemConfiguration = true;

  # This option defines the first version of NixOS you have installed on this particular machine,
  # and is used to maintain compatibility with application data (e.g. databases) created on older NixOS versions.
  #
  # Most users should NEVER change this value after the initial install, for any reason,
  # even if you've upgraded your system to a new NixOS release.
  #
  # This value does NOT affect the Nixpkgs version your packages and OS are pulled from,
  # so changing it will NOT upgrade your system - see https://nixos.org/manual/nixos/stable/#sec-upgrading for how
  # to actually do that.
  #
  # This value being lower than the current NixOS release does NOT mean your system is
  # out of date, out of support, or vulnerable.
  #
  # Do NOT change this value unless you have manually inspected all the changes it would make to your configuration,
  # and migrated your data accordingly.
  #
  # For more information, see `man configuration.nix` or https://nixos.org/manual/nixos/stable/options#opt-system.stateVersion .
  system.stateVersion = "24.05"; # Did you read the comment?

}

