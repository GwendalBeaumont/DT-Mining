let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  nativeBuildInputs = with pkgs.buildPackages; [
    vscode.fhs
    ollama
  ];
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.pandas
      python-pkgs.requests
      python-pkgs.types-requests
      python-pkgs.matplotlib
      python-pkgs.seaborn
      python-pkgs.tqdm
      python-pkgs.ipykernel
      python-pkgs.pip
      python-pkgs.ollama
    ]))
  ];

  shellHook = ''
    ollama pull deepseek-r1:8b
    code .
  '';
}
