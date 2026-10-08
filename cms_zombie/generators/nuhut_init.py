import subprocess
from pathlib import Path

class NuhutInitializer:
    """Invokes the Nuhut installer to initialize SDLC quality gates on the newly migrated project."""

    @classmethod
    def initialize_nuhut(cls, target_dir: Path, nuhut_kit_path: Path = None) -> bool:
        target_dir = Path(target_dir).resolve()
        if nuhut_kit_path is None:
            # Default to standard sibling or local kit path
            possible_path = Path("/Users/reza/Projects/ai-sdlc-template")
            if possible_path.exists():
                nuhut_kit_path = possible_path

        if not nuhut_kit_path or not (nuhut_kit_path / "install.sh").exists():
            return False

        install_script = (nuhut_kit_path / "install.sh").resolve()
        # Run non-interactive or default installation
        try:
            # Running install.py directly with target
            res = subprocess.run(
                ["python3", str(nuhut_kit_path / "install.py"), str(target_dir)],
                input=b"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",
                capture_output=True,
                timeout=30
            )
            return res.returncode == 0
        except Exception:
            return False
