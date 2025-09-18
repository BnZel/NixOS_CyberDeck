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

  networking.hostName = "nixexp"; # Define your hostname.
  # Pick only one of the below networking options.
  #networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.
  networking.networkmanager.enable = true;  # Easiest to use and most distros use this by default.

  #networking.wireless.allowAuxiliaryImperativeNetworks = true;

  #networking.wireless.userControlled.enable = true;

  # Set your time zone.
  time.timeZone = "America/Toronto";

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  nix.settings.experimental-features = [ "nix-command" "flakes" ];

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
  # services.pulseaudio.enable = true;
  # OR
  # services.pipewire = {
  #   enable = true;
  #   pulse.enable = true;
  # };

 services.cockpit = {
    enable = true;
    port = 9090;
    settings = {
      WebService = {
        AllowUnencrypted = true;
      };
    };
  };

  # Enable touchpad support (enabled default in most desktopManager).
  # services.libinput.enable = true;

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.jay = {
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" ]; # Enable ‘sudo’ for the user.
    shell = pkgs.zsh;
    packages = with pkgs; [];
  };

  programs = {
     zsh = {
        autosuggestions.enable = true;
        zsh-autoenv.enable = true;
	syntaxHighlighting.enable = true;
	shellAliases = {
	    la = "ls -la";
	    c = "clear";
	    h = "history -p";
	    s = "sudo shutdown now";
	    e = "exit";
	    rebuild = "sudo nixos-rebuild switch && sudo nix-env --list-generations --profile /nix/var/nix/profiles/system";
	    del_gen = "sudo nix-env --profile /nix/var/nix/profiles/system --delete-generations";
	    clt_garbage = "sudo nix-collect-garbage -d && sudo fstrim -av";
	    switch_config = "sudo /run/current-system/bin/switch-to-configuration boot";
	    gens = "sudo nix-env --list-generations --profile /nix/var/nix/profiles/system";
            config = "sudo nano /etc/nixos/configuration.nix";
	    hw_config = "sudo nano /etc/nixos/hardware-configuration";
	    trim = "sudo fstrim -av";
	};
	ohMyZsh = {
	    enable = true;
	    theme = "jonathan";
	    plugins = [
	      "git"
	    ];
        };
     };
  };

  environment.etc."modprobe.d/iwlwifi.conf".text = ''
    options ilwifi 11n_disable=1
    options iwlwifi power_save=0
  '';

  # programs.firefox.enable = true;

  # List packages installed in system profile.
  # You can use https://search.nixos.org/ to find more packages (and options).
  environment.systemPackages = with pkgs; [
  #  vim # Do not forget to add an editor to edit configuration.nix! The Nano editor is also installed by default.
    wget
    htop
    cockpit
    zsh
    oh-my-zsh
    fastfetch
    linux-firmware
    tmux
    busybox
    libusb1
    docker
    git
    nmap
    duckdb
#   tailscale
  ];

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  programs.zsh.enable = true;

  # List services that you want to enable:

  # Enable Docker 
  virtualisation.docker.enable = true; 

  # Enable Tailscale
  # services.tailscale.enable = true; 

  # Enable the OpenSSH daemon.
  services.openssh.enable = true;

  services.openssh.settings = {
   PasswordAuthentication = true;
  };

  # Open ports in the firewall.
  networking.firewall.allowedTCPPorts = [ 9090 443 80 22 4000 8888 ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

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
  system.stateVersion = "25.05"; # Did you read the comment?

}

