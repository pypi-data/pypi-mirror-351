{
  description = "Claude SDK - Typed Python wrapper for Claude Code CLI";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Python with uv
        python = pkgs.python311;

        # Development tools
        devTools = with pkgs; [
          # Python and package management
          python
          uv

          # Development tools
          git
          pre-commit

          # Additional utilities
          just  # command runner
          tree
          fd
          ripgrep
        ];

        # Python packages for development
        pythonEnv = python.withPackages (ps: with ps; [
          # Core dependencies
          pydantic

          # Development dependencies
          pytest
          pytest-cov
          hypothesis

          # Type checking and linting handled by uv
        ]);

      in {
        # Development shell
        devShells.default = pkgs.mkShell {
          buildInputs = devTools ++ [ pythonEnv ];

          shellHook = ''
            echo "🐍 Claude SDK Development Environment"
            echo "Python: $(python --version)"
            echo "uv: $(uv --version)"
            echo ""
            echo "Getting started:"
            echo "  uv sync --dev          # Install dependencies"
            echo "  just check             # Run all checks"
            echo "  just test              # Run tests"
            echo "  just fmt               # Format code"
            echo ""

            # Set up environment
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            export UV_PYTHON=${python}/bin/python

            # Create .venv if it doesn't exist
            if [ ! -d ".venv" ]; then
              echo "Creating virtual environment..."
              uv venv --python ${python}/bin/python
            fi

            # Activate virtual environment
            source .venv/bin/activate

            # Install dependencies if needed
            if [ ! -f ".venv/pyvenv.cfg" ] || [ ! -f "uv.lock" ]; then
              echo "Installing dependencies..."
              uv sync --dev
            fi

            # Install pre-commit hooks if not already installed
            if [ ! -f ".git/hooks/pre-commit" ]; then
              echo "Installing pre-commit hooks..."
              pre-commit install
            fi
          '';
        };

        # Package build
        packages.default = python.pkgs.buildPythonPackage {
          pname = "claude-sdk";
          version = "0.1.0";

          src = ./.;

          build-system = with python.pkgs; [
            hatchling
          ];

          dependencies = with python.pkgs; [
            pydantic
          ];

          optional-dependencies = {
            dev = with python.pkgs; [
              pytest
              pytest-cov
              hypothesis
            ];
          };

          pythonImportsCheck = [ "claude_sdk" ];

          meta = with pkgs.lib; {
            description = "Typed Python wrapper for Claude Code CLI";
            homepage = "https://github.com/darinkishore/claude-sdk";
            license = licenses.mit;
            maintainers = [ ];
          };
        };
      });
}
