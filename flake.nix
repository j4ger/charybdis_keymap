{
  description = "Dev shell for the QMK charybdis keymap visualizer";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAll = f: nixpkgs.lib.genAttrs systems (sys: f nixpkgs.legacyPackages.${sys});
    in {
      devShells = forAll (pkgs: {
        default = pkgs.mkShell { packages = [ pkgs.python3 ]; };
      });
    };
}
